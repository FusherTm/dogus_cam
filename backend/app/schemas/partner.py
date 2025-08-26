from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PageMeta


class PartnerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    type: Literal["CUSTOMER", "SUPPLIER", "BOTH"]
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_number: str | None = None


class PartnerCreate(PartnerBase):
    pass


class PartnerUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    type: Literal["CUSTOMER", "SUPPLIER", "BOTH"] | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    tax_number: str | None = None


class PartnerPublic(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    type: Literal["CUSTOMER", "SUPPLIER", "BOTH"]
    contact_person: str | None
    phone: str | None
    email: EmailStr | None
    address: str | None
    tax_number: str | None

    model_config = ConfigDict(from_attributes=True)


class PartnerListResponse(PageMeta):
    items: list[PartnerPublic]
