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
    # Insert default user roles
        
    meta = sa.MetaData()
    user_rol = sa.Table('user_rol', meta, autoload_with=op.get_bind())
    op.bulk_insert(
        user_rol,
        [
            {
                "id_user_rol": 1,
                "user_rol_name": "viewer"
            },
            {
                "id_user_rol": 2,
                "user_rol_name": "editor"
            }
        ]
    )


def downgrade() -> None:
    # Remove default user roles
    op.execute("DELETE FROM user_rol WHERE id_user_rol IN (1, 2)")