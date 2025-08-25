from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
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


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT','SUBMITTED','APPROVED','REJECTED','CANCELLED')",
            name="ck_leave_requests_status",
        ),
        Index("ix_leave_requests_emp", "employee_id", "start_date", "end_date"),
        Index("ix_leave_requests_created", text("created_at_utc DESC")),
    )

    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    employee_id = Column(
        UUID(as_uuid=True), ForeignKey("employees.id", ondelete="RESTRICT"), nullable=False
    )
    type_id = Column(
        UUID(as_uuid=True), ForeignKey("leave_types.id", ondelete="RESTRICT"), nullable=False
    )
    status = Column(Text, nullable=False, server_default=text("'DRAFT'"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Numeric(6, 2), nullable=False, server_default=text("0.00"))
    reason = Column(Text, nullable=True)
    created_at_utc = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
