from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PageMeta


class EmployeeBase(BaseModel):
    code: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,40}$")
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr | None = None
    phone: str | None = None
    department: str | None = None
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True
    annual_leave_days_per_year: Decimal = Decimal("14")


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    code: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{3,40}$")
    first_name: str | None = Field(None, min_length=2, max_length=60)
    last_name: str | None = Field(None, min_length=2, max_length=60)
    email: EmailStr | None = None
    phone: str | None = None
    department: str | None = None
    title: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    annual_leave_days_per_year: Decimal | None = None


class EmployeePublic(BaseModel):
    id: UUID
    code: str
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    department: str | None = None
    title: str | None = None
    start_date: date
    end_date: date | None = None
    is_active: bool
    annual_leave_days_per_year: Decimal
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(PageMeta):
    items: list[EmployeePublic]
