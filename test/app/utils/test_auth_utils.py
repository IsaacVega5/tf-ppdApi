import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status
import bcrypt
from app.controllers import UserController
import os
from sqlmodel import Session

# Importar componentes a testear
from app.controllers.AuthController import login, refresh_token, create_token_response
from app.models.User import User, UserLogin
from app.models.Auth import Token
from app.models.RefreshToken import RefreshToken
from app.utils.auth import (
    generate_access_token,
    generate_refresh_token,
    verify_token_by_type,
    verify_access_token,
    verify_refresh_token,
    get_current_user,
    get_admin_user,
    get_refresh_username
)
from app.utils.hashing import verify_password, get_hash

# Configuración de prueba
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Mock data
TEST_SECRET_KEY = "test-secret-key"
TEST_ALGORITHM = "HS256"
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"

# Fixtures
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
    # Configurar mocks
    mock_session.exec.return_value.first.return_value = mock_user
    
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh:
        
        mock_access.return_value = "mock_access_token"
        mock_refresh.return_value = ("mock_refresh_token", "mock_jti", datetime.now(timezone.utc))
        
        result = login(mock_user_login, mock_session)
    
    # Verificaciones
    assert isinstance(result, Token)
    assert result.access_token == "mock_access_token"
    assert result.refresh_token == "mock_refresh_token"
    assert result.token_type == "bearer"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_login_invalid_username(mock_session, mock_user_login):
    mock_session.exec.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        login(mock_user_login, mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid user or password"

def test_login_invalid_password(mock_session, mock_user, mock_user_login):
    mock_session.exec.return_value.first.return_value = mock_user
    mock_user_login.password = "wrongpassword"
    
    with pytest.raises(HTTPException) as exc_info:
        login(mock_user_login, mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid user or password"

def test_refresh_token_success(mock_session, mock_user):
    mock_session.exec.return_value.first.return_value = mock_user
    
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh:
        
        mock_access.return_value = "mock_access_token"
        mock_refresh.return_value = ("mock_refresh_token", "mock_jti", datetime.now(timezone.utc))
        
        result = refresh_token("testuser", mock_session)
    
    assert isinstance(result, Token)
    assert result.access_token == "mock_access_token"
    assert result.refresh_token == "mock_refresh_token"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_refresh_token_invalid_user(mock_session):
    mock_session.exec.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        refresh_token("nonexistent", mock_session)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid username"

def test_create_token_response(mock_session, mock_user):
    with patch('app.controllers.AuthController.generate_access_token') as mock_access, \
         patch('app.controllers.AuthController.generate_refresh_token') as mock_refresh, \
         patch('app.controllers.AuthController.get_hash') as mock_hash:
        
        mock_access.return_value = "test_access_token"
        mock_refresh.return_value = ("test_refresh_token", "test_jti", datetime.now(timezone.utc))
        mock_hash.return_value = b"hashed_token"
        
        result = create_token_response(mock_user, mock_session)
    
    assert isinstance(result, Token)
    assert result.access_token == "test_access_token"
    assert result.refresh_token == "test_refresh_token"
    
    mock_session.add.assert_called_once()
    added_token = mock_session.add.call_args[0][0]
    assert isinstance(added_token, RefreshToken)
    assert added_token.id_token == "test_jti"
    assert added_token.id_user == mock_user.id_user
    mock_session.commit.assert_called_once()

# Tests para utils/auth.py
@pytest.mark.asyncio
async def test_generate_access_token(mock_token_payload):
    # Usar fecha futura para el token
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    
    with patch('app.utils.auth.datetime') as mock_datetime:
        # Mockear now() para que devuelva una fecha anterior a la expiración
        mock_datetime.now.return_value = datetime.now(timezone.utc)
        # Mockear la fecha de expiración para que sea futura
        mock_datetime.side_effect = lambda *args, **kw: future_date if args == () else datetime(*args, **kw)
        
        token = generate_access_token(mock_token_payload)
        
        # Mockear now() durante la verificación también
        with patch('jwt.api_jwt.datetime') as jwt_datetime:
            jwt_datetime.now.return_value = datetime.now(timezone.utc)
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            assert decoded["sub"] == "testuser"
            assert decoded["email"] == "test@example.com"
            assert decoded["token_type"] == "access"

@pytest.mark.asyncio
async def test_generate_refresh_token(mock_token_payload):
    # Configurar tiempo actual mockeado
    current_time = datetime.now(timezone.utc)
    expected_expires_at = current_time + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    with patch('app.utils.auth.datetime') as mock_datetime, \
         patch('app.utils.auth.uuid.uuid4') as mock_uuid:
        
        # Configurar mocks
        mock_datetime.now.return_value = current_time
        mock_uuid.return_value = "mock-uuid"
        
        # Generar token
        token, jti, expires_at = generate_refresh_token(mock_token_payload)
        
        # Verificar fecha de expiración
        assert expires_at.replace(microsecond=0) == expected_expires_at.replace(microsecond=0)
        
        # Verificar token
        with patch('jwt.api_jwt.datetime') as jwt_datetime:
            jwt_datetime.now.return_value = current_time
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            assert decoded["sub"] == mock_token_payload["sub"]
            assert decoded["jti"] == "mock-uuid"
            assert jti == "mock-uuid"

@pytest.mark.asyncio
async def test_verify_token_by_type_success(mock_token_payload):
    token = jwt.encode(
        {**mock_token_payload, "token_type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    with patch('app.utils.auth.secret_key', SECRET_KEY), \
         patch('app.utils.auth.algorithm', ALGORITHM):
        
        payload = await verify_token_by_type(token, "access")
        assert payload["sub"] == "testuser"

@pytest.mark.asyncio
async def test_verify_token_by_type_wrong_type(mock_token_payload):
    token = jwt.encode(
        {**mock_token_payload, "token_type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    with patch('app.utils.auth.secret_key', SECRET_KEY), \
         patch('app.utils.auth.algorithm', ALGORITHM):
        
        with pytest.raises(HTTPException) as exc_info:
            await verify_token_by_type(token, "access")
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_verify_access_token_success(mock_token_payload):
    token = jwt.encode(
        {**mock_token_payload, "token_type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    with patch('app.utils.auth.secret_key', SECRET_KEY), \
         patch('app.utils.auth.algorithm', ALGORITHM):
        
        payload = await verify_access_token(token)
        assert payload["sub"] == "testuser"

@pytest.mark.asyncio
async def test_verify_refresh_token_success(mock_token_payload, mock_session):
    token = jwt.encode(
        {**mock_token_payload, "token_type": "refresh", "jti": "test-jti", 
         "exp": datetime.now(timezone.utc) + timedelta(days=7)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    mock_db_token = MagicMock()
    mock_db_token.token_hash = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    mock_db_token.expires_at = int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())
    mock_db_token.used = False
    mock_db_token.revoked = False
    
    mock_session.exec.return_value.first.return_value = mock_db_token
    
    with patch('app.utils.auth.secret_key', SECRET_KEY), \
         patch('app.utils.auth.algorithm', ALGORITHM):
        
        payload = await verify_refresh_token(token, mock_session)
        assert payload["sub"] == "testuser"
        assert mock_db_token.used is True
        mock_session.commit.assert_called_once()

# Tests para utils/hashing.py
def test_verify_password_correct():
    password = "testpassword"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "testpassword"
    wrong_password = "wrongpassword"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    assert verify_password(wrong_password, hashed) is False

def test_get_hash():
    password = "testpassword"
    hashed = get_hash(password)
    assert isinstance(hashed, bytes)
    assert bcrypt.checkpw(password.encode('utf-8'), hashed)


@pytest.mark.asyncio
async def test_get_current_user_success():
    token_payload = {
        "sub": TEST_USERNAME,
        "email": TEST_EMAIL,
        "token_type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    valid_token = jwt.encode(token_payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)

    mock_user = MagicMock()
    mock_user.username = TEST_USERNAME

    with patch('app.utils.auth.verify_access_token', new_callable=AsyncMock) as mock_verify, \
         patch('app.utils.auth.UserController.get_by_username', return_value=mock_user):
        
        mock_verify.return_value = token_payload
        mock_session = MagicMock(spec=Session)
        
        result = await get_current_user(valid_token, mock_session)
        
        assert result == mock_user
        mock_verify.assert_called_once_with(token=valid_token)
        UserController.get_by_username.assert_called_once_with(TEST_USERNAME, mock_session)

@pytest.mark.asyncio
async def test_get_admin_user_success():
    token_payload = {
        "sub": TEST_USERNAME,
        "email": TEST_EMAIL,
        "token_type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    valid_token = jwt.encode(token_payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)

    mock_admin_user = MagicMock()
    mock_admin_user.username = TEST_USERNAME
    mock_admin_user.is_admin = True

    with patch('app.utils.auth.verify_access_token', new_callable=AsyncMock) as mock_verify, \
         patch('app.utils.auth.UserController.get_by_username', return_value=mock_admin_user):
        
        mock_verify.return_value = token_payload
        mock_session = MagicMock(spec=Session)
        
        result = await get_admin_user(valid_token, mock_session)
        
        assert result == mock_admin_user
        mock_verify.assert_called_once_with(token=valid_token)
        UserController.get_by_username.assert_called_once_with(TEST_USERNAME, mock_session)

@pytest.mark.asyncio
async def test_get_refresh_username_success():
    token_payload = {
        "sub": TEST_USERNAME,
        "email": TEST_EMAIL,
        "jti": "test-jti",
        "token_type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    valid_refresh_token = jwt.encode(token_payload, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)

    with patch('app.utils.auth.verify_refresh_token', new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = token_payload
        mock_session = MagicMock(spec=Session)

        result = await get_refresh_username(valid_refresh_token, mock_session)

        assert result == TEST_USERNAME
        # Verificar los argumentos posicionales
        mock_verify.assert_called_once_with(valid_refresh_token, mock_session)