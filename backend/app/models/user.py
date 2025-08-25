from sqlalchemy import Boolean, Column, DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import CITEXT, UUID

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email = Column(CITEXT(), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text, nullable=True)
    role = Column(Text, nullable=False, server_default=text("'user'"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
