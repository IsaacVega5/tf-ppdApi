import pytest
from fastapi import HTTPException, status
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.InstitutionTypeController import get_all, get_by_id, create_institution_type, delete_institution_type, update_institution_type
from app.models import InstitutionType, InstitutionTypeCreate

# Configuración de base de datos en memoria para pruebas
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(name="session")
def session_fixture():
    """Crea una sesión de prueba con una base de datos en memoria."""
    SQLModel.metadata.create_all(engine)  # Crea las tablas
    with Session(engine) as session:
        yield session  # Retorna la sesión para pruebas
    # Limpia las tablas después de la prueba
    SQLModel.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_get_all_institution_types(session):
    """Prueba obtener todos los tipos de instituciones."""
    type1 = InstitutionType(id_institution_type=1, institution_type="Universidad")
    type2 = InstitutionType(id_institution_type=2, institution_type="Escuela")

    session.add_all([type1, type2])
    session.commit()

    institution_types = get_all(session)

    assert len(institution_types) == 2
    assert institution_types[0].institution_type == "Universidad"
    assert institution_types[1].institution_type == "Escuela"


@pytest.mark.asyncio
async def test_get_institution_type_by_id(session):
    """Prueba obtener un tipo de institución por ID."""
    institution_type = InstitutionType(id_institution_type=1, institution_type="Universidad")
    session.add(institution_type)
    session.commit()

    retrieved = get_by_id(1, session)

    assert retrieved is not None
    assert retrieved.institution_type == "Universidad"


@pytest.mark.asyncio
async def test_create_institution_type(session):
    """Prueba la creación de un tipo de institución."""
    institution_type_data = InstitutionTypeCreate(institution_type="Nuevo Tipo")
    created_institution_type = create_institution_type(institution_type_data, session)

    assert created_institution_type is not None
    assert created_institution_type.institution_type == "Nuevo Tipo"


@pytest.mark.asyncio
async def test_update_institution_type(session):
    """Prueba actualizar un tipo de institución."""
    institution_type = InstitutionType(id_institution_type=1, institution_type="Nombre Antiguo")
    session.add(institution_type)
    session.commit()

    update_data = InstitutionTypeCreate(institution_type="Actualizar Nombre")
    updated_institution_type = update_institution_type(1, update_data, session)

    assert updated_institution_type.institution_type == "Actualizar Nombre"


@pytest.mark.asyncio
async def test_delete_institution_type(session):
    """Prueba eliminar un tipo de institución."""
    institution_type = InstitutionType(id_institution_type=1, institution_type="Institución a Eliminar")
    session.add(institution_type)
    session.commit()

    # Verificar que existe antes de eliminar
    assert get_by_id(1, session) is not None
    
    # Eliminar
    result = delete_institution_type(1, session)
    assert result["message"] == "Institution type 1 deleted"
    
    # Verificar que ya no existe (debe lanzar excepción)
    with pytest.raises(HTTPException) as exc_info:
        get_by_id(1, session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_nonexistent_institution_type(session):
    """Obtener tipo inexistente debe retornar 404"""
    with pytest.raises(HTTPException) as exc:
        get_by_id(999, session)
    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_delete_nonexistent_institution_type(session):
    """Eliminar tipo inexistente debe fallar"""
    with pytest.raises(HTTPException) as exc:
        delete_institution_type(999, session)
    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()

@pytest.mark.asyncio
async def test_update_nonexistent_institution_type(session):
    """Actualizar tipo inexistente debe fallar"""
    update_data = InstitutionTypeCreate(institution_type="Nuevo nombre")
    with pytest.raises(HTTPException) as exc:
        update_institution_type(999, update_data, session)
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_partial_update(session):
    """Actualización parcial debe funcionar"""
    # Setup
    original = InstitutionType(id_institution_type=1, institution_type="Original")
    session.add(original)
    session.commit()
    
    # Actualización parcial
    update_data = InstitutionTypeCreate(institution_type="Actualizado")
    updated = update_institution_type(1, update_data, session)
    
    assert updated.institution_type == "Actualizado"
    assert updated.id_institution_type == 1

@pytest.mark.asyncio
async def test_create_institution_type_with_empty_name(session):
    """Prueba crear un tipo con nombre vacío."""
    with pytest.raises(HTTPException) as exc_info:
        create_institution_type(InstitutionTypeCreate(institution_type=""), session)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot be empty" in str(exc_info.value.detail)