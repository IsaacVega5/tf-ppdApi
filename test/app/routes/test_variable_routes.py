import os
os.environ["DATABASE"] = "sqlite"
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

from app.models import Variable
from app.models.Variable import VariableBase
from app.controllers import VariableController, KpiController
from app.utils.auth import verify_access_token, get_admin_user
from uuid import uuid4

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    yield

@pytest.fixture(autouse=True)
def override_auth_dependency():
    # Override to bypass authentication
    app.dependency_overrides[verify_access_token] = lambda: True
    app.dependency_overrides[get_admin_user] = lambda: {"sub": "admin-user"}
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def get_mock_variable(id_kpi=None, formula=None, verification_medium=None):
    return Variable(
        id_variable=str(uuid4()),
        id_kpi=id_kpi or str(uuid4()),
        formula=formula or "Test Formula",
        verification_medium=verification_medium or "Test Medium"
    )

def test_get_all_variables(mocker, client):
    mock_data = [
        get_mock_variable("kpi-1", "formula-1", "medium-1"),
        get_mock_variable("kpi-2", "formula-2", "medium-2")
    ]
    mocker.patch.object(VariableController, "get_all_variables", return_value=mock_data)
    response = client.get("/variable/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["formula"] == "formula-1"
    assert data[1]["formula"] == "formula-2"

def test_get_variable_by_id(mocker, client):
    mock_variable = get_mock_variable("kpi-1", "formula-1", "medium-1")
    mocker.patch.object(VariableController, "get_variable_by_id", return_value=mock_variable)
    response = client.get(f"/variable/{mock_variable.id_variable}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id_variable"] == mock_variable.id_variable
    assert data["formula"] == "formula-1"
    assert data["verification_medium"] == "medium-1"

def test_create_variable(mocker, client):
    mock_variable = get_mock_variable("kpi-2", "formula-create", "medium-create")
    mocker.patch.object(VariableController, "create_variable", return_value=mock_variable)
    mocker.patch.object(KpiController, "get_kpi_by_id", return_value=True)  # Mock KPI validation
    
    payload = {
        "id_kpi": "kpi-2", 
        "formula": "formula-create", 
        "verification_medium": "medium-create"
    }
    response = client.post("/variable/", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id_kpi"] == "kpi-2"
    assert data["formula"] == "formula-create"
    assert data["verification_medium"] == "medium-create"

def test_update_variable(mocker, client):
    mock_variable = get_mock_variable("kpi-3", "formula-updated", "medium-updated")
    mocker.patch.object(VariableController, "update_variable", return_value=mock_variable)
    mocker.patch.object(KpiController, "get_kpi_by_id", return_value=True)  # Mock KPI validation
    
    payload = {
        "id_kpi": "kpi-3", 
        "formula": "formula-updated", 
        "verification_medium": "medium-updated"
    }
    response = client.put(f"/variable/{mock_variable.id_variable}", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["formula"] == "formula-updated"
    assert data["verification_medium"] == "medium-updated"

def test_delete_variable(mocker, client):
    variable_id = str(uuid4())
    mocker.patch.object(VariableController, "delete_variable", 
                        return_value={"detail": "Variable deleted", "id": variable_id})
    
    response = client.delete(f"/variable/{variable_id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Variable deleted"
    assert response.json()["id"] == variable_id

def test_get_variables_by_kpi(mocker, client):
    kpi_id = str(uuid4())
    mock_data = [
        get_mock_variable(kpi_id, "formula-a", "medium-a"),
        get_mock_variable(kpi_id, "formula-b", "medium-b")
    ]
    
    mocker.patch.object(VariableController, "get_variables_by_kpi", return_value=mock_data)
    mocker.patch.object(KpiController, "get_kpi_by_id", return_value=True)  # Mock KPI validation
    
    response = client.get(f"/variable/kpi/{kpi_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["id_kpi"] == kpi_id
    assert data[1]["id_kpi"] == kpi_id

def test_create_variable_invalid_kpi(mocker, client):
    mocker.patch.object(KpiController, "get_kpi_by_id", side_effect=HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="KPI not found"))
    
    payload = {
        "id_kpi": "invalid-kpi", 
        "formula": "formula-test", 
        "verification_medium": "medium-test"
    }
    response = client.post("/variable/", json=payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "KPI not found"
