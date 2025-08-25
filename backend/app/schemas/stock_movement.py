from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class StockMovementBase(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    direction: Literal['IN', 'OUT']
    quantity: Decimal = Field(..., gt=0)
    reason: str | None = Field(None, max_length=60)
    document_no: str | None = Field(None, max_length=40)


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementPublic(BaseModel):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    direction: Literal['IN', 'OUT']
    quantity: Decimal
    reason: str | None
    document_no: str | None
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class StockMovementListResponse(PageMeta):
    items: list[StockMovementPublic]
