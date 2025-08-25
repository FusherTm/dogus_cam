from sqlalchemy import Column, DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
