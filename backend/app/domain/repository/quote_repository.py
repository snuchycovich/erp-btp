"""Repository protocol for quote aggregates."""

from typing import Protocol
from uuid import UUID

from app.domain.models.quote import Quote
from app.domain.repository.crud_repository import CrudRepository


class QuoteRepository(CrudRepository[Quote, UUID], Protocol):
    """Define CRUD operations for quotes identified by UUID."""
