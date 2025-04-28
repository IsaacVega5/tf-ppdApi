import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
import os
from unittest.mock import patch
from sqlmodel import SQLModel, create_engine

os.environ["DATABASE"] = "sqlite"
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

def get_test_session():
    from sqlmodel import Session
    with Session(test_engine) as session:
        yield session

with patch('app.db.engine', test_engine), patch('app.db.get_session', get_test_session):
    from app.main import app
    SQLModel.metadata.create_all(test_engine)

from app.models import History
from app.models.History import HistoryBase
from app.utils.auth import verify_access_token
from uuid import uuid4
from app.controllers import HistoryController
import uuid
from datetime import datetime

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

@pytest.fixture(autouse=True)
def override_auth_dependency():
    app.dependency_overrides[verify_access_token] = lambda: True
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def get_mock_history():
    return History(
        id_history=str(uuid4()),
        id_variable='var1',
        id_report='rep1',
        date=datetime.now()
    )

def test_get_all_history(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_all", return_value=mock_data)
    response = client.get("/history/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_history_by_id(mocker, client):
    mock_history = get_mock_history()
    mocker.patch.object(HistoryController, "get_by_id", return_value=mock_history)
    response = client.get(f"/history/{mock_history.id_history}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_history"] == mock_history.id_history

def test_get_history_by_id_not_found(mocker, client):
    mocker.patch.object(HistoryController, "get_by_id", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found"))
    response = client.get("/history/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_create_history(mocker, client):
    payload = {"id_variable": "var1", "id_report": "rep1", "date": "2025-01-01T00:00:00"}
    mock_history = get_mock_history()
    mocker.patch.object(HistoryController, "create_history", return_value=mock_history)
    response = client.post("/history/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id_variable"] == "var1"
    assert "id_history" in response.json()

def test_update_history(mocker, client):
    payload = {"id_variable": "var1", "id_report": "rep1", "date": "2025-01-01T00:00:00"}
    mock_history = get_mock_history()
    mocker.patch.object(HistoryController, "update_history", return_value=mock_history)
    response = client.put(f"/history/{mock_history.id_history}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_variable"] == "var1"

def test_update_history_not_found(mocker, client):
    mocker.patch.object(HistoryController, "update_history", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found"))
    payload = {"id_variable": "var1", "id_report": "rep1", "date": "2025-01-01T00:00:00"}
    response = client.put("/history/non-existent-id", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_delete_history(mocker, client):
    mocker.patch.object(HistoryController, "delete_history", return_value={"detail": "History deleted", "id": "some-id"})
    response = client.delete("/history/some-id")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "History deleted"

def test_delete_history_not_found(mocker, client):
    mocker.patch.object(HistoryController, "delete_history", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found"))
    response = client.delete("/history/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_get_history_by_variable(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_by_variable", return_value=mock_data)
    response = client.get("/history/variable/var1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_history_by_report(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_by_report", return_value=mock_data)
    response = client.get("/history/report/rep1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_history_by_var_and_report(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_by_var_and_report", return_value=mock_data)
    response = client.get("/history/var-report/var1/rep1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_history_by_kpi(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_by_kpi", return_value=mock_data)
    response = client.get("/history/kpi/kpi1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_history_by_action(mocker, client):
    mock_data = [get_mock_history()]
    mocker.patch.object(HistoryController, "get_by_action", return_value=mock_data)
    response = client.get("/history/action/action1")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
