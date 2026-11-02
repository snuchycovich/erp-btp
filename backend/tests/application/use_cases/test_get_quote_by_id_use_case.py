"""Tests for retrieving a quote by ID."""

from uuid import uuid4

from app.application.use_cases.get_quote_by_id import GetQuoteByIdUseCase
from app.infrastructure.persistence.repositories.in_memory_quote_repository import (
    InMemoryQuoteRepository,
)
from tests.utils import create_test_quote


def test_execute_returns_quote_when_it_exists() -> None:
    """Return the matching quote from the repository."""
    repository = InMemoryQuoteRepository()
    quote = create_test_quote()
    repository.add(quote)
    use_case = GetQuoteByIdUseCase(repository)

    result = use_case.execute(quote.id)

    assert result == quote


def test_execute_returns_none_when_quote_does_not_exist() -> None:
    """Return None when the repository has no quote with the requested ID."""
    repository = InMemoryQuoteRepository()
    use_case = GetQuoteByIdUseCase(repository)

    result = use_case.execute(uuid4())

    assert result is None
