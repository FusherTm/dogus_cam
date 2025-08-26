from sqlalchemy import Column, Text, CheckConstraint, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, CITEXT

from app.db.base import Base


class Partner(Base):
    __tablename__ = "partners"
    __table_args__ = (
        Index("ix_partners_name", text("lower(name)")),
        Index("ix_partners_type", "type"),
        CheckConstraint(
            "type IN ('CUSTOMER','SUPPLIER','BOTH')",
            name="chk_partner_type",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    contact_person = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    email = Column(CITEXT(), nullable=True)
    address = Column(Text, nullable=True)
    tax_number = Column(Text, nullable=True)
