from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin, get_current_user, get_db, get_pagination
from app.models.user import User
from app.schemas.ar import (
    AREntryListResponse,
    PartnerBalance,
    PaymentCreate,
    PaymentResult,
)
from app.services.ar_service import (
    compute_partner_balance,
    list_ar_entries,
    post_payment,
)

router = APIRouter(prefix="/finance/ar", tags=["finance-ar"])


@router.get("/balances/{partner_id}", response_model=PartnerBalance)
def get_balance(
    partner_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compute_partner_balance(db, partner_id)


@router.get("/entries", response_model=AREntryListResponse)
def list_entries(
    partner_id: UUID,
    pagination: tuple[int, int] = Depends(get_pagination),
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_ar_entries(db, partner_id, page, page_size, date_from, date_to)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/payments", response_model=PaymentResult, status_code=status.HTTP_201_CREATED)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    allocations = None
    if data.allocations is not None:
        allocations = [a.model_dump() for a in data.allocations]
    try:
        entry, applied, unapplied = post_payment(
            db,
            data.partner_id,
            data.amount,
            data.currency,
            data.note,
            allocations,
        )
    except ValueError as e:
        detail = str(e)
        if detail in {"overallocation", "invalid_invoice_for_allocation"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        raise
    return {"entry_id": entry.id, "applied": applied, "unapplied_amount": unapplied}
