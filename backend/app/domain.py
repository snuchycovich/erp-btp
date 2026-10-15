from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True)
class QuoteItem:
    description: str
    quantity: Decimal
    unit_price: Decimal

    def __post_init__(self) -> None:
        self._check_non_negative("quantity", self.quantity)
        self._check_not_empty("quantity", self.quantity)
        self._check_non_negative("unit_price", self.unit_price)

    @staticmethod
    def _check_non_negative(name: str, value: Decimal) -> None:
        if value < 0:
            raise ValueError(f"{name} must be positive, given value {value}")

    @staticmethod
    def _check_not_empty(name: str, value: Decimal) -> None:
        if value == 0:
            raise ValueError(f"{name} can not be empty, given value {value}")


def calculate_item_total(item: QuoteItem) -> Decimal:
    return item.quantity * item.unit_price


def calculate_quote_total(items: tuple[QuoteItem, ...]) -> Decimal:
    return sum(
        (calculate_item_total(item) for item in items),
        Decimal(0),
    )


def calculate_tax(total_ht: Decimal, tax_rate: Decimal) -> Decimal:
    _validate_tax_rate(tax_rate)
    tax = total_ht * tax_rate / Decimal(100)
    return tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validate_tax_rate(value: Decimal) -> None:
    if not value.is_finite() or not Decimal(0) <= value <= Decimal(100):
        raise ValueError(f"Invalid tax rate: {value}")
