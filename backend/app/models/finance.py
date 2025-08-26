from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("type IN ('CASH','BANK')", name="chk_account_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    current_balance = Column(Numeric(14, 2), nullable=False, server_default=text("0"))


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"
    __table_args__ = (
        CheckConstraint("direction IN ('IN','OUT')", name="chk_fin_tx_direction"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    partner_id = Column(
        UUID(as_uuid=True), ForeignKey("partners.id", ondelete="RESTRICT"), nullable=False
    )
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True
    )
    direction = Column(Text, nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    method = Column(Text, nullable=False)
