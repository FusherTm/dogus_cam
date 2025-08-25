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


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    __table_args__ = (
        Index("ix_sales_orders_partner", "partner_id"),
        Index("ix_sales_orders_created", text("created_at_utc DESC")),
        CheckConstraint(
            "status IN ('NEW','CONFIRMED','FULFILLED','CANCELLED')",
            name="chk_sales_order_status",
        ),
        CheckConstraint(
            "discount_rate >= 0 AND discount_rate <= 100",
            name="chk_sales_order_discount_rate",
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
    currency = Column(Text, nullable=False, server_default=text("'TRY'"))
    status = Column(Text, nullable=False, server_default=text("'NEW'"))
    order_date = Column(Date, nullable=False, server_default=func.current_date())
    notes = Column(Text, nullable=True)
    discount_rate = Column(Numeric(5, 2), nullable=False, server_default=text("0.00"))
    subtotal = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    tax_total = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    grand_total = Column(Numeric(14, 2), nullable=False, server_default=text("0.00"))
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    items = relationship(
        "SalesOrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    __table_args__ = (
        Index("ix_sales_order_items_order", "order_id"),
        CheckConstraint("quantity > 0", name="chk_sales_order_item_quantity_positive"),
        CheckConstraint(
            "unit_price >= 0", name="chk_sales_order_item_unit_price_nonneg"
        ),
        CheckConstraint(
            "line_discount_rate >= 0 AND line_discount_rate <= 100",
            name="chk_sales_order_item_discount_rate",
        ),
        CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="chk_sales_order_item_tax_rate",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False
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

    order = relationship("SalesOrder", back_populates="items")
