"""create ar tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.create_table(
        "ar_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.Text(), nullable=False, server_default="TRY"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["invoice_id"], ["sales_invoices.id"], ondelete="SET NULL"),
        sa.CheckConstraint("type IN ('INVOICE','PAYMENT','REFUND','ADJUSTMENT')", name="chk_ar_entry_type"),
        sa.CheckConstraint("amount >= 0", name="chk_ar_entry_amount_nonneg"),
    )
    op.create_table(
        "ar_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.ForeignKeyConstraint(["entry_id"], ["ar_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invoice_id"], ["sales_invoices.id"], ondelete="CASCADE"),
        sa.CheckConstraint("amount > 0", name="chk_ar_allocation_amount_positive"),
    )
    op.create_index("ix_ar_entries_partner", "ar_entries", ["partner_id"])
    op.create_index(
        "ix_ar_entries_date", "ar_entries", ["entry_date", sa.text("created_at_utc DESC")]
    )
    op.create_index("ix_ar_allocations_invoice", "ar_allocations", ["invoice_id"])


def downgrade() -> None:
    op.drop_index("ix_ar_allocations_invoice", table_name="ar_allocations")
    op.drop_table("ar_allocations")
    op.drop_index("ix_ar_entries_date", table_name="ar_entries")
    op.drop_index("ix_ar_entries_partner", table_name="ar_entries")
    op.drop_table("ar_entries")
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
