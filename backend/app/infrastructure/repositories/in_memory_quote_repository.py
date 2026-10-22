from uuid import UUID

from app.domain.model.quote import Quote
from app.domain.repository.quote_repository import QuoteRepository


class InMemoryQuoteRepository(QuoteRepository):
    def __init__(self) -> None:
        self._quotes: dict[UUID, Quote] = {}

    def get_by_id(self, entity_id: UUID) -> Quote | None:
        return self._quotes.get(entity_id)

    def list_all(self) -> list[Quote]:
        return list(self._quotes.values())

    def add(self, entity: Quote) -> Quote:
        self._quotes[entity.id] = entity
        return entity

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._quotes:
            del self._quotes[entity_id]
            return True
        return False
