from fastapi.testclient import TestClient


def test_list_quotes_returns_empty_list(client: TestClient) -> None:
    """Return an empty list when no quotes exist."""
    response = client.get("/quotes")

    assert response.status_code == 200
    assert response.json() == []


def test_list_quotes_returns_existing_quotes(client: TestClient) -> None:
    """Return quote summaries for quotes already created through the API."""
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
    created_quote = create_response.json()

    response = client.get("/quotes")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": created_quote["id"],
            "status": "draft",
            "total_ht": "90.00",
        }
    ]
