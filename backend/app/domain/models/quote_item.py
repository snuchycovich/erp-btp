"""Domain value object and calculations for quote line items."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.application.validations import (
    validate_not_empty,
    validate_positive_decimal,
)


@dataclass(frozen=True)
class QuoteItem:
    """A line item in a quote.

    Attributes:
        description: Non-empty description of the work or product.
        quantity: Number of units; must be strictly positive.
        unit_price: Price per unit; must be non-negative.
    """

    description: str
    quantity: Decimal
    unit_price: Decimal

    def __post_init__(self) -> None:
        """Validate the description, quantity, and unit price after initialization."""
        validate_not_empty("description", self.description)
        validate_positive_decimal("quantity", self.quantity)
        validate_positive_decimal("unit_price", self.unit_price, allow_zero=True)


# TODO: Define whether monetary amounts are rounded per item, on the quote total, or only for tax.
def calculate_item_total(item: QuoteItem) -> Decimal:
    """Return the amount for one item before tax."""
    return item.quantity * item.unit_price


def calculate_tax(total_ht: Decimal, tax_rate: Decimal) -> Decimal:
    """Calculate tax for a non-negative total and a finite rate from 0 to 100, rounded to two decimals."""
    validate_positive_decimal("total_ht", total_ht, allow_zero=True)
    _validate_tax_rate(tax_rate)
    tax = total_ht * tax_rate / Decimal(100)
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validate_tax_rate(value: Decimal) -> None:
    """Ensure a finite tax rate is between zero and one hundred inclusive."""
    if not value.is_finite() or not Decimal(0) <= value <= Decimal(100):
        raise ValueError(f"Invalid tax rate: {value}")
