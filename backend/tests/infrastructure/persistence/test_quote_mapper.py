"""Tests for mappings between quote domain objects and ORM models."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.models import (
    Quote,
    QuoteItem,
    QuoteRevision,
    QuoteRevisionStatus,
)
from app.infrastructure.persistence.mapper.quote_mapper import QuoteMapper
from app.infrastructure.persistence.models import (
    QuoteItemModel,
    QuoteModel,
    QuoteRevisionModel,
)
from tests.utils import create_test_quote


def test_quote_mapper_to_model() -> None:
    """Map a complete domain quote to its ORM object graph."""
    created_at = datetime.now(UTC)
    quote_id = uuid4()
    items = (
        QuoteItem(
            description="Tile installation",
            quantity=Decimal(10),
            unit_price=Decimal("45.00"),
        ),
        QuoteItem(
            description="Paint work",
            quantity=Decimal(2),
            unit_price=Decimal("100.00"),
        ),
    )
    quote = Quote(
        id=quote_id,
        created_at=created_at,
        revisions=(
            QuoteRevision(
                version=1,
                status=QuoteRevisionStatus.DRAFT,
                items=items,
                total_ht=Decimal("650.00"),
                created_at=created_at,
                version_lock=1,
            ),
        ),
    )

    model = QuoteMapper.to_model(quote)

    assert isinstance(model, QuoteModel)
    assert model.id == quote_id
    assert model.created_at == created_at
    assert len(model.revisions) == 1

    revision_model = model.revisions[0]
    assert isinstance(revision_model, QuoteRevisionModel)
    assert revision_model.version == 1
    assert revision_model.status is QuoteRevisionStatus.DRAFT
    assert revision_model.total_ht == Decimal("650.00")
    assert revision_model.created_at == created_at
    assert revision_model.version_lock == 1
    assert len(revision_model.items) == 2
    assert all(isinstance(item, QuoteItemModel) for item in revision_model.items)
    assert [
        (item.description, item.quantity, item.unit_price)
        for item in revision_model.items
    ] == [
        ("Tile installation", Decimal(10), Decimal("45.00")),
        ("Paint work", Decimal(2), Decimal("100.00")),
    ]


def test_quote_mapper_to_domain() -> None:
    """Map a complete ORM object graph to an immutable domain quote."""
    created_at = datetime.now(UTC)
    quote_id = uuid4()
    model = QuoteModel(
        id=quote_id,
        created_at=created_at,
        revisions=[
            QuoteRevisionModel(
                version=1,
                status="draft",
                total_ht=Decimal("650.00"),
                created_at=created_at,
                version_lock=1,
                items=[
                    QuoteItemModel(
                        description="Tile installation",
                        quantity=Decimal(10),
                        unit_price=Decimal("45.00"),
                    ),
                    QuoteItemModel(
                        description="Paint work",
                        quantity=Decimal(2),
                        unit_price=Decimal("100.00"),
                    ),
                ],
            )
        ],
    )

    quote = QuoteMapper.to_domain(model)

    assert isinstance(quote, Quote)
    assert quote.id == quote_id
    assert quote.created_at == created_at
    assert len(quote.revisions) == 1

    revision = quote.revisions[0]
    assert revision.version == 1
    assert revision.status is QuoteRevisionStatus.DRAFT
    assert revision.total_ht == Decimal("650.00")
    assert revision.created_at == created_at
    assert revision.version_lock == 1
    assert len(revision.items) == 2
    assert [
        (item.description, item.quantity, item.unit_price) for item in revision.items
    ] == [
        ("Tile installation", Decimal(10), Decimal("45.00")),
        ("Paint work", Decimal(2), Decimal("100.00")),
    ]


def test_quote_mapper_round_trip() -> None:
    """Preserve a quote through a domain-to-model-to-domain round trip."""
    original = create_test_quote()

    model = QuoteMapper.to_model(original)
    restored = QuoteMapper.to_domain(model)

    assert restored == original
