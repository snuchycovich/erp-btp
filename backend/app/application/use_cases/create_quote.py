"""Application use case for creating and persisting quotes."""

from uuid import uuid4

from app.domain.models import (
    Quote,
    QuoteItem,
    QuoteRevision,
    QuoteRevisionStatus,
)
from app.domain.models.quote_revision import calculate_quote_total
from app.domain.repository.quote_repository import QuoteRepository


class CreateQuoteUseCase:
    """Create a quote with its initial immutable draft revision."""

    def __init__(self, repository: QuoteRepository) -> None:
        """Initialize the use case with its quote repository."""
        self._repository = repository

    def execute(self, items: tuple[QuoteItem, ...]) -> Quote:
        """Create and persist a quote containing the supplied items."""
        total_ht = calculate_quote_total(items)

        revision = QuoteRevision(
            version=1,
            status=QuoteRevisionStatus.DRAFT,
            items=items,
            total_ht=total_ht,
            version_lock=1,
        )

        quote = Quote(id=uuid4(), revisions=(revision,))

        return self._repository.add(quote)
