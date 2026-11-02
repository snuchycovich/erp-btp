"""HTTP routes for quote management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.use_cases import (
    CreateQuoteUseCase,
    ListQuotesUseCase,
)
from app.domain.models.quote_item import QuoteItem
from app.presentation.api.dependencies import (
    get_create_quote_use_case,
    get_list_quotes_use_case,
    get_session,
)
from app.presentation.api.schemas.quote import (
    QuoteCreateRequest,
    QuoteCreateResponse,
    QuoteListResponse,
)

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.get(
    "",
    response_model=list[QuoteListResponse],
    status_code=200,
)
def list_quotes(
    use_case: Annotated[
        ListQuotesUseCase,
        Depends(get_list_quotes_use_case),
    ],
    session: Annotated[Session, Depends(get_session)],
) -> list[QuoteListResponse]:
    quotes = use_case.execute()

    return [
        QuoteListResponse(
            id=quote.id,
            status=quote.status.value,
            total_ht=quote.current_revision.total_ht,
        )
        for quote in quotes
    ]


@router.post(
    "",
    response_model=QuoteCreateResponse,
    status_code=201,
)
def create_quote(
    request: QuoteCreateRequest,
    use_case: Annotated[
        CreateQuoteUseCase,
        Depends(get_create_quote_use_case),
    ],
    session: Annotated[Session, Depends(get_session)],
):
    """Create and persist a quote with its initial draft revision."""
    try:
        items = tuple(
            QuoteItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in request.items
        )

        quote = use_case.execute(items)

        session.commit()

    except ValueError as exc:
        session.rollback()
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except Exception:
        session.rollback()
        raise

    revision = quote.revisions[0]

    return QuoteCreateResponse(
        id=quote.id,
        revision=revision.version,
        status=revision.status.value,
        total_ht=revision.total_ht,
    )
