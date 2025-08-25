from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

from app.schemas.common import PageMeta


class PartnerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    type: Literal["customer", "supplier", "both"]
    email: EmailStr | None = None
    phone: str | None = None
    tax_number: constr(min_length=5, max_length=20) | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    is_active: bool = True


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    type: Literal["customer", "supplier", "both"] | None = None
    email: EmailStr | None = None
    phone: str | None = None
    tax_number: constr(min_length=5, max_length=20) | None = None
    billing_address: str | None = None
    shipping_address: str | None = None
    is_active: bool | None = None


class PartnerPublic(BaseModel):
    id: UUID
    name: str
    type: Literal["customer", "supplier", "both"]
    email: EmailStr | None
    phone: str | None
    tax_number: str | None
    billing_address: str | None
    shipping_address: str | None
    is_active: bool
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class PartnerListResponse(PageMeta):
    items: list[PartnerPublic]
