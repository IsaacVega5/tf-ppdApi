"""Create Message

Revision ID: aa14078b49e7
Revises: 0bb11c65b4b1
Create Date: 2025-03-30 19:45:46.059541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'aa14078b49e7'
down_revision: Union[str, None] = '0bb11c65b4b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('time_before', sa.Integer(), nullable=True),
    sa.Column('id_message', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id_message'),
    sa.UniqueConstraint('id_message')
    )
    op.create_unique_constraint(None, 'ppda', ['id_ppda'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ppda', type_='unique')
    op.drop_table('message')
    # ### end Alembic commands ###
