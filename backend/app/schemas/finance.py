from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    type: Literal["CASH", "BANK"]


class AccountCreate(AccountBase):
    pass


class AccountPublic(AccountBase):
    id: UUID
    organization_id: UUID
    current_balance: Decimal

    model_config = ConfigDict(from_attributes=True)


class FinancialTransactionBase(BaseModel):
    account_id: UUID
    partner_id: UUID
    order_id: UUID | None = None
    direction: Literal["IN", "OUT"]
    amount: Decimal = Field(..., gt=0)
    transaction_date: datetime
    description: str | None = None
    method: str


class FinancialTransactionCreate(FinancialTransactionBase):
    pass


class FinancialTransactionPublic(FinancialTransactionBase):
    id: UUID
    organization_id: UUID

    model_config = ConfigDict(from_attributes=True)
