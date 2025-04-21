"""Create user type base roles

Revision ID: d500c6ac5ac3
Revises: 26a1ccdfbe8e
Create Date: 2025-04-18 18:01:05.462833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd500c6ac5ac3'
down_revision: Union[str, None] = '26a1ccdfbe8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert default user roles if they don't exist
        
    meta = sa.MetaData()
    user_rol = sa.Table('user_rol', meta, autoload_with=op.get_bind())
    
    conn = op.get_bind()
    existing_roles = conn.execute(
        sa.select(user_rol.c.user_rol_name)
    ).fetchall()
    
    existing_roles_names = [role[0] for role in existing_roles]
    
    default_roles = [
        {"user_rol_name": "viewer"},    
        {"user_rol_name": "editor"}    
    ]

    roles_to_insert = [
        role for role in default_roles 
        if role["user_rol_name"] not in existing_roles_names
    ]
    
    if roles_to_insert:
        op.bulk_insert(
            user_rol,
            roles_to_insert
        )


def downgrade() -> None:
    # Remove default user roles
    op.execute("DELETE FROM user_rol WHERE user_rol_name IN ('viewer', 'editor')")