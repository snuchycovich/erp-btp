"""Use case for retrieving a quote by ID."""

from uuid import UUID

from app.domain.models import Quote
from app.domain.repository.quote_repository import QuoteRepository


class GetQuoteByIdUseCase:
    """Retrieve a quote by its ID."""

    def __init__(self, repository: QuoteRepository) -> None:
        """Initialize the use case with its quote repository."""
        self._repository = repository

    def execute(self, quote_id: UUID) -> Quote | None:
        """Return the matching quote, or None if it does not exist."""
        return self._repository.get_by_id(quote_id)
