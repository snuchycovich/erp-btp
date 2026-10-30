"""Shared factories for constructing test domain objects."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.models import (
    Quote,
    QuoteItem,
    QuoteRevision,
    QuoteRevisionStatus,
)


def create_test_quote() -> Quote:
    """Return a complete quote aggregate suitable for persistence tests."""
    created_at = datetime.now(UTC)
    items = (
        QuoteItem(
            description="Tile installation",
            quantity=Decimal(10),
            unit_price=Decimal("45.00"),
        ),
        QuoteItem(
            description="Paint work",
            quantity=Decimal(2),
            unit_price=Decimal("100.00"),
        ),
    )
    return Quote(
        id=uuid4(),
        created_at=created_at,
        revisions=(
            QuoteRevision(
                version=1,
                status=QuoteRevisionStatus.DRAFT,
                items=items,
                total_ht=Decimal("650.00"),
                created_at=created_at,
                version_lock=1,
            ),
        ),
    )
