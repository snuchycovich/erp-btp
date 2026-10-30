"""Domain entity for quote revisions and their validated totals."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast

from app.application.validations import (
    validate_non_negative_integer,
    validate_positive_decimal,
    validate_positive_integer,
    validate_required,
)
from app.domain.models.quote_item import QuoteItem, calculate_item_total
from app.domain.models.quote_revision_status import QuoteRevisionStatus


def calculate_quote_total(items: Iterable[QuoteItem]) -> Decimal:
    """Return the sum of all item amounts in a quote."""
    return sum(
        (calculate_item_total(item) for item in items),
        Decimal(0),
    )


@dataclass(frozen=True)
class QuoteRevision:
    """Represent an immutable quote revision with its items and lifecycle status."""

    version: int
    items: tuple[QuoteItem, ...]
    total_ht: Decimal = Decimal(0)
    status: QuoteRevisionStatus = QuoteRevisionStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version_lock: int | None = None

    def __post_init__(self) -> None:
        """Validate quote revision attributes after initialization."""
        validate_positive_integer("version", self.version)
        if not isinstance(cast(object, self.status), QuoteRevisionStatus):
            raise TypeError("status must be a QuoteRevisionStatus")
        validate_required("items", self.items)
        object.__setattr__(self, "items", tuple(self.items))
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

    def change_status(self, new_status: QuoteRevisionStatus) -> QuoteRevision:
        """Return a copy with the new status if the transition is allowed."""
        if not self._can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")

        return cast(QuoteRevision, replace(self, status=new_status))

    def _can_transition_to(self, new_status: QuoteRevisionStatus) -> bool:
        """Check whether the revision lifecycle permits the requested transition."""
        allowed: dict[QuoteRevisionStatus, set[QuoteRevisionStatus]] = {
            QuoteRevisionStatus.DRAFT: {QuoteRevisionStatus.PENDING_APPOVAL},
            QuoteRevisionStatus.PENDING_APPOVAL: {
                QuoteRevisionStatus.DRAFT,
                QuoteRevisionStatus.ACCEPTED,
                QuoteRevisionStatus.REJECTED,
            },
            QuoteRevisionStatus.ACCEPTED: set(),
            QuoteRevisionStatus.REJECTED: set(),
        }

        return new_status in allowed[self.status]
