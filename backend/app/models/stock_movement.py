from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        Index("ix_stock_movements_prod", "product_id"),
        Index("ix_stock_movements_wh", "warehouse_id"),
        Index("ix_stock_movements_created", text("created_at_utc DESC")),
        CheckConstraint("direction IN ('IN','OUT')", name="chk_direction"),
        CheckConstraint("quantity > 0", name="chk_quantity_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    direction = Column(Text, nullable=False)
    quantity = Column(Numeric(14, 3), nullable=False)
    reason = Column(Text, nullable=True)
    document_no = Column(Text, nullable=True)
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
