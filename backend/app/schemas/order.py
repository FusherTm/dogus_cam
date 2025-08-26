from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class OrderItemBase(BaseModel):
    product_id: UUID
    description: str | None = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    line_discount_rate: Decimal = Field(0, ge=0, le=100)
    tax_rate: Decimal = Field(20, ge=0, le=100)


class OrderItemCreate(OrderItemBase):
    pass


class OrderBase(BaseModel):
    partner_id: UUID
    project_name: str | None = None
    delivery_date: date | None = None
    status: str | None = "TEKLIF"
    discount_rate: Decimal = Field(0, ge=0, le=100)
    notes: str | None = None
    items: list[OrderItemCreate]


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    project_name: str | None = None
    delivery_date: date | None = None
    status: str | None = None
    discount_rate: Decimal | None = Field(None, ge=0, le=100)
    notes: str | None = None
    items: list[OrderItemCreate] | None = None


class OrderItemPublic(BaseModel):
    id: UUID
    product_id: UUID
    description: str | None
    quantity: Decimal
    unit_price: Decimal
    line_discount_rate: Decimal
    tax_rate: Decimal
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderPublic(BaseModel):
    id: UUID
    organization_id: UUID
    number: str
    partner_id: UUID
    project_name: str | None
    delivery_date: date | None
    status: str
    discount_rate: Decimal
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    notes: str | None
    created_at_utc: datetime
    items: list[OrderItemPublic]

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(PageMeta):
    items: list[OrderPublic]

