from app.infrastructure.persistence.repositories.in_memory_quote_repository import (
    InMemoryQuoteRepository,
)

"""Tests for the quote listing application use case."""

from app.application.use_cases.list_quotes import ListQuotesUseCase
from tests.utils import create_test_quote


def test_execute_returns_empty_list_when_no_quotes_exist() -> None:
    """Return an empty list when the repository contains no quotes."""
    repository = InMemoryQuoteRepository()
    use_case = ListQuotesUseCase(repository)

    quotes = use_case.execute()

    assert quotes == []


def test_execute_returns_all_quotes_from_repository() -> None:
    """Return every quote stored in the repository."""
    repository = InMemoryQuoteRepository()
    first_quote = create_test_quote()
    second_quote = create_test_quote()
    repository.add(first_quote)
    repository.add(second_quote)
    use_case = ListQuotesUseCase(repository)

    quotes = use_case.execute()

    assert quotes == [first_quote, second_quote]
