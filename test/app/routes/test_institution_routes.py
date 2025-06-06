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

from app.models.Institution import InstitutionCreate, InstitutionUpdate
from app.controllers import InstitutionController
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

def test_get_all_institutions(mocker, client):
  mock_data = [
      {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "Institution 1", "id_institution_type": 1},
      {"id_institution": "d4185081-2f8b-4714-8855-f48f9262c6c7", "institution_name": "Institution 2", "id_institution_type": 2},
  ]
  mocker.patch.object(InstitutionController, "get_all", return_value=mock_data)

  response = client.get("/institution/")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data
  
def test_get_institution_by_id(mocker, client):
  mock_data = {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "Institution 1", "id_institution_type": 1}
  mocker.patch.object(InstitutionController, "get_by_id", return_value=mock_data)

  response = client.get("/institution/68d5412b-29d7-40ef-b234-64a5f55b5497")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data

def test_get_institution_not_found(mocker, client):
  mocker.patch.object(InstitutionController, "get_by_id", return_value=None)

  response = client.get("/institution/aaa-bbb-ccc-ddd-eee-fff")

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert response.json() == {"detail": "Institution not found"}

def test_create_institution(mocker, client):
    new_data = InstitutionCreate(institution_name="New Institution", id_institution_type=2)
    created_data = {
        "id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497",
        "institution_name": "New Institution",
        "id_institution_type": 2
    }

    # Mockea el tipo de institución como si existiera
    mocker.patch.object(
        InstitutionTypeController, 
        "get_by_id", 
        return_value={"id_institution_type": 2, "type_name": "University"}
    )

    # Mockea la creación
    mocker.patch.object(
        InstitutionController, 
        "create_institution", 
        return_value=created_data
    )

    response = client.post("/institution/", json=new_data.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_data


def test_update_institution(mocker, client):
  updated_data = InstitutionUpdate(institution_name="Updated Institution")
  response_data = {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "Updated Institution", "id_institution_type": 2}
  
  mocker.patch.object(InstitutionController, "get_by_id", return_value=response_data)
  mocker.patch.object(InstitutionController, "update_institution", return_value=response_data)

  response = client.put("/institution/68d5412b-29d7-40ef-b234-64a5f55b5497", json=updated_data.model_dump(exclude_unset=True))

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == response_data