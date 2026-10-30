"""Reserved for conversions between domain quotes and ORM models."""

from datetime import UTC, datetime

from app.domain.models import (
    Quote,
    QuoteItem,
    QuoteRevision,
    QuoteRevisionStatus,
)
from app.infrastructure.persistence.models import (
    QuoteItemModel,
    QuoteModel,
    QuoteRevisionModel,
)


class QuoteMapper:
    """Convert quote aggregates between domain objects and ORM models."""

    @staticmethod
    def _to_utc_datetime(value: datetime) -> datetime:
        """Normalize a naive or timezone-aware datetime to UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def to_model(quote: Quote) -> QuoteModel:
        """Build an ORM object graph from a domain quote."""
        return QuoteModel(
            id=quote.id,
            created_at=QuoteMapper._to_utc_datetime(quote.created_at),
            revisions=[
                QuoteRevisionModel(
                    version=revision.version,
                    status=revision.status,
                    total_ht=revision.total_ht,
                    created_at=QuoteMapper._to_utc_datetime(revision.created_at),
                    version_lock=revision.version_lock,
                    items=[
                        QuoteItemModel(
                            description=item.description,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                        )
                        for item in revision.items
                    ],
                )
                for revision in quote.revisions
            ],
        )

    @staticmethod
    def to_domain(model: QuoteModel) -> Quote:
        """Build a domain quote from a loaded ORM object graph."""
        return Quote(
            id=model.id,
            created_at=QuoteMapper._to_utc_datetime(model.created_at),
            revisions=tuple(
                QuoteRevision(
                    version=revision.version,
                    status=QuoteRevisionStatus(revision.status),
                    total_ht=revision.total_ht,
                    created_at=QuoteMapper._to_utc_datetime(revision.created_at),
                    version_lock=revision.version_lock,
                    items=tuple(
                        QuoteItem(
                            description=item.description,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                        )
                        for item in revision.items
                    ),
                )
                for revision in model.revisions
            ),
        )
