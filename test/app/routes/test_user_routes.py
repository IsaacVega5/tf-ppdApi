import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
from app.main import app
from app.controllers import UserController
from app.models.User import UserCreate
from app.utils.auth import get_admin_user, get_current_user
from uuid import uuid4

@pytest.fixture(autouse=True)
def override_auth_dependencies():
    app.dependency_overrides[get_admin_user] = lambda: {
        "id_user": str(uuid4()),
        "username": "test_admin",
        "email": "admin@example.com",
        "is_admin": True,
        "created_at": int(datetime.now().timestamp()),
        "updated_at": int(datetime.now().timestamp())
    }
    app.dependency_overrides[get_current_user] = lambda: {
        "id_user": str(uuid4()),
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False,
        "created_at": int(datetime.now().timestamp()),
        "updated_at": int(datetime.now().timestamp())
    }
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def get_mock_user(id=1):
    return {
        "id_user": str(uuid4()),
        "username": f"User {id}",
        "email": f"user{id}@example.com",
        "is_admin": False,
        "created_at": int(datetime.now().timestamp()),
        "updated_at": int(datetime.now().timestamp())
    }

def test_get_users(mocker, client):
    mock_users = [
        get_mock_user(1),
        get_mock_user(2)
    ]
    mocker.patch.object(UserController, "get_all", return_value=mock_users)

    response = client.get("/user/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_users

def test_get_user_by_id(mocker, client):
    mock_user = get_mock_user(1)
    mocker.patch.object(UserController, "get_by_id", return_value=mock_user)

    response = client.get(f"/user/{mock_user['id_user']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_user

def test_get_user_not_found(mocker, client):
    mocker.patch.object(UserController, "get_by_id", return_value=None)

    response = client.get(f"/user/{str(uuid4())}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}

def test_create_user(mocker, client):
    new_user = UserCreate(
        username="Alice",
        email="alice@example.com",
        password="securepassword"
    )
    created_user = get_mock_user(3)
    created_user.update({
        "username": "Alice",
        "email": "alice@example.com"
    })
    
    mocker.patch.object(UserController, "create_user", return_value=created_user)

    response = client.post("/user/", json=new_user.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_user

def test_delete_user(mocker, client):
    user_id = str(uuid4())
    mocker.patch.object(
        UserController, 
        "delete_user", 
        return_value={"message": "User deleted"}
    )

    response = client.delete(f"/user/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "User deleted"}

def test_get_user_me(client):
    response = client.get("/user/me")
    
    expected_keys = {"id_user", "username", "email", "is_admin", "created_at", "updated_at"}
    assert response.status_code == status.HTTP_200_OK
    assert all(key in response.json() for key in expected_keys)