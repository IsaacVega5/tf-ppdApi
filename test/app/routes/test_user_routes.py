import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controllers import UserController
from app.models.User import UserCreate, UserLogin

@pytest.fixture
def client():
    return TestClient(app)

def test_get_users(mocker, client):
    mock_users = [
        {"id": 1, "username": "John Doe", "email": "john@example.com"},
        {"id": 2, "username": "Jane Doe", "email": "jane@example.com"},
    ]
    mocker.patch.object(UserController, "get_all", return_value=mock_users)

    response = client.get("/user/")
    
    assert response.status_code == 200
    assert response.json() == mock_users

def test_get_user_by_id(mocker, client):
    mock_user = {"id": 1, "username": "John Doe", "email": "john@example.com"}
    mocker.patch.object(UserController, "get_by_id", return_value=mock_user)

    response = client.get("/user/1")

    assert response.status_code == 200
    assert response.json() == mock_user

def test_get_user_not_found(mocker, client):
    mocker.patch.object(UserController, "get_by_id", return_value=None)

    response = client.get("/user/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user(mocker, client):
    new_user = UserCreate(username="Alice", email="alice@example.com", password="securepassword")  # Usando Pydantic
    created_user = {"id": 3, "username": "Alice", "email": "alice@example.com"}
    
    mocker.patch.object(UserController, "create_user", return_value=created_user)

    response = client.post("/user/", json=new_user.model_dump())  # Convertimos Pydantic a JSON

    assert response.status_code == 200
    assert response.json() == created_user

def test_delete_user(mocker, client):
    mocker.patch.object(UserController, "delete_user", return_value={"message": "User deleted"})

    response = client.delete("/user/1")

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted"}

def test_login_success(mocker, client):
    login_data = UserLogin(email="john@example.com", password="securepassword")  # Usando Pydantic
    login_response = {"token": "valid_token"}
    
    mocker.patch.object(UserController, "login", return_value=login_response)

    response = client.post("/user/login", json=login_data.model_dump())

    assert response.status_code == 200
    assert response.json() == login_response

def test_login_failed(mocker, client):
    login_data = UserLogin(email="john@example.com", password="wrongpassword")  # Usando Pydantic
    
    mocker.patch.object(UserController, "login", return_value={"error": "Invalid credentials"})

    response = client.post("/user/login", json=login_data.model_dump())

    assert response.status_code == 200
    assert response.json() == {"error": "Invalid credentials"}
