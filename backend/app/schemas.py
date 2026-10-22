from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class QuoteItemRequest(BaseModel):
    """Input data required to calculate a quote item's pre-tax total."""

    description: str = Field(min_length=1)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be empty")
        return value

    @field_validator("unit_price")
    @classmethod
    def unit_price_must_be_finite_and_non_negative(cls, value: Decimal) -> Decimal:
        if not value.is_finite() or value < 0:
            raise ValueError("unit_price must be finite and non-negative")
        return value


class QuoteItemResponse(BaseModel):
    """Response containing the calculated pre-tax total."""

    total_ht: Decimal = Field(ge=0)
