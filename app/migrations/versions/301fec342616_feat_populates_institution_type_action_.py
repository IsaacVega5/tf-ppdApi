"""[feat] populates institution_type, action_type and priority_type

Revision ID: 301fec342616
Revises: 911a4741fe30
Create Date: 2025-04-28 15:38:00.371028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '301fec342616'
down_revision: Union[str, None] = '911a4741fe30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    institution_type = table('institution_type', column('id_institution_type', sa.Integer), column('institution_type', sa.String))
    action_type = table('action_type', column('id_action_type', sa.Integer), column('action_type', sa.String))
    priority_type = table('priority_type', column('id_priority_type', sa.Integer), column('value', sa.String))
    op.bulk_insert(institution_type,[
        {'id_institution_type': 1, 'institution_type': 'Autoridad fiscalizadora nacional'},
        {'id_institution_type': 2, 'institution_type': 'Servicio público sectorial regulador'},
        {'id_institution_type': 3, 'institution_type': 'Ministerio / Nivel central'},
        {'id_institution_type': 4, 'institution_type': 'Gobierno Regional / Delegación Presidencial'},
        {'id_institution_type': 5, 'institution_type': 'SEREMI Medio Ambiente'},
        {'id_institution_type': 6, 'institution_type': 'Municipalidad'},
        {'id_institution_type': 7, 'institution_type': 'Fuerza pública'},
        {'id_institution_type': 8, 'institution_type': 'Universidad / Centro de investigación'},
        {'id_institution_type': 9, 'institution_type': 'Empresa privada mandatada'},
        {'id_institution_type': 10, 'institution_type': 'Otro'},
    ])
    op.bulk_insert(action_type,[
        {'id_action_type': 1, 'action_type': 'Regulación'},
        {'id_action_type': 2, 'action_type': 'Fomento de actividades económicas'},
        {'id_action_type': 3, 'action_type': 'Beneficios para impulsar acciones de interés general'},
        {'id_action_type': 4, 'action_type': 'Estudios'},
        {'id_action_type': 5, 'action_type': 'Educación y difusión'},
        {'id_action_type': 6, 'action_type': 'Política Pública'},
    ])
    op.bulk_insert(priority_type,[
        {'id_priority_type': 1, 'value': 'Reminder'},
        {'id_priority_type': 2, 'value': 'Last week'},
        {'id_priority_type': 3, 'value': 'Last call'},
        {'id_priority_type': 4, 'value': 'Failed'},
    ])

def downgrade() -> None:
    op.execute("""
        DELETE FROM institution_type
        WHERE institution_type IN (
            'Autoridad fiscalizadora nacional',
            'Servicio público sectorial regulador',
            'Ministerio / Nivel central',
            'Gobierno Regional / Delegación Presidencial',
            'SEREMI Medio Ambiente',
            'Municipalidad',
            'Fuerza pública',
            'Universidad / Centro de investigación',
            'Empresa privada mandatada',
            'Otro'
        );
    """)
    op.execute("""
        DELETE FROM action_type
        WHERE action_type IN (
            'Regulación',
            'Fomento de actividades económicas',
            'Beneficios para impulsar acciones de interés general',
            'Estudios',
            'Educación y difusión',
            'Política Pública'
        );
    """)
    op.execute("""
        DELETE FROM priority_type
        WHERE value IN (
            'Failed',
            'Last call',
            'Last week',
            'Reminder'
        );
    """)
