from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    sku: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,40}$")
    category_id: UUID
    base_price_sqm: Decimal = Field(..., ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    sku: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{3,40}$")
    category_id: UUID | None = None
    base_price_sqm: Decimal | None = Field(None, ge=0)


class ProductPublic(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    sku: str
    category_id: UUID
    base_price_sqm: Decimal

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(PageMeta):
    items: list[ProductPublic]

