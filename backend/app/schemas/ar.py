from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class PaymentAllocationIn(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(..., gt=0)


class PaymentCreate(BaseModel):
    partner_id: UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = 'TRY'
    note: str | None = None
    allocations: list[PaymentAllocationIn] | None = None


class PaymentAllocationOut(BaseModel):
    invoice_id: UUID
    amount: Decimal
    remaining_after: Decimal


class PaymentResult(BaseModel):
    entry_id: UUID
    applied: list[PaymentAllocationOut]
    unapplied_amount: Decimal


class PartnerInvoiceBalance(BaseModel):
    invoice_id: UUID
    status: str
    issued_total: Decimal
    allocated: Decimal
    remaining: Decimal


class PartnerBalance(BaseModel):
    currency: str
    total_due: Decimal
    by_invoice: list[PartnerInvoiceBalance]


class AREntryPublic(BaseModel):
    id: UUID
    partner_id: UUID
    invoice_id: UUID | None = None
    entry_date: date
    type: str
    amount: Decimal
    currency: str
    note: str | None = None
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class AREntryListResponse(PageMeta):
    items: list[AREntryPublic]
