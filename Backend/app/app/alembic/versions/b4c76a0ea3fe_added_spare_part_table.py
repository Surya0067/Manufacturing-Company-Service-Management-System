"""added spare part table

Revision ID: b4c76a0ea3fe
Revises: 12edcac38f07
Create Date: 2024-09-25 17:08:11.380355

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "b4c76a0ea3fe"
down_revision: Union[str, None] = "12edcac38f07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "spare_parts",
        "quantity",
        existing_type=mysql.INTEGER(),
        type_=sa.Float(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "spare_parts",
        "quantity",
        existing_type=sa.Float(),
        type_=mysql.INTEGER(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
