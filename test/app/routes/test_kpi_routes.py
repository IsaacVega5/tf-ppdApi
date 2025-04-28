import os
os.environ["DATABASE"] = "sqlite"
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from uuid import uuid4
from unittest.mock import patch
from sqlmodel import SQLModel, create_engine

test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

def get_test_session():
    from sqlmodel import Session
    with Session(test_engine) as session:
        yield session

with patch('app.db.engine', test_engine), patch('app.db.get_session', get_test_session):
    from app.main import app
    SQLModel.metadata.create_all(test_engine)

from app.models.Kpi import Kpi
from app.controllers import KpiController
from app.utils.auth import verify_access_token

@pytest.fixture(autouse=True)
def override_auth_dependency():
    # Override to bypass authentication
    app.dependency_overrides[verify_access_token] = lambda: True
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def get_mock_kpi(id_action=None, description=None):
    return Kpi(
        id_kpi=str(uuid4()),
        id_action=id_action or str(uuid4()),
        description=description or "Test KPI"
    )

def test_get_kpis_by_action(mocker, client):
    mock_data = [
        get_mock_kpi("action-1", "desc-1"),
        get_mock_kpi("action-1", "desc-2")
    ]
    mocker.patch.object(KpiController, "get_kpis_by_action", return_value=mock_data)
    response = client.get("/kpi/action/action-1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["id_action"] == "action-1"
    assert data[1]["id_action"] == "action-1"

def test_create_kpi(mocker, client):
    mock_kpi = get_mock_kpi("action-2", "desc-create")
    mocker.patch.object(KpiController, "create_kpi", return_value=mock_kpi)
    payload = {"id_action": "action-2", "description": "desc-create"}
    response = client.post("/kpi/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id_action"] == "action-2"
    assert data["description"] == "desc-create"

def test_update_kpi(mocker, client):
    mock_kpi = get_mock_kpi("action-3", "desc-updated")
    mocker.patch.object(KpiController, "update_kpi", return_value=mock_kpi)
    payload = {"id_kpi": mock_kpi.id_kpi, "id_action": "action-3", "description": "desc-updated"}
    response = client.put(f"/kpi/{mock_kpi.id_kpi}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "desc-updated"

def test_delete_kpi(mocker, client):
    mocker.patch.object(KpiController, "delete_kpi", return_value={"detail": "KPI deleted", "id": "kpi-1"})
    response = client.delete("/kpi/kpi-1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "KPI deleted"
