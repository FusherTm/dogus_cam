from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    sku = Column(Text, nullable=False, unique=True)
    price = Column(Numeric(12, 2), nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    restock_level = Column(Numeric(14, 3), nullable=False, server_default=text("0"))
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
