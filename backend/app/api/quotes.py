from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.quote import QuoteCreate, QuoteListResponse, QuotePublic, QuoteUpdate
from app.services.quote_service import (
    create_quote,
    get_quote,
    list_quotes,
    set_status,
    update_quote,
)


class StatusChange(BaseModel):
    status: Literal["SENT", "APPROVED", "REJECTED", "EXPIRED"]


router = APIRouter(prefix="/sales/quotes", tags=["sales-quotes"])


@router.get("", response_model=QuoteListResponse)
def list_quotes_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_quotes(db, page, page_size, search, status, partner_id)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{quote_id}", response_model=QuotePublic)
def get_quote_endpoint(
    quote_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quote = get_quote(db, quote_id)
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return quote


@router.post("", response_model=QuotePublic, status_code=status.HTTP_201_CREATED)
def create_quote_endpoint(
    data: QuoteCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    quote = create_quote(db, data)
    return quote


@router.put("/{quote_id}", response_model=QuotePublic)
def update_quote_endpoint(
    quote_id: UUID,
    data: QuoteUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        quote = update_quote(db, quote_id, data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="immutable_state")
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return quote


@router.post("/{quote_id}/status", response_model=QuotePublic)
def change_status_endpoint(
    quote_id: UUID,
    body: StatusChange,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        quote = set_status(db, quote_id, body.status)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="invalid_status")
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return quote
