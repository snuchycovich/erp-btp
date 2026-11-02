from app.domain.models import Quote
from app.domain.repository.quote_repository import QuoteRepository


class ListQuotesUseCase:
    """List all existing quotes."""

    def __init__(self, repository: QuoteRepository) -> None:
        """Initialize the use case with its quote repository"""
        self.__repository = repository

    def execute(self) -> list[Quote]:
        """Get list of quotes"""
        return self.__repository.list_all()
