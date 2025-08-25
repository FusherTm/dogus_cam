from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    sku: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,40}$")
    price: Decimal = Field(..., ge=0)
    is_active: bool = True
    restock_level: Decimal = Field(0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    sku: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{3,40}$")
    price: Decimal | None = Field(None, ge=0)
    is_active: bool | None = None
    restock_level: Decimal | None = Field(None, ge=0)


class ProductPublic(BaseModel):
    id: UUID
    name: str
    sku: str
    price: Decimal
    is_active: bool
    restock_level: Decimal
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(PageMeta):
    items: list[ProductPublic]
