from enum import StrEnum


class QuoteRevisionStatus(StrEnum):
    """Lifecycle status assigned to a quote revision."""

    DRAFT = "draft"
    PENDING_APPOVAL = "pending_approval"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
