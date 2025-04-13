"""[feat] Add is_activated column in user_institution table

Revision ID: 26a1ccdfbe8e
Revises: 7f8728b5c191
Create Date: 2025-04-12 11:59:58.351265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '26a1ccdfbe8e'
down_revision: Union[str, None] = '7f8728b5c191'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_institution', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.execute('UPDATE user_institution SET is_active = TRUE')
    op.alter_column('user_institution', 'is_active', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_institution', 'is_active')
    # ### end Alembic commands ###
