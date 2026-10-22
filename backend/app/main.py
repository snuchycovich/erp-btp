"""FastAPI application exposing quote item calculations."""

from fastapi import FastAPI, HTTPException

from app.domain import QuoteItem, calculate_item_total
from app.schemas import QuoteItemRequest, QuoteItemResponse

app = FastAPI(title="BTP Project Manager")


@app.post("/quote-items/calculate")
def calculate_item(
    request: QuoteItemRequest,
) -> QuoteItemResponse:
    """Calculate and return the pre-tax total for one quote item."""
    try:
        item = QuoteItem(
            description=request.description,
            quantity=request.quantity,
            unit_price=request.unit_price,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    total = calculate_item_total(item)
    return QuoteItemResponse(total_ht=total)
