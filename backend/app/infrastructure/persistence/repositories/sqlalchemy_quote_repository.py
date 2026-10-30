"""SQLAlchemy-backed repository for quote entities."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models.quote import Quote
from app.domain.repository.quote_repository import QuoteRepository
from app.infrastructure.persistence.mapper.quote_mapper import QuoteMapper
from app.infrastructure.persistence.models import QuoteModel, QuoteRevisionModel


class SQLAlchemyQuoteRepository(QuoteRepository):
    """Implement repository operations using ORM models."""

    def __init__(self, session: Session) -> None:
        """Bind the repository to the provided SQLAlchemy session."""
        self._session = session

    def add(self, entity: Quote) -> Quote:
        """Add the quote to the session, flush it, and return the entity."""
        model = QuoteMapper.to_model(entity)

        self._session.add(model)
        self._session.flush()

        return entity

    def get_by_id(self, entity_id: UUID) -> Quote | None:
        """Find a quote by UUID and load its revisions and line items."""
        statement = (
            select(QuoteModel)
            .where(QuoteModel.id == entity_id)
            .options(
                selectinload(QuoteModel.revisions).selectinload(
                    QuoteRevisionModel.items
                )
            )
        )

        model = self._session.scalar(statement)

        if model is None:
            return None
        else:
            return QuoteMapper.to_domain(model)

    def list_all(self) -> list[Quote]:
        """Return all quotes with their revisions and line items."""
        statement = select(QuoteModel).options(
            selectinload(QuoteModel.revisions).selectinload(QuoteRevisionModel.items)
        )

        models = self._session.scalars(statement).all()

        return [QuoteMapper.to_domain(model) for model in models]

    def delete(self, entity_id: UUID) -> bool:
        """Schedule the matching quote for deletion in the session."""
        model = self._session.get(QuoteModel, entity_id)

        return False if model is None else self._delete_model(model)

    def _delete_model(self, model: QuoteModel) -> bool:
        """Schedule an ORM quote for deletion and report success."""
        self._session.delete(model)
        return True
