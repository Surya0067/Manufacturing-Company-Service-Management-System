"""Added TicketRejected table

Revision ID: 6d5aea664a18
Revises: a9c93d9c24a0
Create Date: 2024-09-22 21:32:49.695365

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d5aea664a18"
down_revision: Union[str, None] = "a9c93d9c24a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
