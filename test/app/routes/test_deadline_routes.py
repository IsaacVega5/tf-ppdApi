import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from uuid import uuid4
from app.main import app
from app.models.DeadLine import DeadLine
from app.controllers.DeadLineController import DeadLineController
from app.utils.auth import verify_access_token

@pytest.fixture(autouse=True)
def override_auth_dependency():
    # Override para bypassear la autenticación si aplica
    app.dependency_overrides[verify_access_token] = lambda: True
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

from datetime import datetime

def get_mock_deadline(id_action=None):
    return DeadLine(
        id_deadline=str(uuid4()),
        id_action=id_action or str(uuid4()),
        deadline_date=datetime(2025, 1, 1, 0, 0, 0),
        year=2025
    )
def test_get_all_deadlines(mocker, client):
    mock_data = [
        get_mock_deadline("action-1"),
        get_mock_deadline("action-2")
    ]
    mocker.patch.object(DeadLineController, "get_all", return_value=mock_data)
    response = client.get("/deadline/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["id_action"] == "action-1"
    assert response.json()[1]["id_action"] == "action-2"

def test_get_deadline_by_id(mocker, client):
    mock_deadline = get_mock_deadline("action-1")
    mocker.patch.object(DeadLineController, "get_by_id", return_value=mock_deadline)
    response = client.get(f"/deadline/{mock_deadline.id_deadline}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_deadline"] == mock_deadline.id_deadline
    assert response.json()["id_action"] == "action-1"

def test_get_deadline_by_id_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "get_by_id", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    response = client.get("/deadline/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_create_deadline(mocker, client):
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    mock_deadline = get_mock_deadline("action-1")
    mocker.patch.object(DeadLineController, "create_deadline", return_value=mock_deadline)
    response = client.post("/deadline/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id_action"] == "action-1"
    assert "id_deadline" in response.json()

def test_update_deadline(mocker, client):
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    mock_deadline = get_mock_deadline("action-1")
    mocker.patch.object(DeadLineController, "update_deadline", return_value=mock_deadline)
    response = client.put(f"/deadline/{mock_deadline.id_deadline}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_action"] == "action-1"

def test_update_deadline_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "update_deadline", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    response = client.put("/deadline/non-existent-id", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_delete_deadline(mocker, client):
    mocker.patch.object(DeadLineController, "delete_deadline", return_value={"detail": "Deadline deleted", "id": "1234-abcd"})
    response = client.delete("/deadline/1234-abcd")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Deadline deleted"

def test_delete_deadline_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "delete_deadline", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    response = client.delete("/deadline/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_get_deadline_by_id(mocker, client):
    mock_deadline = get_mock_deadline()
    mocker.patch.object(DeadLineController, "get_by_id", return_value=mock_deadline)
    response = client.get(f"/deadline/{mock_deadline.id_deadline}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_deadline"] == mock_deadline.id_deadline

def test_get_deadline_by_id_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "get_by_id", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    response = client.get("/deadline/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_create_deadline(mocker, client):
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    mock_deadline = get_mock_deadline("action-1")
    mocker.patch.object(DeadLineController, "create_deadline", return_value=mock_deadline)
    response = client.post("/deadline/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id_action"] == "action-1"
    assert "id_deadline" in response.json()

def test_update_deadline(mocker, client):
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    mock_deadline = get_mock_deadline("action-1")
    mocker.patch.object(DeadLineController, "update_deadline", return_value=mock_deadline)
    response = client.put(f"/deadline/{mock_deadline.id_deadline}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_action"] == "action-1"

def test_update_deadline_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "update_deadline", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    payload = {"deadline_date": "2025-01-01T00:00:00", "id_action": "action-1", "year": 2025}
    response = client.put("/deadline/non-existent-id", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_delete_deadline(mocker, client):
    mocker.patch.object(DeadLineController, "delete_deadline", return_value={"detail": "Deadline deleted", "id": "some-id"})
    response = client.delete("/deadline/some-id")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Deadline deleted"

def test_delete_deadline_not_found(mocker, client):
    mocker.patch.object(DeadLineController, "delete_deadline", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found"))
    response = client.delete("/deadline/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()
