"""Integration tests for the quote item calculation API."""

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
