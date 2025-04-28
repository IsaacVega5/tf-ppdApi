import pytest
from fastapi import HTTPException, status
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.ActionTypeController import get_all, get_by_id, create_action_type, delete_action_type, update_action_type
from app.models import ActionType

# Configuración de base de datos en memoria para pruebas
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    """Crea una sesión de prueba con una base de datos en memoria."""
    SQLModel.metadata.create_all(engine)
    # Crea las tablas
    with Session(engine) as session:
      yield session  # Retorna la sesión para pruebas
    # Limpia las tablas después de la prueba
    SQLModel.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_get_all_action_types(session):
    """Prueba obtener todos los tipos de acciones."""
    type1 = ActionType(id_action_type=1, action_type="Tipo A")
    type2 = ActionType(id_action_type=2, action_type="Tipo B")

    session.add_all([type1, type2])
    session.commit()

    action_types = await get_all(session)

    assert len(action_types) == 2
    assert action_types[0].action_type == "Tipo A"
    assert action_types[1].action_type == "Tipo B"

@pytest.mark.asyncio
async def test_get_action_type_by_id(session):
    """Prueba obtener un tipo de acción por ID."""
    action_type = ActionType(id_action_type=1, action_type="Tipo A")
    session.add(action_type)
    session.commit()

    retrieved = await get_by_id(1, session)

    assert retrieved is not None
    assert retrieved.action_type == "Tipo A"

@pytest.mark.asyncio
async def test_create_action_type(session):
    """Prueba la creación de un tipo de acción."""
    action_type_data = ActionType(action_type="Nuevo Tipo")
    created_action_type = await create_action_type(action_type_data, session)

    assert created_action_type is not None
    assert created_action_type.action_type == "Nuevo Tipo"
    
@pytest.mark.asyncio
async def test_create_action_type_empty(session):
    """Prueba la creación de un tipo de acción vacío."""
    action_type_data = ActionType(action_type="")
    with pytest.raises(HTTPException) as excinfo:
        await create_action_type(action_type_data, session)
    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Action type cannot be empty"

@pytest.mark.asyncio
async def test_delete_action_type(session):
    """Prueba la eliminación de un tipo de acción."""
    action_type = ActionType(id_action_type=1, action_type="Tipo A")
    session.add(action_type)
    session.commit()

    await delete_action_type(1, session)
  
    with pytest.raises(HTTPException) as excinfo:
        await get_by_id(1, session)
    assert excinfo.value.status_code is status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_action_type(session):
    """Prueba la actualización de un tipo de acción."""
    action_type = ActionType(id_action_type=1, action_type="Nombre Antiguo")
    session.add(action_type)
    session.commit()

    update_data = ActionType(action_type="Actualizar Nombre")
    updated_action_type = await update_action_type(1, update_data, session)

    assert updated_action_type.action_type == "Actualizar Nombre"

async def test_update_action_type_not_found(session):
    """Prueba la actualización de un tipo de acción que no existe."""
    update_data = ActionType(action_type="Actualizar Nombre")
    with pytest.raises(HTTPException) as excinfo:
        await update_action_type(999, update_data, session)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Action type not found"