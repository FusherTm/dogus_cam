from sqlalchemy import Boolean, Column, DateTime, Numeric, Text, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    sku = Column(Text, nullable=False, unique=True)
    price = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
