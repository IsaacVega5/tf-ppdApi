import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.UserController import create_user, get_all, get_by_id, login, delete_user
from app.models.User import UserCreate, UserLogin
from fastapi import HTTPException, status
import hashlib
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

@pytest.fixture
def sample_user_data():
    """Provee datos de usuario de prueba."""
    return UserCreate(
        email="test@example.com",
        password="securepassword",
        username="testuser"
    )

@pytest.fixture
def sample_login_data():
    """Provee datos de login de prueba."""
    return UserLogin(
        email="test@example.com",
        password="securepassword"
    )

def test_create_user_success(session: Session, sample_user_data: UserCreate):
    """Prueba creación exitosa de usuario."""
    result = create_user(sample_user_data, session)
    
    assert result is not None
    assert result.id_user is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"
    assert result.password == hashlib.sha256("securepassword".encode()).hexdigest()
    assert isinstance(result.created_at, int)
    assert isinstance(result.updated_at, int)

def test_create_user_missing_email(session: Session):
    """Prueba crear usuario sin email."""
    with pytest.raises(ValueError) as exc_info:
        create_user(UserCreate(
            password="pass", 
            username="user"
        ), session)
    assert "field required" in str(exc_info.value).lower()

def test_create_user_missing_password(session: Session):
    """Prueba crear usuario sin contraseña."""
    with pytest.raises(ValueError) as exc_info:
        create_user(UserCreate(
            email="test@test.com", 
            username="user"
        ), session)
    assert "field required" in str(exc_info.value).lower()

def test_create_user_duplicate_email(session: Session):
    """Prueba que no se permitan usuarios con email duplicado."""
    # Crear usuario inicial
    user1 = UserCreate(
        email="test@example.com",
        password="pass1",
        username="user1"
    )
    create_user(user1, session)
    
    # Intentar crear usuario con mismo email
    user2 = UserCreate(
        email="test@example.com",
        password="pass2",
        username="user2"
    )
    
    # Debería lanzar una excepción HTTP 409
    with pytest.raises(HTTPException) as exc_info:
        create_user(user2, session)
    
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "Email already registered" in exc_info.value.detail

def test_get_all_users(session: Session):
    """Prueba obtener todos los usuarios."""
    # Crear varios usuarios
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
    retrieved = get_by_id(str(uuid.uuid4()), session)  # ID que no existe
    assert retrieved is None

def test_login_success(session: Session):
    """Prueba login exitoso."""
    # Crear usuario primero
    user_data = UserCreate(
        email="test@example.com",
        password="securepassword",
        username="testuser"
    )
    create_user(user_data, session)
    
    # Intentar login
    login_data = UserLogin(
        email="test@example.com",
        password="securepassword"
    )
    result = login(login_data, session)
    
    assert result is not None
    assert result.email == "test@example.com"
    assert result.username == "testuser"

def test_login_wrong_password(session: Session):
    """Prueba login con contraseña incorrecta."""
    # Crear usuario
    user_data = UserCreate(
        email="test@example.com",
        password="securepassword",
        username="testuser"
    )
    create_user(user_data, session)
    
    # Intentar login con contraseña incorrecta
    wrong_login = UserLogin(
        email="test@example.com",
        password="wrongpassword"
    )
    
    result = login(wrong_login, session)
    assert isinstance(result, HTTPException)
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in result.detail

def test_login_user_not_found(session: Session):
    """Prueba login con usuario que no existe."""
    non_existent_login = UserLogin(
        email="nonexistent@example.com",
        password="anypassword"
    )
    
    result = login(non_existent_login, session)
    assert isinstance(result, HTTPException)
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in result.detail

def test_delete_user_success(session: Session):
    """Prueba eliminar usuario exitosamente."""
    # Crear usuario primero
    user_data = UserCreate(
        email="test@example.com",
        password="pass",
        username="testuser"
    )
    created_user = create_user(user_data, session)
    
    # Eliminar usuario
    result = delete_user(created_user.id_user, session)
    
    assert result["message"] == f"User was deleted successfully"
    
    # Verificar que ya no existe
    deleted_user = get_by_id(created_user.id_user, session)
    assert deleted_user is None

def test_delete_non_existent_user(session: Session):
    """Prueba eliminar usuario que no existe."""
    non_existent_id = str(uuid.uuid4())
    
    with pytest.raises(HTTPException) as exc_info:
        delete_user(non_existent_id, session)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert f"User not found" in exc_info.value.detail