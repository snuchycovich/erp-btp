"""Tests for the quote creation application use case."""

from decimal import Decimal
from uuid import UUID

from app.application.use_cases.create_quote import CreateQuoteUseCase
from app.domain.models import QuoteItem, QuoteRevisionStatus
from app.infrastructure.persistence.repositories.in_memory_quote_repository import (
    InMemoryQuoteRepository,
)


def _create_items() -> tuple[QuoteItem, ...]:
    return (
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


def test_execute_creates_initial_draft_revision() -> None:
    """Create a quote with one immutable draft revision and its calculated total."""
    repository = InMemoryQuoteRepository()
    use_case = CreateQuoteUseCase(repository)
    items = _create_items()

    quote = use_case.execute(items)

    assert isinstance(quote.id, UUID)
    assert isinstance(quote.revisions, tuple)
    assert len(quote.revisions) == 1

    revision = quote.current_revision
    assert quote.revisions == (revision,)
    assert revision.version == 1
    assert revision.status is QuoteRevisionStatus.DRAFT
    assert revision.version_lock == 1
    assert isinstance(revision.items, tuple)
    assert revision.items == items
    assert revision.total_ht == Decimal("650.00")


def test_execute_persists_created_quote() -> None:
    """Store the created quote in the repository under its generated identifier."""
    repository = InMemoryQuoteRepository()
    use_case = CreateQuoteUseCase(repository)

    quote = use_case.execute(_create_items())

    assert repository.get_by_id(quote.id) == quote
    assert repository.list_all() == [quote]
