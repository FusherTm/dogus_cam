from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    role: str
    is_active: bool
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)
