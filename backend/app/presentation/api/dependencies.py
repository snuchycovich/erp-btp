"""FastAPI dependencies for database sessions and application use cases."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases import (
    CreateQuoteUseCase,
    GetQuoteByIdUseCase,
    ListQuotesUseCase,
    UpdateQuoteUseCase,
)
from app.domain.repository.quote_repository import QuoteRepository
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.repositories.sqlalchemy_quote_repository import (
    SQLAlchemyQuoteRepository,
)


def get_session() -> Generator[Session, None, None]:
    """Yield one database session for the duration of a request."""
    with SessionLocal() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def get_quote_repository(session: DbSession) -> QuoteRepository:
    """Build the quote repository for the current request."""
    return SQLAlchemyQuoteRepository(session)


QuoteRepositoryDep = Annotated[
    QuoteRepository,
    Depends(get_quote_repository),
]


def get_create_quote_use_case(
    repository: QuoteRepositoryDep,
) -> CreateQuoteUseCase:
    """Build the quote creation use case."""
    return CreateQuoteUseCase(repository)


def get_list_quotes_use_case(
    repository: QuoteRepositoryDep,
) -> ListQuotesUseCase:
    """Build the quote listing use case."""
    return ListQuotesUseCase(repository)


def get_quote_detail_use_case(
    repository: QuoteRepositoryDep,
) -> GetQuoteByIdUseCase:
    """Build the quote detail use case."""
    return GetQuoteByIdUseCase(repository)


def get_update_quote_use_case(
    repository: QuoteRepositoryDep,
) -> UpdateQuoteUseCase:
    """Build the quote update use case."""
    return UpdateQuoteUseCase(repository)
