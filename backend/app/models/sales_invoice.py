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


class SalesInvoice(Base):
    __tablename__ = "sales_invoices"
    __table_args__ = (
        Index("ix_sales_invoices_partner", "partner_id"),
        Index("ix_sales_invoices_created", text("created_at_utc DESC")),
        CheckConstraint(
            "status IN ('DRAFT','ISSUED','PAID','CANCELLED')",
            name="chk_sales_invoice_status",
        ),
        CheckConstraint(
            "discount_rate >= 0 AND discount_rate <= 100",
            name="chk_sales_invoice_discount_rate",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    number = Column(Text, nullable=False, unique=True)
    partner_id = Column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="SET NULL"), nullable=True
    )
    currency = Column(Text, nullable=False, server_default=text("'TRY'"))
    status = Column(Text, nullable=False, server_default=text("'DRAFT'"))
    issue_date = Column(Date, nullable=False, server_default=func.current_date())
    notes = Column(Text, nullable=True)
    discount_rate = Column(Numeric(5, 2), nullable=False, server_default=text("0.00"))
    subtotal = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    tax_total = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    grand_total = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    items = relationship(
        "SalesInvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SalesInvoiceItem(Base):
    __tablename__ = "sales_invoice_items"
    __table_args__ = (
        Index("ix_sales_invoice_items_invoice", "invoice_id"),
        CheckConstraint("quantity > 0", name="chk_sales_invoice_item_quantity_positive"),
        CheckConstraint(
            "unit_price >= 0", name="chk_sales_invoice_item_unit_price_nonneg"
        ),
        CheckConstraint(
            "line_discount_rate >= 0 AND line_discount_rate <= 100",
            name="chk_sales_invoice_item_discount_rate",
        ),
        CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="chk_sales_invoice_item_tax_rate",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    invoice_id = Column(
        UUID(as_uuid=True), ForeignKey("sales_invoices.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    description = Column(Text, nullable=True)
    quantity = Column(Numeric(14, 3), nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    line_discount_rate = Column(Numeric(5, 2), nullable=False, server_default=text("0.00"))
    tax_rate = Column(Numeric(5, 2), nullable=False, server_default=text("20.00"))
    line_subtotal = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    line_tax = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    line_total = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))

    invoice = relationship("SalesInvoice", back_populates="items")
