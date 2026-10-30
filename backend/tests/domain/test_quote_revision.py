"""Tests for immutable quote revision status transitions."""

import pytest

from app.domain.models.quote_revision import QuoteRevision
from app.domain.models.quote_revision_status import QuoteRevisionStatus


def test_new_revision_is_draft() -> None:
    """Assign draft status to a newly created revision by default."""
    revision = QuoteRevision(version=1, items=())

    assert revision.status == QuoteRevisionStatus.DRAFT


def test_quote_can_be_summited() -> None:
    """Allow a draft revision to be submitted for approval."""
    revision = QuoteRevision(version=1, items=())
    updated_revision = revision.change_status(QuoteRevisionStatus.PENDING_APPOVAL)

    assert updated_revision.status == QuoteRevisionStatus.PENDING_APPOVAL


@pytest.mark.parametrize(
    "new_status",
    [
        QuoteRevisionStatus.ACCEPTED,
        QuoteRevisionStatus.REJECTED,
        QuoteRevisionStatus.DRAFT,
    ],
)
def test_quote_can_be_accepted_or_rejected_form_summited(
    new_status: QuoteRevisionStatus,
) -> None:
    """Allow a submitted revision to reach an authorized next status."""
    revision = QuoteRevision(
        version=1, items=(), status=QuoteRevisionStatus.PENDING_APPOVAL
    )
    updated_revision = revision.change_status(new_status)

    assert updated_revision.status == new_status


def test_draft_cannot_be_accetped_directly() -> None:
    """Prevent a draft revision from being accepted directly."""
    revision = QuoteRevision(version=1, items=())

    with pytest.raises(ValueError):
        revision.change_status(QuoteRevisionStatus.ACCEPTED)

    assert revision.status == QuoteRevisionStatus.DRAFT


@pytest.mark.parametrize(
    "status, new_status",
    [
        (QuoteRevisionStatus.ACCEPTED, QuoteRevisionStatus.DRAFT),
        (QuoteRevisionStatus.ACCEPTED, QuoteRevisionStatus.PENDING_APPOVAL),
        (QuoteRevisionStatus.ACCEPTED, QuoteRevisionStatus.REJECTED),
        (QuoteRevisionStatus.REJECTED, QuoteRevisionStatus.DRAFT),
        (QuoteRevisionStatus.REJECTED, QuoteRevisionStatus.PENDING_APPOVAL),
        (QuoteRevisionStatus.REJECTED, QuoteRevisionStatus.ACCEPTED),
    ],
)
def test_accepted_or_rejected_cannot_transitioned(
    status: QuoteRevisionStatus, new_status: QuoteRevisionStatus
) -> None:
    """Prevent terminal revisions from transitioning to another status."""
    revision = QuoteRevision(version=1, items=(), status=status)

    with pytest.raises(ValueError):
        revision.change_status(new_status)

    assert revision.status == status


@pytest.mark.parametrize(
    "status, new_status",
    [
        (QuoteRevisionStatus.DRAFT, QuoteRevisionStatus.DRAFT),
        (QuoteRevisionStatus.PENDING_APPOVAL, QuoteRevisionStatus.PENDING_APPOVAL),
        (QuoteRevisionStatus.ACCEPTED, QuoteRevisionStatus.ACCEPTED),
        (QuoteRevisionStatus.REJECTED, QuoteRevisionStatus.REJECTED),
    ],
)
def test_rejected_same_transition(
    status: QuoteRevisionStatus, new_status: QuoteRevisionStatus
) -> None:
    """Reject transitions that retain the revision's current status."""
    revision = QuoteRevision(version=1, items=(), status=status)

    with pytest.raises(ValueError):
        revision.change_status(new_status)

    assert revision.status == status
