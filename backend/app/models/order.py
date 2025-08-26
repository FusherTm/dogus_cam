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


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_partner", "partner_id"),
        CheckConstraint(
            "status IN ('TEKLIF','SIPARIS','IPTAL')",
            name="chk_order_status",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    number = Column(Text, nullable=False, unique=True)
    partner_id = Column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )
    project_name = Column(Text, nullable=True)
    delivery_date = Column(Date, nullable=True)
    status = Column(Text, nullable=False, server_default=text("'TEKLIF'"))
    discount_rate = Column(Numeric(5, 2), nullable=False, server_default=text("0"))
    subtotal = Column(Numeric(14, 2), nullable=False, server_default=text("0"))
    tax_total = Column(Numeric(14, 2), nullable=False, server_default=text("0"))
    grand_total = Column(Numeric(14, 2), nullable=False, server_default=text("0"))
    notes = Column(Text, nullable=True)
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_order_item_quantity_positive"),
        CheckConstraint(
            "unit_price >= 0",
            name="chk_order_item_unit_price_nonneg",
        ),
        CheckConstraint(
            "line_discount_rate >= 0 AND line_discount_rate <= 100",
            name="chk_order_item_discount_rate",
        ),
        CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="chk_order_item_tax_rate",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    description = Column(Text, nullable=True)
    quantity = Column(Numeric(14, 3), nullable=False)
    unit_price = Column(Numeric(14, 2), nullable=False)
    line_discount_rate = Column(Numeric(5, 2), nullable=False, server_default=text("0"))
    tax_rate = Column(Numeric(5, 2), nullable=False, server_default=text("20"))
    line_subtotal = Column(Numeric(14, 2), nullable=False, server_default=text("0"))
    line_tax = Column(Numeric(14, 2), nullable=False, server_default=text("0"))
    line_total = Column(Numeric(14, 2), nullable=False, server_default=text("0"))

    order = relationship("Order", back_populates="items")
