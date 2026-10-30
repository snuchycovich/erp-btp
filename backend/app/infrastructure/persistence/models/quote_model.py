"""ORM model for a quote and its revisions."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models.quote_revision_model import (
    QuoteRevisionModel,
)


class QuoteModel(Base):
    """Represent a persisted quote and its collection of revisions."""

    __tablename__ = "quotes"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    revisions: Mapped[list["QuoteRevisionModel"]] = relationship(
        back_populates="quote", cascade="all, delete-orphan"
    )
