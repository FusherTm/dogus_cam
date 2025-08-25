from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class AREntry(Base):
    __tablename__ = "ar_entries"
    __table_args__ = (
        Index("ix_ar_entries_partner", "partner_id"),
        Index("ix_ar_entries_date", "entry_date", text("created_at_utc DESC")),
        CheckConstraint(
            "type IN ('INVOICE','PAYMENT','REFUND','ADJUSTMENT')",
            name="chk_ar_entry_type",
        ),
        CheckConstraint("amount >= 0", name="chk_ar_entry_amount_nonneg"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("sales_invoices.id", ondelete="SET NULL"), nullable=True)
    entry_date = Column(Date, nullable=False, server_default=func.current_date())
    type = Column(Text, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(Text, nullable=False, server_default=text("'TRY'"))
    note = Column(Text, nullable=True)
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    allocations = relationship(
        "ARAllocation",
        back_populates="entry",
        cascade="all, delete-orphan",
    )


class ARAllocation(Base):
    __tablename__ = "ar_allocations"
    __table_args__ = (
        Index("ix_ar_allocations_invoice", "invoice_id"),
        CheckConstraint("amount > 0", name="chk_ar_allocation_amount_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    entry_id = Column(UUID(as_uuid=True), ForeignKey("ar_entries.id", ondelete="CASCADE"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)

    entry = relationship("AREntry", back_populates="allocations")
