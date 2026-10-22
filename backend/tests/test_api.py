"""Integration tests for the quote item calculation API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calculate_item_endpoint() -> None:
    """Return the calculated pre-tax total for a valid quote item request."""
    response = client.post(
        "/quote-items/calculate",
        json={
            "description": "Pose de carrlage",
            "quantity": "10",
            "unit_price": "45.50",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"total_ht": "455.00"}


def test_calculate_item_accept_zero_as_price() -> None:
    """Accept a zero unit price and return a zero pre-tax total."""
    response = client.post(
        "/quote-items/calculate",
        json={
            "description": "Pose de carrlage",
            "quantity": "10",
            "unit_price": "0",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"total_ht": "0"}


@pytest.mark.parametrize("field", ["description", "quantity", "unit_price"])
def test_calculate_item_rejects_missing_required_field(field: str) -> None:
    """Reject requests that omit any required quote-item field."""
    payload = {
        "description": "Carrelage",
        "quantity": "5",
        "unit_price": "45.50",
    }
    payload.pop(field)

    response = client.post("/quote-items/calculate", json=payload)

    assert response.status_code == 422
    assert any(
        error["type"] == "missing"
        and error["loc"] == ["body", field]
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize(
    ("field, expected_type"),
    [
        ("description", "string_type"),
        ("quantity", "decimal_type"),
        ("unit_price", "decimal_type"),
    ],
)
def test_calculate_item_rejects_null_required_field(
    field: str, expected_type: str
) -> None:
    """Reject null values for required quote-item fields."""
    payload = {
        "description": "Carrelage",
        "quantity": "5",
        "unit_price": "45.50",
    }
    payload[field] = None

    response = client.post("/quote-items/calculate", json=payload)

    assert response.status_code == 422
    assert any(
        error["type"] == expected_type
        and error["loc"] == ["body", field]
        for error in response.json()["detail"]
    )

    
@pytest.mark.parametrize(
    ("quantity", "expected_type", "expected_message"),
    [
        ("-5", "greater_than", "Input should be greater than 0"),
        ("0", "greater_than", "Input should be greater than 0"),
        ("NaN", "finite_number", "Input should be a finite number"),
        ("Infinity", "finite_number", "Input should be a finite number"),
        ("-Infinity", "finite_number", "Input should be a finite number"),
        ("not-a-number", "decimal_parsing", "Input should be a valid decimal"),
    ],
)
def test_calculate_item_rejects_invalid_quantity(
    quantity: str, expected_type: str, expected_message: str
) -> None:
    """Reject non-positive, non-finite, and non-numeric quantities."""
    response = client.post(
        "/quote-items/calculate",
        json={
            "description": "Carrelage",
            "quantity": quantity,
            "unit_price": "45.50",
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "quantity"]
    assert error["msg"] == expected_message


@pytest.mark.parametrize(
    ("description", "expected_type", "expected_message"),
    [
        ("", "string_too_short", "String should have at least 1 character"),
        ("  ", "value_error", "Value error, description cannot be empty"),
        (None, "string_type", "Input should be a valid string"),
    ],
)
def test_calculate_item_rejects_blank_description(
    description: str | None, 
    expected_type: str, 
    expected_message: str
) -> None:
    """Reject empty, whitespace-only, and null descriptions."""
    response = client.post(
        "/quote-items/calculate",
        json={
            "description": description,
            "quantity": "5",
            "unit_price": "45.50",
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "description"]
    assert error["msg"] == expected_message


@pytest.mark.parametrize(
    ("unit_price", "expected_type", "expected_message"),
    [
        ("-1", "greater_than_equal", "Input should be greater than or equal to 0"),
        ("NaN", "finite_number", "Input should be a finite number"),
        ("Infinity", "finite_number", "Input should be a finite number"),
        ("-Infinity", "finite_number", "Input should be a finite number"),
    ],
)
def test_calculate_item_rejects_invalid_unit_price(
    unit_price: str, expected_type: str, expected_message: str
) -> None:
    """Reject negative and non-finite unit prices."""
    response = client.post(
        "/quote-items/calculate",
        json={
            "description": "Carrelage",
            "quantity": "1",
            "unit_price": unit_price,
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "unit_price"]
    assert error["msg"] == expected_message
