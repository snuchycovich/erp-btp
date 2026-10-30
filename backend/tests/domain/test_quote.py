from datetime import datetime
from decimal import Decimal
from typing import cast
from uuid import UUID

import pytest

from app.domain.models.quote import Quote
from app.domain.models.quote_item import QuoteItem
from app.domain.models.quote_revision import QuoteRevision, calculate_quote_total
from app.domain.models.quote_revision_status import QuoteRevisionStatus


def test_quote_create() -> None:
    """A quote keeps stable identity and exposes its initial revision."""
    items = (
        QuoteItem(
            description="Prestation 1",
            quantity=Decimal(10),
            unit_price=Decimal("45.50"),
        ),
        QuoteItem(
            description="Prestation 2",
            quantity=Decimal(5),
            unit_price=Decimal("15.90"),
        ),
    )

    revision = QuoteRevision(
        version=1,
        status=QuoteRevisionStatus.PENDING_APPOVAL,
        items=items,
        total_ht=calculate_quote_total(items),
    )
    quote = Quote(
        id=UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        created_at=datetime.now(),
        revisions=(revision,),
    )

    assert quote.id == UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837")
    assert quote.current_revision == revision
    assert quote.current_revision.total_ht == Decimal("534.50")
    assert quote.status == QuoteRevisionStatus.PENDING_APPOVAL


@pytest.mark.parametrize("version", [0, -1])
def test_quote_revision_rejects_non_positive_version(version: int) -> None:
    """A quote revision number must be a positive integer."""
    with pytest.raises(ValueError, match="version must be strictly positive"):
        QuoteRevision(
            version=version,
            status=QuoteRevisionStatus.DRAFT,
            items=(),
            total_ht=Decimal(0),
            created_at=datetime.now(),
        )


@pytest.mark.parametrize("status", [None, "invalid"])
def test_quote_revision_rejects_invalid_status(status: object) -> None:
    with pytest.raises(TypeError, match="status must be a QuoteRevisionStatus"):
        QuoteRevision(
            version=1,
            status=cast(QuoteRevisionStatus, status),
            items=(),
            total_ht=Decimal(0),
            created_at=datetime.now(),
        )


@pytest.mark.parametrize("total_ht", [Decimal(-1), Decimal("NaN"), Decimal("Infinity")])
def test_quote_revision_rejects_invalid_total(total_ht: Decimal) -> None:
    """A quote revision total must be finite and non-negative."""
    with pytest.raises(ValueError, match="total_ht must be non-negative"):
        QuoteRevision(
            version=1,
            status=QuoteRevisionStatus.DRAFT,
            items=(),
            total_ht=total_ht,
            created_at=datetime.now(),
        )


def test_quote_revision_total_must_be_sum_of_items() -> None:
    """A quote revision rejects a stored total that differs from its item sum."""
    items = (
        QuoteItem(
            description="Prestation",
            quantity=Decimal(2),
            unit_price=Decimal("10.00"),
        ),
    )

    with pytest.raises(ValueError, match="total_ht must equal the sum of items"):
        QuoteRevision(
            version=1,
            status=QuoteRevisionStatus.DRAFT,
            items=items,
            total_ht=Decimal("19.99"),
            created_at=datetime.now(),
        )


def test_revising_items_appends_revision_and_recalculates_total() -> None:
    """Changing an item appends a revision and preserves the previous revision."""
    items = (
        QuoteItem(
            description="Prestation",
            quantity=Decimal(2),
            unit_price=Decimal("10.00"),
        ),
    )
    initial_revision = QuoteRevision(
        version=1,
        status=QuoteRevisionStatus.DRAFT,
        items=items,
        total_ht=Decimal("20.00"),
        created_at=datetime.now(),
    )
    quote = Quote(
        id=UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        created_at=datetime.now(),
        revisions=(initial_revision,),
    )

    updated_items = [
        QuoteItem(
            description="Prestation",
            quantity=Decimal(2),
            unit_price=Decimal("15.00"),
        )
    ]
    updated_quote = quote.revise_items(updated_items)

    assert updated_quote.id == quote.id
    assert updated_quote.created_at == quote.created_at
    assert [revision.version for revision in updated_quote.revisions] == [1, 2]
    assert updated_quote.current_revision.items[0].unit_price == Decimal("15.00")
    assert updated_quote.current_revision.total_ht == Decimal("30.00")
    assert updated_quote.revisions[0] == initial_revision
    assert updated_quote.revisions[0].items[0].unit_price == Decimal("10.00")
    assert updated_quote.revisions[0].total_ht == Decimal("20.00")
    assert quote.revisions == (initial_revision,)


def test_revising_items_to_empty_list_creates_zero_total_revision() -> None:
    """Removing every item appends a revision with a zero total."""
    initial_items = (
        QuoteItem(
            description="Prestation",
            quantity=Decimal(2),
            unit_price=Decimal("10.00"),
        ),
    )
    initial_revision = QuoteRevision(
        version=1,
        status=QuoteRevisionStatus.DRAFT,
        items=initial_items,
        total_ht=Decimal("20.00"),
    )
    quote = Quote(
        id=UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        created_at=datetime.now(),
        revisions=(initial_revision,),
    )

    revised_quote = quote.revise_items([])

    assert [revision.version for revision in revised_quote.revisions] == [1, 2]
    assert revised_quote.current_revision.items == ()
    assert revised_quote.current_revision.total_ht == Decimal(0)
    assert quote.revisions == (initial_revision,)


def test_quote_accepts_zero_total_and_lock_version() -> None:
    """A zero total and zero lock version are valid boundaries."""
    quote = Quote(
        id=UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        created_at=datetime.now(),
        revisions=(
            QuoteRevision(
                version=1,
                status=QuoteRevisionStatus.DRAFT,
                items=(),
                total_ht=Decimal(0),
            ),
        ),
    )

    assert quote.current_revision.total_ht == Decimal(0)


@pytest.mark.parametrize("attribute", ["id", "created_at", "revisions"])
def test_quote_rejects_missing_required_attributes(attribute: str) -> None:
    """Required quote identity and history fields cannot be None."""
    quote_attributes: dict[str, object] = {
        "id": UUID("7f77ddc9-abd7-4306-9d8b-f720937ae837"),
        "created_at": datetime.now(),
        "revisions": (
            QuoteRevision(
                version=1,
                status=QuoteRevisionStatus.DRAFT,
                items=(),
                total_ht=Decimal(0),
            ),
        ),
    }
    quote_attributes[attribute] = None

    with pytest.raises(ValueError, match=f"{attribute} cannot be empty"):
        Quote(**quote_attributes)  # type: ignore[arg-type]
