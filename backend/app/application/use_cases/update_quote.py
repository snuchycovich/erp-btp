from uuid import UUID

from app.domain.models import Quote, QuoteItem
from app.domain.repository.quote_repository import QuoteRepository


class UpdateQuoteUseCase:
    """Replace a quote's items by appending a new revision."""

    def __init__(self, repository: QuoteRepository) -> None:
        """Initialize the use case with its quote repository."""
        self._repository = repository

    def execute(
        self,
        quote_id: UUID,
        items: tuple[QuoteItem, ...],
    ) -> Quote | None:
        """Append a revision with the supplied items, or return None if absent."""
        quote = self._repository.get_by_id(quote_id)
        if quote is None:
            return None

        updated_quote = quote.revise_items(list(items))

        # revise_items returns the same object when the items are unchanged.
        if updated_quote is quote:
            return quote

        return self._repository.update(updated_quote)
