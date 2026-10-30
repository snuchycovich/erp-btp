"""ORM model for a quote revision and its line items."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models import QuoteRevisionStatus

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.quote_item_model import (
        QuoteItemModel,
    )
    from app.infrastructure.persistence.models.quote_model import QuoteModel
from app.infrastructure.persistence.database import Base


def _status_values(statuses: list[QuoteRevisionStatus]) -> list[str]:
    """Return the status values stored in the database."""
    return [status.value for status in statuses]


class QuoteRevisionModel(Base):
    """Persist a revision, its status and total, and its line items."""

    __tablename__ = "quote_revisions"

    __table_args__ = (UniqueConstraint("quote_id", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    quote_id: Mapped[UUID] = mapped_column(
        ForeignKey("quotes.id"),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(nullable=False)

    status: Mapped[QuoteRevisionStatus] = mapped_column(
        Enum(
            QuoteRevisionStatus,
            native_enum=False,
            values_callable=_status_values,
        ),
        nullable=False,
    )

    total_ht: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    version_lock: Mapped[int] = mapped_column(nullable=False, default=1)

    quote: Mapped["QuoteModel"] = relationship(back_populates="revisions")

    items: Mapped[list["QuoteItemModel"]] = relationship(
        back_populates="revision", cascade="all, delete-orphan", lazy="selectin"
    )

    __mapper_args__: dict[str, Any] = {"version_id_col": version_lock}  # noqa: RUF012
