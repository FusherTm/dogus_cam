from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_admin,
    get_current_user,
    get_db,
    get_pagination,
)
from app.models.user import User
from app.schemas.sales_invoice import (
    SalesInvoiceCreate,
    SalesInvoiceListResponse,
    SalesInvoicePublic,
    SalesInvoiceUpdate,
)
from app.services.sales_invoice_service import (
    create_invoice,
    get_invoice,
    list_invoices,
    set_status,
    update_invoice,
)


class StatusChange(BaseModel):
    status: Literal["ISSUED", "PAID", "CANCELLED"]


router = APIRouter(prefix="/sales/invoices", tags=["sales-invoices"])


@router.get("", response_model=SalesInvoiceListResponse)
def list_invoices_endpoint(
    pagination: tuple[int, int] = Depends(get_pagination),
    search: str | None = None,
    status: str | None = None,
    partner_id: UUID | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    page, page_size = pagination
    items, total = list_invoices(db, page, page_size, search, status, partner_id)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{invoice_id}", response_model=SalesInvoicePublic)
def get_invoice_endpoint(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.post("", response_model=SalesInvoicePublic, status_code=status.HTTP_201_CREATED)
def create_invoice_endpoint(
    data: SalesInvoiceCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        invoice = create_invoice(db, data)
    except ValueError as e:
        detail = str(e)
        if detail == "partner_mismatch":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="partner_mismatch")
        if detail == "order_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="order_not_found")
        raise
    return invoice


@router.put("/{invoice_id}", response_model=SalesInvoicePublic)
def update_invoice_endpoint(
    invoice_id: UUID,
    data: SalesInvoiceUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        invoice = update_invoice(db, invoice_id, data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="immutable_state")
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.post("/{invoice_id}/status", response_model=SalesInvoicePublic)
def change_status_endpoint(
    invoice_id: UUID,
    body: StatusChange,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        invoice = set_status(db, invoice_id, body.status)
    except ValueError as e:
        detail = str(e)
        if detail in {"invalid_status", "unsettled_balance", "allocated_invoice"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
        raise
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice
