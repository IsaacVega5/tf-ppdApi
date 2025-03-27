import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.InstitutionController import get_all, get_by_id, create_institution, delete_institution, update_institution
from app.models import Institution, InstitutionCreate, InstitutionUpdate, InstitutionType
from fastapi import HTTPException, status
import uuid

# Configuración de base de datos en memoria
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    """Crea una sesión de prueba con una base de datos en memoria."""
    SQLModel.metadata.create_all(engine)  # Crea las tablas
    with Session(engine) as session:
        yield session  # Retorna la sesión para pruebas
    # Limpiar después de la prueba
    SQLModel.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_get_all_institutions(session):
    """Prueba obtener todas las instituciones con sesión asíncrona."""
    institution1 = Institution(id_institution="1234", institution_name="Institución 1", id_institution_type=1)
    institution2 = Institution(id_institution="5678", institution_name="Institución 2", id_institution_type=2)

    session.add_all([institution1, institution2])
    session.commit()

    institutions = await get_all(session)  # `await` necesario

    assert len(institutions) == 2
    assert institutions[0].institution_name == "Institución 1"
    assert institutions[1].institution_name == "Institución 2"

@pytest.mark.asyncio
async def test_get_by_id(session):
    """Prueba obtener una institución por su ID con sesión asíncrona."""
    institution = Institution(id_institution="12345", institution_name="Institución X", id_institution_type=2)
    session.add(institution)
    session.commit()

    retrieved = await get_by_id("12345", session)  # `await` necesario

    assert retrieved is not None
    assert retrieved.institution_name == "Institución X"
    assert retrieved.id_institution_type == 2

@pytest.mark.asyncio
async def test_get_by_id_not_found(session):
    """Prueba obtener una institución con un ID que no existe."""
    retrieved = await get_by_id("non_existent_id", session)
    assert retrieved is None

@pytest.mark.asyncio
async def test_create_institution_success(session: Session):
    """Prueba creación exitosa de institución"""
    # Crear un tipo de institución primero
    institution_type = InstitutionType(institution_type="Escuela")
    session.add(institution_type)
    session.commit()

    # Datos válidos
    institution_data = InstitutionCreate(
        institution_name="Escuela Primaria",
        id_institution_type=1
    )

    # Crear institución
    result = await create_institution(institution_data, session)

    assert result is not None
    assert result.id_institution is not None
    assert result.institution_name == "Escuela Primaria"
    assert result.id_institution_type == 1

@pytest.mark.asyncio
async def test_create_institution_missing_name(session):
    with pytest.raises(ValueError) as exc_info:
        await create_institution(InstitutionCreate(id_institution_type=1), session)
    assert "field required" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_create_institution_missing_type(session):
    with pytest.raises(ValueError) as exc_info:
        await create_institution(InstitutionCreate(institution_name="Nombre"), session)
    assert "field required" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_create_institution_duplicate(session: Session):
    """Prueba que no se permitan instituciones duplicadas"""
    # Crear tipo e institución inicial
    institution_type = InstitutionType(institution_type="Universidad")
    session.add(institution_type)
    session.commit()

    institution_data = InstitutionCreate(
        institution_name="Universidad Nacional",
        id_institution_type=1
    )
    await create_institution(institution_data, session)

    # Intentar crear duplicado
    with pytest.raises(HTTPException) as exc_info:
        await create_institution(institution_data, session)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc_info.value.detail

@pytest.mark.asyncio
async def test_create_institution_invalid_type(session: Session):
    """Prueba con tipo de institución inexistente"""
    institution_data = InstitutionCreate(
        institution_name="Institución Inválida",
        id_institution_type=999  # ID que no existe
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_institution(institution_data, session)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_institution(session):
    """Prueba actualizar una institución con sesión asíncrona."""
    institution = Institution(id_institution="123456", institution_name="Nombre Antiguo", id_institution_type=1)
    session.add(institution)
    session.commit()

    update_data = InstitutionUpdate(institution_name="Nuevo Nombre")
    updated_institution = await update_institution("123456", update_data, session)  # `await` necesario

    assert updated_institution.institution_name == "Nuevo Nombre"

@pytest.mark.asyncio
async def test_update_non_existent_institution(session):
    """Prueba actualizar una institución que no existe."""
    update_data = InstitutionUpdate(institution_name="No debería funcionar")
    with pytest.raises(HTTPException) as exc_info:
        await update_institution("non_existent", update_data, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_with_optional_fields(session):
    """Prueba actualización con campos opcionales."""
    # Primero crear el tipo de institución necesario
    from app.models import InstitutionType
    institution_type = InstitutionType(id_institution_type=1, institution_type="Escuela")
    session.add(institution_type)
    session.commit()

    # Ahora crear la institución inicial
    initial_data = InstitutionCreate(institution_name="Original", id_institution_type=1)
    created = await create_institution(initial_data, session)
    
    # Actualizar solo el nombre
    update1 = InstitutionUpdate(institution_name="Nuevo nombre")
    updated1 = await update_institution(created.id_institution, update1, session)
    assert updated1.institution_name == "Nuevo nombre"
    assert updated1.id_institution_type == 1  # No cambió
    
    # Actualizar solo el tipo
    # Primero crear otro tipo si es necesario
    institution_type2 = InstitutionType(id_institution_type=2, institution_type="Universidad")
    session.add(institution_type2)
    session.commit()
    
    update2 = InstitutionUpdate(id_institution_type=2)
    updated2 = await update_institution(created.id_institution, update2, session)
    assert updated2.id_institution_type == 2
    assert updated2.institution_name == "Nuevo nombre"  # No cambió 

@pytest.mark.asyncio
async def test_update_institution_success(session):
    """Prueba actualizar una institución exitosamente."""
    # Crear tipo e institución inicial
    institution_type1 = InstitutionType(institution_type="Tipo 1")
    institution_type2 = InstitutionType(institution_type="Tipo 2")
    session.add_all([institution_type1, institution_type2])
    session.commit()
    
    institution = Institution(id_institution="123", institution_name="Original", id_institution_type=1)
    session.add(institution)
    session.commit()

    # Actualizar nombre
    update_data = InstitutionUpdate(institution_name="Nuevo Nombre")
    updated = await update_institution("123", update_data, session)
    assert updated.institution_name == "Nuevo Nombre"
    assert updated.id_institution_type == 1  # No cambió

    # Actualizar tipo
    update_data = InstitutionUpdate(id_institution_type=2)
    updated = await update_institution("123", update_data, session)
    assert updated.id_institution_type == 2
    assert updated.institution_name == "Nuevo Nombre"  # No cambió

@pytest.mark.asyncio
async def test_update_non_existent_institution(session):
    """Prueba actualizar una institución que no existe."""
    update_data = InstitutionUpdate(institution_name="No existe")
    with pytest.raises(HTTPException) as exc_info:
        await update_institution("non_existent", update_data, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_institution_duplicate_name_type(session):
    """Prueba no permitir actualización a nombre+tipo que ya existe."""
    # Crear tipos e instituciones
    institution_type = InstitutionType(institution_type="Escuela")
    session.add(institution_type)
    session.commit()
    
    institution1 = Institution(id_institution="1", institution_name="Escuela A", id_institution_type=1)
    institution2 = Institution(id_institution="2", institution_name="Escuela B", id_institution_type=1)
    session.add_all([institution1, institution2])
    session.commit()

    # Intentar cambiar institución2 al nombre de institución1
    update_data = InstitutionUpdate(institution_name="Escuela A")
    with pytest.raises(HTTPException) as exc_info:
        await update_institution("2", update_data, session)
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_institution_invalid_type(session):
    """Prueba actualizar con tipo de institución inválido."""
    # Crear institución
    institution = Institution(id_institution="123", institution_name="Original", id_institution_type=1)
    session.add(institution)
    session.commit()

    # Intentar actualizar con tipo inválido
    update_data = InstitutionUpdate(id_institution_type=999)
    with pytest.raises(HTTPException) as exc_info:
        await update_institution("123", update_data, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_institution_no_changes(session):
    """Prueba actualizar sin cambios."""
    institution = Institution(id_institution="123", institution_name="Original", id_institution_type=1)
    session.add(institution)
    session.commit()

    # Enviar update sin cambios
    update_data = InstitutionUpdate()
    updated = await update_institution("123", update_data, session)
    
    assert updated.institution_name == "Original"
    assert updated.id_institution_type == 1

@pytest.mark.asyncio
async def test_delete_institution_success(session):
    """Prueba eliminar una institución exitosamente."""
    institution = Institution(id_institution="123", institution_name="A eliminar", id_institution_type=1)
    session.add(institution)
    session.commit()

    result = await delete_institution("123", session)
    
    assert result["message"] == "Institution 123 deleted successfully"
    assert result["deleted_institution"].id_institution == "123"
    
    retrieved = await get_by_id("123", session)
    assert retrieved is None

@pytest.mark.asyncio
async def test_delete_non_existent_institution(session):
    """Prueba eliminar una institución que no existe."""
    with pytest.raises(HTTPException) as exc_info:
        await delete_institution("non_existent", session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_delete_institution_with_users(session):
    """Prueba eliminar una institución con usuarios asociados."""
    from app.models import UserInstitution, User

    # Crear institución y usuario asociado
    institution = Institution(id_institution="123", institution_name="Con usuarios", id_institution_type=1)
    user = User(
        id_user="user1", 
        email="test@example.com", 
        password="hash"
    )
    user_institution = UserInstitution(
        id_user_institution=str(uuid.uuid4()), 
        id_user="user1", 
        id_institution="123"
    )

    session.add_all([institution, user, user_institution])
    session.commit()