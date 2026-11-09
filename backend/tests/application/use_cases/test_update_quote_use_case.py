from decimal import Decimal

from app.application.use_cases import UpdateQuoteUseCase
from app.domain.models import QuoteItem
from app.infrastructure.persistence.repositories.in_memory_quote_repository import (
    InMemoryQuoteRepository,
)
from tests.utils import create_test_quote


def test_execute_appends_revision_and_persist_updated_quote() -> None:
    repository = InMemoryQuoteRepository()
    quote = create_test_quote()
    repository.add(quote)
    use_case = UpdateQuoteUseCase(repository)
    updated_items = (
        QuoteItem(
            description="Pose carrelage",
            quantity=Decimal(3),
            unit_price=Decimal("35.00"),
        ),
    )

    result = use_case.execute(quote.id, updated_items)

    assert result is not None
    assert result.id == quote.id
    assert [revision.version for revision in result.revisions] == [1, 2]
    assert result.revisions[0] == quote.revisions[0]
    assert result.current_revision.items == updated_items
    assert result.current_revision.total_ht == Decimal("105.00")
    assert repository.get_by_id(quote.id) == result
