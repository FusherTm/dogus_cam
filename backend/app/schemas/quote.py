from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import PageMeta


class QuoteItemIn(BaseModel):
    product_id: UUID
    description: str | None = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    line_discount_rate: Decimal = Field(0, ge=0, le=100)
    tax_rate: Decimal = Field(20, ge=0, le=100)


class QuoteItemPublic(QuoteItemIn):
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class QuoteCreate(BaseModel):
    partner_id: UUID
    currency: str = "TRY"
    issue_date: date | None = None
    valid_until: date | None = None
    notes: str | None = None
    discount_rate: Decimal = Field(0, ge=0, le=100)
    items: list[QuoteItemIn] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def check_items(cls, v):
        if not v:
            raise ValueError("at least one item required")
        return v


class QuoteUpdate(BaseModel):
    notes: str | None = None
    discount_rate: Decimal | None = Field(None, ge=0, le=100)
    valid_until: date | None = None
    items: list[QuoteItemIn] | None = Field(None, min_length=1)


class QuotePublic(BaseModel):
    id: UUID
    number: str
    partner_id: UUID
    currency: str
    status: str
    issue_date: date
    valid_until: date | None
    notes: str | None
    discount_rate: Decimal
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    created_at_utc: datetime
    items: list[QuoteItemPublic]

    model_config = ConfigDict(from_attributes=True)


class QuoteSummary(BaseModel):
    id: UUID
    number: str
    partner_id: UUID
    currency: str
    status: str
    issue_date: date
    valid_until: date | None
    notes: str | None
    discount_rate: Decimal
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class QuoteListResponse(PageMeta):
    items: list[QuoteSummary]
