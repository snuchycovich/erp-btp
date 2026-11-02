"""Integration tests for retrieving quote details."""

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient


def test_get_quote_returns_revisions_and_items(client: TestClient) -> None:
    """Return the quote details, including its revision and line items."""
    create_response = client.post(
        "/quotes",
        json={
            "items": [
                {
                    "description": "Tile installation",
                    "quantity": "2",
                    "unit_price": "45.00",
                }
            ]
        },
    )
    assert create_response.status_code == 201
    quote_id = create_response.json()["id"]

    response = client.get(f"/quotes/{quote_id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == quote_id
    UUID(body["id"])
    assert len(body["revisions"]) == 1

    revision = body["revisions"][0]
    assert revision["version"] == 1
    assert revision["status"] == "draft"
    assert revision["total_ht"] == "90.00"

    items = revision["items"]
    assert len(items) == 1

    item = items[0]
    assert item["description"] == "Tile installation"
    assert Decimal(item["quantity"]) == Decimal(2)
    assert Decimal(item["unit_price"]) == Decimal("45.00")


def test_get_quote_returns_404_when_quote_does_not_exist(
    client: TestClient,
) -> None:
    """Return 404 when no quote has the requested ID."""
    missing_quote_id = uuid4()

    response = client.get(f"/quotes/{missing_quote_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Quote not found"}
