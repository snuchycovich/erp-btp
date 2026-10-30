from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.application.validations import (
    validate_required,
)
from app.domain.model.quote_item import QuoteItem
from app.domain.model.quote_revision import QuoteRevision, calculate_quote_total
from app.domain.model.quote_revision_status import QuoteRevisionStatus


@dataclass(frozen=True)
class Quote:
    id: UUID
    revisions: list[QuoteRevision]
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate quote attributes after initialization."""
        validate_required("id", self.id)
        validate_required("revisions", self.revisions)
        validate_required("created_at", self.created_at)
        if not self.revisions:
            raise ValueError("revisions cannot be empty")

    @property
    def current_revision(self) -> QuoteRevision:
        """Return the latest quote revision."""
        return max(
            self.revisions,
            key=lambda revision: revision.version,
        )

    @property
    def status(self) -> QuoteRevisionStatus:
        return self.current_revision.status

    def revise_items(self, new_items: list[QuoteItem]) -> "Quote":
        """Return a new quote with a revision containing the supplied items."""
        current_revision = self.current_revision
        updated_items = list(new_items)

        if updated_items == current_revision.items:
            return self

        new_revision = QuoteRevision(
            version=current_revision.version + 1,
            status=current_revision.status,
            items=updated_items,
            total_ht=calculate_quote_total(updated_items),
        )

        return Quote(
            id=self.id,
            revisions=[*self.revisions, new_revision],
            created_at=self.created_at,
        )
