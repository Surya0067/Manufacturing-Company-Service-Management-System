"""changes in  expense tables

Revision ID: d8b12eeb1d93
Revises: a797defeaf2e
Create Date: 2024-09-26 22:32:51.518416

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "d8b12eeb1d93"
down_revision: Union[str, None] = "a797defeaf2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("travel_expense_rejection")
    op.add_column(
        "travel_expense_reports",
        sa.Column("image_path", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "travel_expense_reports",
        sa.Column("status", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "travel_expense_reports", sa.Column("status_by", sa.Integer(), nullable=True)
    )
    op.add_column(
        "travel_expense_reports", sa.Column("status_at", sa.DateTime(), nullable=True)
    )
    op.drop_constraint(
        "travel_expense_reports_ibfk_1", "travel_expense_reports", type_="foreignkey"
    )
    op.create_foreign_key(None, "travel_expense_reports", "user", ["status_by"], ["id"])
    op.drop_column("travel_expense_reports", "approval_status")
    op.drop_column("travel_expense_reports", "approved_at")
    op.drop_column("travel_expense_reports", "approved_by")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "travel_expense_reports",
        sa.Column("approved_by", mysql.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "travel_expense_reports",
        sa.Column("approved_at", mysql.DATETIME(), nullable=True),
    )
    op.add_column(
        "travel_expense_reports",
        sa.Column("approval_status", mysql.VARCHAR(length=50), nullable=True),
    )
    op.drop_constraint(None, "travel_expense_reports", type_="foreignkey")
    op.create_foreign_key(
        "travel_expense_reports_ibfk_1",
        "travel_expense_reports",
        "user",
        ["approved_by"],
        ["id"],
    )
    op.drop_column("travel_expense_reports", "status_at")
    op.drop_column("travel_expense_reports", "status_by")
    op.drop_column("travel_expense_reports", "status")
    op.drop_column("travel_expense_reports", "image_path")
    op.create_table(
        "travel_expense_rejection",
        sa.Column("id", mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("report_id", mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "rejected_by_id", mysql.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("rejection_reason", mysql.VARCHAR(length=255), nullable=False),
        sa.Column("rejected_at", mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(
            ["rejected_by_id"], ["user.id"], name="travel_expense_rejection_ibfk_1"
        ),
        sa.ForeignKeyConstraint(
            ["report_id"],
            ["travel_expense_reports.id"],
            name="travel_expense_rejection_ibfk_2",
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    # ### end Alembic commands ###
