"""changesin  spare part table

Revision ID: 30051f193c0e
Revises: 1586348acca7
Create Date: 2024-09-26 10:04:50.376524

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "30051f193c0e"
down_revision: Union[str, None] = "1586348acca7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("spare_parts", sa.Column("status_time", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("spare_parts", "status_time")
    # ### end Alembic commands ###
