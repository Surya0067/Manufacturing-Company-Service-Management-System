"""Changes in customer name as string

Revision ID: 571c0ec522e3
Revises: 24b04b570e4c
Create Date: 2024-09-21 14:47:28.997023

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "571c0ec522e3"
down_revision: Union[str, None] = "24b04b570e4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "customer",
        "name",
        existing_type=mysql.INTEGER(),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "customer",
        "name",
        existing_type=sa.String(length=50),
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
