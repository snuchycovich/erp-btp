from typing import Protocol
from uuid import UUID

from app.domain.model.quote import Quote
from app.domain.repository.crud_repository import CrudRepository


class QuoteRepository(CrudRepository[Quote, UUID], Protocol):
    pass
