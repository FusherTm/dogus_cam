from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    code: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{2,20}$")
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    code: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{2,20}$")
    is_active: bool | None = None


class WarehousePublic(BaseModel):
    id: UUID
    name: str
    code: str | None
    is_active: bool
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseListResponse(PageMeta):
    items: list[WarehousePublic]
