"""FastAPI dependencies for database sessions and application use cases."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases import CreateQuoteUseCase, ListQuotesUseCase
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.repositories.sqlalchemy_quote_repository import (
    SQLAlchemyQuoteRepository,
)


def get_session() -> Generator[Session, None, None]:
    """Yield one database session for the duration of a request."""
    with SessionLocal() as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]


def get_create_quote_use_case(
    session: DbSession,
) -> CreateQuoteUseCase:
    """Build the quote creation use case with a SQLAlchemy repository."""
    repository = SQLAlchemyQuoteRepository(session)
    return CreateQuoteUseCase(repository)


def get_list_quotes_use_case(
    session: DbSession,
) -> ListQuotesUseCase:
    """Build the quote fetch use case with SQLAlchemy repository."""
    repository = SQLAlchemyQuoteRepository(session)
    return ListQuotesUseCase(repository)
