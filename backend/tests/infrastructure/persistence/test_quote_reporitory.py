from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.pool import StaticPool

from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.models import (
    QuoteItemModel,
    QuoteModel,
    QuoteRevisionModel,
)


def test_save_quote_with_revision_and_items() -> None:
    # Arrange: isolated in-memory database
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    quote_id = uuid4()

    try:
        # Act: save quote with its revision and items
        with Session(engine) as session:
            quote = QuoteModel(
                id=quote_id,
                created_at=datetime.now(UTC),
                revisions=[
                    QuoteRevisionModel(
                        version=1,
                        status="draft",
                        total_ht=Decimal("650.00"),
                        created_at=datetime.now(UTC),
                        version_lock=1,
                        items=[
                            QuoteItemModel(
                                description="Carrelage",
                                quantity=Decimal(10),
                                unit_price=Decimal("45.00"),
                            ),
                            QuoteItemModel(
                                description="Peinture",
                                quantity=Decimal(2),
                                unit_price=Decimal("100.00"),
                            ),
                        ],
                    ),
                ],
            )

            session.add(quote)
            session.commit()

        # Assert: reload from a different session
        with Session(engine) as session:
            statement = (
                select(QuoteModel)
                .where(QuoteModel.id == quote_id)
                .options(
                    selectinload(QuoteModel.revisions).selectinload(
                        QuoteRevisionModel.items
                    )
                )
            )

            saved_quote = session.scalar(statement)

            assert saved_quote is not None
            assert saved_quote.id == quote_id
            assert len(saved_quote.revisions) == 1

            revision = saved_quote.revisions[0]

            assert revision.version == 1
            assert revision.status == "draft"
            assert revision.total_ht == Decimal("650.00")
            assert revision.version_lock == 1

            assert len(revision.items) == 2

            items_by_description = {item.description: item for item in revision.items}

            assert items_by_description["Carrelage"].quantity == Decimal(10)
            assert items_by_description["Carrelage"].unit_price == Decimal("45.00")
            assert items_by_description["Peinture"].unit_price == Decimal("100.00")

    finally:
        engine.dispose()
