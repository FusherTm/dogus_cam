from sqlalchemy import Column, ForeignKey, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_category_org_code"),)

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False
    )
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
