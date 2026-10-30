"""Tests for the in-memory quote repository implementation."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.models.quote import Quote
from app.domain.models.quote_revision import QuoteRevision
from app.domain.models.quote_revision_status import QuoteRevisionStatus
from app.infrastructure.persistence.repositories.in_memory_quote_repository import (
    InMemoryQuoteRepository,
)


def test_in_memory_quote_repository_crud() -> None:
    """InMemoryQuoteRepository must implement the Quote CRUD contract."""
    quote = Quote(
        id=UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        created_at=datetime.now(),
        revisions=(
            QuoteRevision(
                version=1,
                status=QuoteRevisionStatus.DRAFT,
                items=(),
                total_ht=Decimal(0),
            ),
        ),
    )

    repository = InMemoryQuoteRepository()

    assert repository.get_by_id(quote.id) is None
    assert repository.list_all() == []

    assert repository.add(quote) == quote
    assert repository.get_by_id(quote.id) == quote
    assert repository.list_all() == [quote]

    assert repository.delete(quote.id) is True
    assert repository.get_by_id(quote.id) is None
