from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.application.validations import (
    validate_non_negative_integer,
    validate_positive_decimal,
    validate_positive_integer,
    validate_required,
)
from app.domain.model.quote_item import QuoteItem, calculate_item_total


def calculate_quote_total(items: Iterable[QuoteItem]) -> Decimal:
    """Return the sum of all item amounts in a quote."""
    return sum(
        (calculate_item_total(item) for item in items),
        Decimal(0),
    )


@dataclass(frozen=True)
class QuoteRevision:
    version: int
    items: list[QuoteItem]
    total_ht: Decimal
    created_at: datetime = field(default_factory=datetime.now)
    version_lock: int | None = None

    def __post_init__(self) -> None:
        """Validate quote revision attributes after initialization."""
        validate_positive_integer("version", self.version)
        validate_required("items", self.items)
        validate_positive_decimal("total_ht", self.total_ht, allow_zero=True)
        validate_required("created_at", self.created_at)

        if self.version_lock is not None:
            validate_non_negative_integer("version_lock", self.version_lock)

        expected_total = calculate_quote_total(self.items)
        if self.total_ht != expected_total:
            raise ValueError(
                "total_ht must equal the sum of items, "
                f"given value {self.total_ht}; expected {expected_total}"
            )
