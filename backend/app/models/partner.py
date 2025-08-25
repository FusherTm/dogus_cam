from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT, UUID

from app.db.base import Base


class Partner(Base):
    __tablename__ = "partners"
    __table_args__ = (
        Index("ix_partners_name", text("lower(name)")),
        Index("ix_partners_type", "type"),
        CheckConstraint(
            "type IN ('customer','supplier','both')",
            name="chk_partner_type",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    email = Column(CITEXT(), nullable=True)
    phone = Column(Text, nullable=True)
    tax_number = Column(Text, nullable=True, unique=True)
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at_utc = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
