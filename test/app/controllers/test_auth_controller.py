import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from sqlmodel import Session
from datetime import datetime, timezone
import bcrypt

# Importar las funciones a testear
from app.controllers.AuthController import (
    login,
    refresh_token,
    create_token_response
)
from app.models.User import User, UserLogin
from app.models.Auth import AuthTokenResponse
from app.models.RefreshToken import RefreshToken

# Configuración de prueba
SECRET_KEY = "test-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_user():
    hashed_password = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt())
    return User(
        id_user=1,
        username="testuser",
        email="test@example.com",
        password=hashed_password.decode('utf-8'),
        is_admin=False
    )

@pytest.fixture
def mock_user_login():
    return UserLogin(
        username="testuser",
        password="testpassword"
    )

@pytest.fixture
def mock_token_payload():
    return {
        "sub": "testuser",
        "email": "test@example.com"
    }

def test_login_success(mock_session, mock_user, mock_user_login):
    # Configurar el mock
    mock_session.exec.return_value.first.return_value = mock_user
    
    # Ejecutar la función
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh:
        mock_access.return_value = "mock_access_token"
        mock_refresh.return_value = ("mock_refresh_token", "mock_jti", datetime.now(timezone.utc))
        
        result = login(mock_user_login, mock_session)
    
    # Verificar resultados
    assert isinstance(result, AuthTokenResponse)
    assert result.access_token == "mock_access_token"
    assert result.refresh_token == "mock_refresh_token"
    assert result.token_type == "bearer"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_login_invalid_username(mock_session, mock_user_login):
    # Configurar el mock para que no encuentre usuario
    mock_session.exec.return_value.first.return_value = None
    
    # Verificar que lanza la excepción correcta
    with pytest.raises(HTTPException) as exc_info:
        login(mock_user_login, mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid user or password"

def test_login_invalid_password(mock_session, mock_user, mock_user_login):
    # Configurar el mock con usuario pero contraseña incorrecta
    mock_session.exec.return_value.first.return_value = mock_user
    mock_user_login.password = "wrongpassword"
    
    # Verificar que lanza la excepción correcta
    with pytest.raises(HTTPException) as exc_info:
        login(mock_user_login, mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid user or password"

def test_refresh_token_success(mock_session, mock_user):
    # Configurar el mock
    mock_session.exec.return_value.first.return_value = mock_user
    
    # Ejecutar la función
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh:
        mock_access.return_value = "mock_access_token"
        mock_refresh.return_value = ("mock_refresh_token", "mock_jti", datetime.now(timezone.utc))
        
        result = refresh_token("testuser", mock_session)
    
    # Verificar resultados
    assert isinstance(result, AuthTokenResponse)
    assert result.access_token == "mock_access_token"
    assert result.refresh_token == "mock_refresh_token"
    assert result.token_type == "bearer"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_refresh_token_invalid_user(mock_session):
    # Configurar el mock para que no encuentre usuario
    mock_session.exec.return_value.first.return_value = None
    
    # Verificar que lanza la excepción correcta
    with pytest.raises(HTTPException) as exc_info:
        refresh_token("nonexistent", mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid username"

def test_create_token_response(mock_session, mock_user):
    # Configurar mocks para las funciones de generación de tokens
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh, \
         patch('app.controllers.AuthController.get_hash') as mock_hash:
        
        # Configurar valores de retorno
        mock_access.return_value = "test_access_token"
        mock_refresh.return_value = ("test_refresh_token", "test_jti", datetime.now(timezone.utc))
        mock_hash.return_value = b"hashed_token"
        
        # Ejecutar la función
        result = create_token_response(mock_user, mock_session)
    
    # Verificar resultados
    assert isinstance(result, AuthTokenResponse)
    assert result.access_token == "test_access_token"
    assert result.refresh_token == "test_refresh_token"
    assert result.token_type == "bearer"
    
    # Verificar que se agregó el refresh token a la base de datos
    mock_session.add.assert_called_once()
    added_token = mock_session.add.call_args[0][0]
    assert isinstance(added_token, RefreshToken)
    assert added_token.id_token == "test_jti"
    assert added_token.id_user == mock_user.id_user
    
    mock_session.commit.assert_called_once()
