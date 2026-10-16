from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


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
        _validate_not_empty("description", self.description)
        _validate_positive("quantity", self.quantity)
        _validate_positive("unit_price", self.unit_price, allow_zero=True)


# TODO: Define whether monetary amounts are rounded per item, on the quote total, or only for tax.
def calculate_item_total(item: QuoteItem) -> Decimal:
    """Return the amount for one item before tax."""
    return item.quantity * item.unit_price


def calculate_quote_total(items: Iterable[QuoteItem, ...]) -> Decimal:
    """Return the sum of all item amounts in a quote."""
    return sum(
        (calculate_item_total(item) for item in items),
        Decimal(0),
    )


def calculate_tax(total_ht: Decimal, tax_rate: Decimal) -> Decimal:
    """Calculate tax for a non-negative total and a finite rate from 0 to 100, rounded to two decimals."""
    _validate_positive("total_ht", total_ht, allow_zero=True)
    _validate_tax_rate(tax_rate)
    tax = total_ht * tax_rate / Decimal(100)
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validate_not_empty(name: str, value: str) -> None:
    """Reject None, empty strings, and strings containing only whitespace."""
    if value is None or not value.strip():
        raise ValueError(f"{name} cannot be empty, given value {value}")


def _validate_positive(name: str, value: Decimal, allow_zero: bool = False) -> None:
    """Reject non-finite and negative values, and reject zero unless explicitly allowed."""
    if not value.is_finite() or value < 0 or (not allow_zero and value == 0):
        constraint = "non-negative" if allow_zero else "strictly positive"
        raise ValueError(f"{name} must be {constraint}, given value {value}")


def _validate_tax_rate(value: Decimal) -> None:
    """Ensure a finite tax rate is between zero and one hundred inclusive."""
    if not value.is_finite() or not Decimal(0) <= value <= Decimal(100):
        raise ValueError(f"Invalid tax rate: {value}")
