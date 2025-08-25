from sqlalchemy import Boolean, Column, DateTime, Text, func, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    is_annual = Column(Boolean, nullable=False, server_default=text("false"))
    requires_approval = Column(Boolean, nullable=False, server_default=text("true"))
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
