"""ORM model for a line item belonging to a quote revision."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.models.quote_revision_model import (
        QuoteRevisionModel,
    )


class QuoteItemModel(Base):
    """Persist a line item's description, quantity, and unit price."""

    __tablename__ = "quote_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    quote_revision_id: Mapped[int] = mapped_column(
        ForeignKey("quote_revisions.id"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)

    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    revision: Mapped["QuoteRevisionModel"] = relationship(
        back_populates="items",
    )
