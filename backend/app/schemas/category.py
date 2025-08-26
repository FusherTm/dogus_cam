from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PageMeta


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    code: str = Field(..., pattern=r"^[A-Za-z0-9_-]{2,20}$")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    code: str | None = Field(None, pattern=r"^[A-Za-z0-9_-]{2,20}$")


class CategoryPublic(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(PageMeta):
    items: list[CategoryPublic]

