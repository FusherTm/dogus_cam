from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Index,
    Numeric,
    Text,
    func,
    text,
    Computed,
)
from sqlalchemy.dialects.postgresql import CITEXT, UUID

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (Index("ix_employees_created", text("created_at_utc DESC")),)

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    code = Column(Text, nullable=False, unique=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    full_name = Column(Text, Computed("first_name || ' ' || last_name", persisted=True))
    email = Column(CITEXT(), nullable=True, unique=True)
    phone = Column(Text, nullable=True)
    department = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    annual_leave_days_per_year = Column(
        Numeric(5, 2), nullable=False, server_default=text("14.00")
    )
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
