"""Integration tests for the quote creation API."""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import QuoteItemModel


def test_create_quote_returns_201(client: TestClient) -> None:
    """Create a draft quote and return its initial revision summary."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "Tile installation",
                    "quantity": "10",
                    "unit_price": "45.00",
                },
                {
                    "description": "Paint work",
                    "quantity": "2",
                    "unit_price": "100.00",
                },
            ]
        },
    )

    assert response.status_code == 201
    body = response.json()
    UUID(body["id"])
    assert body["revision"] == 1
    assert body["status"] == "draft"
    assert body["total_ht"] == "650.00"


def test_create_quote_accepts_zero_as_price(client: TestClient) -> None:
    """Accept a zero unit price and create a quote with a zero total."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "Complimentary service",
                    "quantity": "10",
                    "unit_price": "0",
                }
            ]
        },
    )

    assert response.status_code == 201
    assert response.json()["total_ht"] == "0"


def test_create_quote_persists_normalized_description(
    client: TestClient, database_engine: Engine
) -> None:
    """Persist only normalized plain text from an HTML-like description."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": (
                        " <p onclick='alert(1)'>Pose&nbsp;de</p> "
                        "<script>alert(1)</script><strong>carrelage</strong> "
                    ),
                    "quantity": "1",
                    "unit_price": "45.50",
                }
            ]
        },
    )

    assert response.status_code == 201
    with Session(database_engine) as session:
        description = session.scalar(select(QuoteItemModel.description))
    assert description == "Pose de carrelage"


@pytest.mark.parametrize("field", ["description", "quantity", "unit_price"])
def test_create_quote_rejects_missing_item_field(
    client: TestClient, field: str
) -> None:
    """Reject quote items that omit a required field."""
    item: dict[str, object] = {
        "description": "Carrelage",
        "quantity": "5",
        "unit_price": "45.50",
    }
    item.pop(field)

    response = client.post("/quotes", json={"items": [item]})

    assert response.status_code == 422
    assert any(
        error["type"] == "missing" and error["loc"] == ["body", "items", 0, field]
        for error in response.json()["detail"]
    )


@pytest.mark.parametrize(
    ("field", "expected_type"),
    [
        ("description", "string_type"),
        ("quantity", "decimal_type"),
        ("unit_price", "decimal_type"),
    ],
)
def test_create_quote_rejects_null_item_field(
    client: TestClient, field: str, expected_type: str
) -> None:
    """Reject null values for required quote item fields."""
    item: dict[str, object] = {
        "description": "Carrelage",
        "quantity": "5",
        "unit_price": "45.50",
    }
    item[field] = None

    response = client.post("/quotes", json={"items": [item]})

    assert response.status_code == 422
    assert any(
        error["type"] == expected_type and error["loc"] == ["body", "items", 0, field]
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
def test_create_quote_rejects_invalid_quantity(
    client: TestClient,
    quantity: str,
    expected_type: str,
    expected_message: str,
) -> None:
    """Reject items with non-positive, non-finite, or non-numeric quantities."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "Carrelage",
                    "quantity": quantity,
                    "unit_price": "45.50",
                }
            ]
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "items", 0, "quantity"]
    assert error["msg"] == expected_message


@pytest.mark.parametrize(
    ("description", "expected_type", "expected_message"),
    [
        ("", "string_too_short", "String should have at least 1 character"),
        ("  ", "value_error", "Value error, description cannot be empty"),
        (None, "string_type", "Input should be a valid string"),
    ],
)
def test_create_quote_rejects_blank_description(
    client: TestClient,
    description: str | None,
    expected_type: str,
    expected_message: str,
) -> None:
    """Reject items with empty, whitespace-only, or null descriptions."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": description,
                    "quantity": "5",
                    "unit_price": "45.50",
                }
            ]
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "items", 0, "description"]
    assert error["msg"] == expected_message


def test_create_quote_rejects_description_empty_after_normalization(
    client: TestClient,
) -> None:
    """Reject a description whose dangerous content is removed entirely."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "<script>alert(1)</script><style>p{}</style>",
                    "quantity": "1",
                    "unit_price": "45.50",
                }
            ]
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "value_error"
    assert error["loc"] == ["body", "items", 0, "description"]
    assert error["msg"] == "Value error, description cannot be empty"


@pytest.mark.parametrize(
    ("unit_price", "expected_type", "expected_message"),
    [
        ("-1", "greater_than_equal", "Input should be greater than or equal to 0"),
        ("NaN", "finite_number", "Input should be a finite number"),
        ("Infinity", "finite_number", "Input should be a finite number"),
        ("-Infinity", "finite_number", "Input should be a finite number"),
    ],
)
def test_create_quote_rejects_invalid_unit_price(
    client: TestClient,
    unit_price: str,
    expected_type: str,
    expected_message: str,
) -> None:
    """Reject items with negative or non-finite unit prices."""
    response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "Carrelage",
                    "quantity": "1",
                    "unit_price": unit_price,
                }
            ]
        },
    )

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == expected_type
    assert error["loc"] == ["body", "items", 0, "unit_price"]
    assert error["msg"] == expected_message


def test_create_quote_rejects_empty_items(client: TestClient) -> None:
    """Reject a quote that does not contain any items."""
    response = client.post("/quotes", json={"items": []})

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == "too_short"
    assert error["loc"] == ["body", "items"]
