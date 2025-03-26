import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controllers import InstitutionController
from app.models.Institution import InstitutionCreate, InstitutionUpdate

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

  assert response.status_code == 200
  assert response.json() == mock_data
  
def test_get_institution_by_id(mocker, client):
  mock_data = {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "Institution 1", "id_institution_type": 1}
  mocker.patch.object(InstitutionController, "get_by_id", return_value=mock_data)

  response = client.get("/institution/68d5412b-29d7-40ef-b234-64a5f55b5497")

  assert response.status_code == 200
  assert response.json() == mock_data

def test_get_institution_not_found(mocker, client):
  mocker.patch.object(InstitutionController, "get_by_id", return_value=None)

  response = client.get("/institution/aaa-bbb-ccc-ddd-eee-fff")

  assert response.status_code == 404
  assert response.json() == {"detail": "Institution not found"}

def test_create_institution(mocker, client):
  new_data = InstitutionCreate(institution_name="New Institution", id_institution_type=2)
  created_data = {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "New Institution", "id_institution_type": 2}
  mocker.patch.object(InstitutionController, "create_institution", return_value=created_data)

  response = client.post("/institution/", json=new_data.model_dump())

  assert response.status_code == 200
  assert response.json() == created_data

def test_update_institution(mocker, client):
  updated_data = InstitutionUpdate(institution_name="Updated Institution")
  response_data = {"id_institution": "68d5412b-29d7-40ef-b234-64a5f55b5497", "institution_name": "Updated Institution", "id_institution_type": 2}
  
  mocker.patch.object(InstitutionController, "get_by_id", return_value=response_data)
  mocker.patch.object(InstitutionController, "update_institution", return_value=response_data)

  response = client.put("/institution/68d5412b-29d7-40ef-b234-64a5f55b5497", json=updated_data.model_dump(exclude_unset=True))

  assert response.status_code == 200
  assert response.json() == response_data