"""Pydantic request and response schemas for the API."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.domain.models import QuoteRevisionStatus
from app.presentation.api.text_normalization import normalize_plain_text


class QuoteItemRequest(BaseModel):
    """Input data for one item in a quote."""

    description: str = Field(min_length=1)
    quantity: Decimal = Field(gt=0, allow_inf_nan=False)
    unit_price: Decimal = Field(ge=0, allow_inf_nan=False)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        """Normalize HTML-like input and reject descriptions left empty."""
        normalized_value = normalize_plain_text(value)
        if not normalized_value:
            raise ValueError("description cannot be empty")
        return normalized_value

    @field_validator("unit_price")
    @classmethod
    def unit_price_must_be_finite_and_non_negative(cls, value: Decimal) -> Decimal:
        """Reject non-finite or negative unit prices."""
        if not value.is_finite() or value < 0:
            raise ValueError("unit_price must be finite and non-negative")
        return value


class QuoteCreateRequest(BaseModel):
    """Request payload for creating a quote with at least one item."""

    items: list[QuoteItemRequest] = Field(min_length=1)


class QuoteCreateResponse(BaseModel):
    """Summary returned after a quote is created successfully."""

    id: UUID
    revision: int
    status: str
    total_ht: Decimal


class QuoteListResponse(BaseModel):
    """Summary returned list quotes"""

    id: UUID
    status: str
    total_ht: Decimal


class QuoteItemResponse(BaseModel):
    """One line item in a quote revision."""

    description: str
    quantity: Decimal
    unit_price: Decimal


class QuoteRevisionResponse(BaseModel):
    """A quote revision and its line items."""

    version: int
    status: QuoteRevisionStatus
    total_ht: Decimal
    created_at: datetime
    items: list[QuoteItemResponse]


class QuoteDetailResponse(BaseModel):
    """Full quote details, including its revision history."""

    id: UUID
    created_at: datetime
    revisions: list[QuoteRevisionResponse]


class QuoteUpdateRequest(BaseModel):
    """Replacement items for a quote revision."""

    items: list[QuoteItemRequest] = Field(min_length=1)


class QuoteUpdateResponse(BaseModel):
    """Summary returned after a quote is updated."""

    id: UUID
    revision: int
    status: str
    total_ht: Decimal
