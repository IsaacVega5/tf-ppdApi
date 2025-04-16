import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.models import User
from app.models.Auth import AuthTokenResponse
from app.controllers import AuthController
import uuid
from datetime import datetime

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_user(session):
    user = User(
        id_user=str(uuid.uuid4()),
        username="test_user",
        email="test@example.com",
        password="hashed_password",
        is_admin=False
    )
    session.add(user)
    session.commit()
    return user

@pytest.mark.asyncio
async def test_login_success(test_client, sample_user):
    login_data = {
        "username": sample_user.username,
        "password": "valid_password"
    }
    
    with patch("app.controllers.AuthController.login") as mock_login:
        mock_login.return_value = {
            "access_token": "mock_access",
            "refresh_token": "mock_refresh",
            "token_type": "bearer"
        }
        response = test_client.post("/auth/token", data=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_refresh_token_success(test_client, sample_user):
    with patch("app.utils.auth.verify_refresh_token", return_value={"sub": sample_user.username}):
        with patch("app.controllers.AuthController.refresh_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_token",
                "refresh_token": "new_refresh",
                "token_type": "bearer"
            }
        
            response = test_client.post(
                "/auth/refresh-token",
                headers={"Authorization": "Bearer valid_token"}
            )
        
            assert response.status_code == status.HTTP_200_OK

def test_create_token_response(session, sample_user):
    with patch("app.controllers.AuthController.generate_access_token", return_value="access_mock"):
        with patch("app.controllers.AuthController.generate_refresh_token") as mock_refresh:
            mock_refresh.return_value = ("refresh_mock", "jti_mock", datetime.now())
            
            result = AuthController.create_token_response(sample_user, session)
            
            assert isinstance(result, AuthTokenResponse)
            assert result.access_token == "access_mock"
            assert result.refresh_token == "refresh_mock"
            assert result.token_type == "bearer"