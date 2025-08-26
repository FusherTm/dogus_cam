from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ProductionJob(Base):
    __tablename__ = "production_jobs"
    __table_args__ = (
        CheckConstraint("quantity_required > 0", name="chk_production_job_qty_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    order_item_id = Column(
        UUID(as_uuid=True), ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False
    )
    quantity_required = Column(Numeric(14, 3), nullable=False)
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    order_item = relationship("OrderItem", back_populates="jobs")
