"""FastAPI application exposing quote item calculations."""

from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel

from app.domain import QuoteItem, calculate_item_total

app = FastAPI(title="BTP Project Manager")


class QuoteItemRequest(BaseModel):
    """Input data required to calculate a quote item's pre-tax total."""

    description: str
    quantity: Decimal
    unit_price: Decimal


class QuoteItemResponse(BaseModel):
    """Response containing the calculated pre-tax total."""

    total_ht: Decimal


@app.post("/quote-items/calculate")
def calculate_item(
    request: QuoteItemRequest,
) -> QuoteItemResponse:
    """Calculate and return the pre-tax total for one quote item."""
    item = QuoteItem(
        description=request.description,
        quantity=request.quantity,
        unit_price=request.unit_price,
    )

    total = calculate_item_total(item)

    return QuoteItemResponse(total_ht=total)
