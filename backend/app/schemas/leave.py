from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class LeaveTypeBase(BaseModel):
    code: str = Field(..., pattern=r"^[A-Za-z0-9_-]{2,20}$")
    name: str = Field(..., min_length=2, max_length=80)
    is_annual: bool = False
    requires_approval: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeUpdate(BaseModel):
    code: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{2,20}$")
    name: str | None = Field(None, min_length=2, max_length=80)
    is_annual: bool | None = None
    requires_approval: bool | None = None


class LeaveTypePublic(BaseModel):
    id: UUID
    code: str
    name: str
    is_annual: bool
    requires_approval: bool
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveTypeListResponse(PageMeta):
    items: list[LeaveTypePublic]


class LeaveRequestBase(BaseModel):
    employee_id: UUID
    type_id: UUID
    start_date: date
    end_date: date
    reason: str | None = None


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None


class LeaveRequestPublic(BaseModel):
    id: UUID
    employee_id: UUID
    type_id: UUID
    status: str
    start_date: date
    end_date: date
    days: Decimal
    reason: str | None = None
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaveRequestListResponse(PageMeta):
    items: list[LeaveRequestPublic]


class AnnualBalance(BaseModel):
    employee_id: UUID
    year: int
    base: Decimal
    used: Decimal
    remaining: Decimal

    model_config = ConfigDict(from_attributes=True)
