import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.UserController import create_user, get_all, get_by_id, delete_user
from app.models.User import UserCreate
from fastapi import HTTPException, status
import bcrypt
import uuid
from pydantic import ValidationError

# 1. Configuraciones y fixtures
# -----------------------------

@pytest.fixture(name="session")
def session_fixture():
    """Crea una sesión de prueba con una base de datos en memoria."""
    SQLModel.metadata.create_all(engine)  # Crea las tablas
    with Session(engine) as session:
        yield session  # Retorna la sesión para pruebas
    # Limpiar después de la prueba
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def sample_user_data():
    """Provee datos de usuario de prueba."""
    return UserCreate(
        email="test@example.com",
        password="securepassword",
        username="testuser"
    )

# Configuración de base de datos en memoria
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 2. Tests de Validación de Modelos
# ---------------------------------

def test_create_user_invalid_email():
    """Prueba crear usuario con email inválido."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="not-an-email",
            password="validpass123",
            username="validuser"
        )
    errors = exc_info.value.errors()
    assert any("email" in error["loc"] for error in errors)

def test_create_user_missing_email():
    """Prueba crear usuario sin email."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            password="pass", 
            username="user"
        )
    assert "field required" in str(exc_info.value).lower()

def test_create_user_missing_password():
    """Prueba crear usuario sin contraseña."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            email="test@test.com", 
            username="user"
        )
    assert "field required" in str(exc_info.value).lower()

# 3. Tests de Creación de Usuarios
# --------------------------------

def test_create_user_success(session: Session, sample_user_data: UserCreate):
    """Prueba creación exitosa de usuario."""
    result = create_user(sample_user_data, session)
    assert result is not None
    assert result.id_user is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"
    assert result.password.startswith("$2b$")
    assert bcrypt.checkpw("securepassword".encode(), result.password.encode())

def test_create_user_duplicate_email(session: Session):
    """Prueba que no se permitan usuarios con email duplicado."""
    user1 = UserCreate(
        email="test@example.com",
        password="pass1",
        username="user1"
    )
    create_user(user1, session)
    
    user2 = UserCreate(
        email="test@example.com",
        password="pass2",
        username="user2"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        create_user(user2, session)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "Email already registered" in exc_info.value.detail

# 4. Tests de Operaciones CRUD
# ----------------------------

def test_get_all_users(session: Session):
    """Prueba obtener todos los usuarios."""
    user1 = UserCreate(
        email="test1@example.com",
        password="pass1",
        username="user1"
    )
    user2 = UserCreate(
        email="test2@example.com",
        password="pass2",
        username="user2"
    )
    create_user(user1, session)
    create_user(user2, session)

    users = get_all(session)
    assert len(users) == 2
    assert users[0].email == "test1@example.com"
    assert users[1].email == "test2@example.com"

def test_get_by_id_success(session: Session):
    """Prueba obtener usuario por ID exitosamente."""
    user_data = UserCreate(
        email="test@example.com",
        password="pass",
        username="testuser"
    )
    created_user = create_user(user_data, session)
    retrieved = get_by_id(created_user.id_user, session)
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
    assert retrieved.username == "testuser"

def test_get_by_id_not_found(session: Session):
    """Prueba obtener usuario con ID inexistente."""
    retrieved = get_by_id(str(uuid.uuid4()), session)
    assert retrieved is None

def test_update_user(session: Session):
    """Prueba actualización de usuario."""
    user = UserCreate(
        email="test@example.com",
        password="pass",
        username="testuser"
    )
    created_user = create_user(user, session)
    
    created_user.email = "new@example.com"
    session.add(created_user)
    session.commit()
    session.refresh(created_user)
    
    updated_user = get_by_id(created_user.id_user, session)
    assert updated_user.email == "new@example.com"

# 5. Tests de Eliminación
# -----------------------

def test_delete_user_success(session: Session):
    """Prueba eliminar usuario exitosamente."""
    user_data = UserCreate(
        email="test@example.com",
        password="pass",
        username="testuser"
    )
    created_user = create_user(user_data, session)
    
    result = delete_user(created_user.id_user, session)
    assert result["message"] == "User was deleted successfully"
    
    deleted_user = get_by_id(created_user.id_user, session)
    assert deleted_user is None

def test_delete_non_existent_user(session: Session):
    """Prueba eliminar usuario que no existe."""
    non_existent_id = str(uuid.uuid4())
    with pytest.raises(HTTPException) as exc_info:
        delete_user(non_existent_id, session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in exc_info.value.detail