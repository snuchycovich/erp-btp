"""In-memory repository for quote entities."""

from uuid import UUID

from app.domain.models.quote import Quote
from app.domain.repository.quote_repository import QuoteRepository


class InMemoryQuoteRepository(QuoteRepository):
    """Implement repository operations using a local dictionary."""

    def __init__(self) -> None:
        """Initialize an empty store indexed by quote ID."""
        self._quotes: dict[UUID, Quote] = {}

    def get_by_id(self, entity_id: UUID) -> Quote | None:
        """Return the quote with this ID, if it exists."""
        return self._quotes.get(entity_id)

    def list_all(self) -> list[Quote]:
        """Return all currently stored quotes."""
        return list(self._quotes.values())

    def add(self, entity: Quote) -> Quote:
        """Store the quote by ID and return the entity."""
        self._quotes[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> bool:
        """Delete the quote if present and report whether it was removed."""
        if entity_id in self._quotes:
            del self._quotes[entity_id]
            return True
        return False
