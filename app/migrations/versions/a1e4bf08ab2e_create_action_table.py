"""Create Action Table

Revision ID: a1e4bf08ab2e
Revises: 1c150280b496
Create Date: 2025-03-30 15:02:40.447222

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1e4bf08ab2e'
down_revision: Union[str, None] = '1c150280b496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_type',
    sa.Column('action_type', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id_action_type', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id_action_type')
    )
    op.create_table('action',
    sa.Column('id_institution', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('rut_creator', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id_action_type', sa.Integer(), nullable=True),
    sa.Column('id_action', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_action_type'], ['action_type.id_action_type'], ),
    sa.ForeignKeyConstraint(['id_institution'], ['institution.id_institution'], ),
    sa.PrimaryKeyConstraint('id_action')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('action')
    op.drop_table('action_type')
    # ### end Alembic commands ###
