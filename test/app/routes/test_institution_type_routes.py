import pytest
from fastapi.testclient import TestClient
from fastapi import status
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

from app.models.InstitutionType import InstitutionTypeCreate, InstitutionTypeUpdate
from app.controllers import InstitutionTypeController
from app.utils.auth import get_admin_user

@pytest.fixture(autouse=True)
def override_admin_user():
    app.dependency_overrides[get_admin_user] = lambda: {
        "username": "test_admin",
        "is_admin": True
    }
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def test_get_all_institution_types(mocker, client):
    mock_data = [
        {"id_institution_type": 1, "institution_type": "University"},
        {"id_institution_type": 2, "institution_type": "College"}
    ]
    mocker.patch.object(InstitutionTypeController, "get_all", return_value=mock_data)

    response = client.get("/institution-type/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_data

def test_get_institution_type_by_id(mocker, client):
    mock_data = {"id_institution_type": 1, "institution_type": "University"}
    mocker.patch.object(InstitutionTypeController, "get_by_id", return_value=mock_data)

    response = client.get("/institution-type/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_data

def test_get_institution_type_not_found(mocker, client):
    mocker.patch.object(InstitutionTypeController, "get_by_id", return_value=None)

    response = client.get("/institution-type/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Institution type not found"}

def test_create_institution_type(mocker, client):
    new_data = InstitutionTypeCreate(institution_type="Technical School")  # Usando Pydantic
    created_data = {"id_institution_type": 3, "institution_type": "Technical School"}
    
    mocker.patch.object(InstitutionTypeController, "create_institution_type", return_value=created_data)

    response = client.post("/institution-type/", json=new_data.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_data

def test_delete_institution_type(mocker, client):
    mocker.patch.object(InstitutionTypeController, "delete_institution_type", return_value={"message": "Institution type deleted"})

    response = client.delete("/institution-type/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Institution type deleted"}

def test_update_institution_type(mocker, client):
    updated_data = InstitutionTypeUpdate(institution_type="Updated Institution")  # Usando Pydantic
    response_data = {"id_institution_type": 1, "institution_type": "Updated Institution"}
    
    mocker.patch.object(InstitutionTypeController, "update_institution_type", return_value=response_data)

    response = client.put("/institution-type/1", json=updated_data.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data

def test_reject_unauthenticated_user(client):
    app.dependency_overrides = {}

    response = client.get("/institution-type/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
