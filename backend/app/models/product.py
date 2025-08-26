from sqlalchemy import Column, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    name = Column(Text, nullable=False)
    sku = Column(Text, nullable=False, unique=True)
    category_id = Column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    base_price_sqm = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
