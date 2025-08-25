"""create leave tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_types",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "is_annual",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "requires_approval",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "leave_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "employee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("leave_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'DRAFT'"),
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "days",
            sa.Numeric(6, 2),
            nullable=False,
            server_default=sa.text("0.00"),
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at_utc",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT','SUBMITTED','APPROVED','REJECTED','CANCELLED')",
            name="ck_leave_requests_status",
        ),
    )

    op.create_index(
        "ix_leave_requests_emp",
        "leave_requests",
        ["employee_id", "start_date", "end_date"],
    )
    op.create_index(
        "ix_leave_requests_created",
        "leave_requests",
        [sa.text("created_at_utc DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_leave_requests_created", table_name="leave_requests")
    op.drop_index("ix_leave_requests_emp", table_name="leave_requests")
    op.drop_table("leave_requests")
    op.drop_table("leave_types")
