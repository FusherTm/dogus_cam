"""create quotes tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("number", sa.Text(), nullable=False, unique=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("currency", sa.Text(), nullable=False, server_default="TRY"),
        sa.Column("status", sa.Text(), nullable=False, server_default="DRAFT"),
        sa.Column("issue_date", sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("discount_rate", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
        sa.Column("subtotal", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_total", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.Column("grand_total", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at_utc", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "status IN ('DRAFT','SENT','APPROVED','REJECTED','EXPIRED')",
            name="chk_quote_status",
        ),
        sa.CheckConstraint(
            "discount_rate >= 0 AND discount_rate <= 100",
            name="chk_quote_discount_rate",
        ),
    )
    op.create_table(
        "quote_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("line_discount_rate", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="20.00"),
        sa.Column("line_subtotal", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.Column("line_tax", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False, server_default="0.00"),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("quantity > 0", name="chk_quote_item_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="chk_quote_item_unit_price_nonneg"),
        sa.CheckConstraint(
            "line_discount_rate >= 0 AND line_discount_rate <= 100",
            name="chk_quote_item_discount_rate",
        ),
        sa.CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="chk_quote_item_tax_rate",
        ),
    )
    op.create_index("ix_quotes_partner", "quotes", ["partner_id"])
    op.create_index("ix_quotes_created", "quotes", [sa.text("created_at_utc DESC")])
    op.create_index("ix_quote_items_quote", "quote_items", ["quote_id"])


def downgrade() -> None:
    op.drop_index("ix_quote_items_quote", table_name="quote_items")
    op.drop_table("quote_items")
    op.drop_index("ix_quotes_created", table_name="quotes")
    op.drop_index("ix_quotes_partner", table_name="quotes")
    op.drop_table("quotes")
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
