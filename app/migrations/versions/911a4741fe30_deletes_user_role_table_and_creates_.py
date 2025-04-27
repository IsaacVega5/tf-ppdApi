"""deletes user role table and creates enum role col in user institution

Revision ID: 911a4741fe30
Revises: d500c6ac5ac3
Create Date: 2025-04-27 08:39:30.565599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '911a4741fe30'
down_revision: Union[str, None] = 'd500c6ac5ac3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Manually inserted commands for new role enum
    op.drop_constraint('user_institution_id_user_rol_fkey', 'user_institution', type_='foreignkey')
    
    # op.add_column('user_institution', sa.Column('role', sa.Enum('VIEWER', 'EDITOR', name='role_enum', native_enum=True), nullable=True))
    enum_type = sa.Enum('VIEWER', 'EDITOR', name='role_enum', native_enum=False, create_type=False)
    op.add_column('user_institution',sa.Column('role', enum_type, nullable=True))
    
    op.execute("UPDATE user_institution SET role = 'VIEWER' WHERE id_user_rol = 1")
    op.execute("UPDATE user_institution SET role = 'EDITOR' WHERE id_user_rol = 2")
    op.execute("UPDATE user_institution SET role = 'VIEWER' WHERE role IS NULL")
    op.alter_column('user_institution', 'role', nullable=False)
    
    op.drop_column('user_institution', 'id_user_rol')
    op.drop_table('user_rol')


def downgrade() -> None:
    # Manually inserted commands for new role enum
    op.create_table('user_rol',              
    sa.Column('user_rol_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('id_user_rol', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id_user_rol', name='user_rol_pkey')
    )
    #####
    # op.execute(
    #     """
    #     INSERT INTO user_rol (id_user_rol, user_rol_name)
    #     VALUES
    #       (1, 'VIEWER'),
    #       (2, 'EDITOR');
    #     """
    # )
    #####
    op.add_column('user_institution', sa.Column('id_user_rol', sa.INTEGER(), autoincrement=False, nullable=True))
    
    op.execute("UPDATE user_institution SET id_user_rol = 1 WHERE role = 'VIEWER'")
    op.execute("UPDATE user_institution SET id_user_rol = 2 WHERE role = 'EDITOR'")

    op.create_foreign_key('user_institution_id_user_rol_fkey', 'user_institution', 'user_rol', ['id_user_rol'], ['id_user_rol'])
    op.drop_column('user_institution', 'role')
    sa.Enum(name='role_enum').drop(op.get_bind(), checkfirst=True)

