from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.ar import ARAllocation, AREntry
from app.models.sales_invoice import SalesInvoice


def _allocated_amount(db: Session, invoice_id: UUID) -> Decimal:
    total = (
        db.query(
            func.coalesce(
                func.sum(
                    case(
                        (AREntry.type.in_(["PAYMENT", "ADJUSTMENT"]), ARAllocation.amount),
                        (AREntry.type == "REFUND", -ARAllocation.amount),
                        else_=0,
                    )
                ),
                0,
            )
        )
        .select_from(ARAllocation)
        .join(AREntry)
        .filter(ARAllocation.invoice_id == invoice_id)
        .scalar()
    )
    return Decimal(total)


def on_invoice_issued(db: Session, invoice: SalesInvoice) -> AREntry:
    existing = (
        db.query(AREntry)
        .filter(AREntry.invoice_id == invoice.id, AREntry.type == "INVOICE")
        .first()
    )
    if existing:
        return existing
    entry = AREntry(
        partner_id=invoice.partner_id,
        invoice_id=invoice.id,
        entry_date=invoice.issue_date or date.today(),
        type="INVOICE",
        amount=invoice.grand_total,
        currency=invoice.currency,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def post_payment(
    db: Session,
    partner_id: UUID,
    amount: Decimal,
    currency: str = "TRY",
    note: str | None = None,
    allocations: list[dict] | None = None,
) -> tuple[AREntry, list[dict], Decimal]:
    if amount <= 0:
        raise ValueError("amount_nonpositive")
    entry = AREntry(
        partner_id=partner_id,
        type="PAYMENT",
        amount=amount,
        currency=currency,
        note=note,
    )
    db.add(entry)
    db.flush()
    remaining_payment = amount
    applied: list[dict] = []
    if allocations:
        total_alloc = sum((a["amount"] for a in allocations), Decimal("0"))
        if total_alloc > amount:
            raise ValueError("overallocation")
        for alloc in allocations:
            invoice = db.get(SalesInvoice, alloc["invoice_id"])
            if not invoice or invoice.partner_id != partner_id or invoice.status in {"CANCELLED", "PAID"}:
                raise ValueError("invalid_invoice_for_allocation")
            remaining = invoice.grand_total - _allocated_amount(db, invoice.id)
            if alloc["amount"] > remaining:
                raise ValueError("overallocation")
            db.add(
                ARAllocation(
                    entry_id=entry.id,
                    invoice_id=invoice.id,
                    amount=alloc["amount"],
                )
            )
            remaining_payment -= alloc["amount"]
            remaining_after = remaining - alloc["amount"]
            applied.append(
                {
                    "invoice_id": invoice.id,
                    "amount": alloc["amount"],
                    "remaining_after": remaining_after,
                }
            )
    else:
        invoices: Sequence[SalesInvoice] = (
            db.query(SalesInvoice)
            .filter(
                SalesInvoice.partner_id == partner_id,
                SalesInvoice.status != "CANCELLED",
            )
            .order_by(SalesInvoice.issue_date, SalesInvoice.created_at_utc)
            .all()
        )
        for invoice in invoices:
            remaining = invoice.grand_total - _allocated_amount(db, invoice.id)
            if remaining <= 0:
                continue
            alloc_amt = remaining if remaining < remaining_payment else remaining_payment
            if alloc_amt <= 0:
                break
            db.add(
                ARAllocation(entry_id=entry.id, invoice_id=invoice.id, amount=alloc_amt)
            )
            remaining_payment -= alloc_amt
            remaining_after = remaining - alloc_amt
            applied.append(
                {
                    "invoice_id": invoice.id,
                    "amount": alloc_amt,
                    "remaining_after": remaining_after,
                }
            )
            if remaining_payment <= 0:
                break
    db.commit()
    db.refresh(entry)
    return entry, applied, remaining_payment


def compute_partner_balance(db: Session, partner_id: UUID) -> dict:
    invoices: Sequence[SalesInvoice] = (
        db.query(SalesInvoice).filter(SalesInvoice.partner_id == partner_id).all()
    )
    by_invoice: list[dict] = []
    total_due = Decimal("0")
    for inv in invoices:
        allocated = _allocated_amount(db, inv.id)
        remaining = inv.grand_total - allocated
        by_invoice.append(
            {
                "invoice_id": inv.id,
                "status": inv.status,
                "issued_total": inv.grand_total,
                "allocated": allocated,
                "remaining": remaining,
            }
        )
        if inv.status != "CANCELLED":
            total_due += remaining
    return {"currency": "TRY", "total_due": total_due, "by_invoice": by_invoice}


def list_ar_entries(
    db: Session,
    partner_id: UUID,
    page: int,
    page_size: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[Sequence[AREntry], int]:
    query = db.query(AREntry).filter(AREntry.partner_id == partner_id)
    if date_from:
        query = query.filter(AREntry.entry_date >= date_from)
    if date_to:
        query = query.filter(AREntry.entry_date <= date_to)
    total = query.count()
    items = (
        query.order_by(AREntry.entry_date.desc(), AREntry.created_at_utc.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
