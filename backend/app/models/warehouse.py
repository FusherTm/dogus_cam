from sqlalchemy import Boolean, Column, DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False, unique=True)
    code = Column(Text, nullable=True, unique=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
