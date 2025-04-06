import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.controllers import PpdaController
from app.models.Ppda import PpdaCreate, PpdaUpdate
from app.models import Ppda

@pytest.fixture
def client():
  return TestClient(app)

def test_get_all_ppda(mocker, client):
  mock_data = [
      {"id_ppda": "68d5412b-29d7-40ef-b234-64a5f55b5497", "id_institution": "Institution 1"},
      {"id_ppda": "d4185081-2f8b-4714-8855-f48f9262c6c7", "id_institution": "Institution 2"},
  ]
  mocker.patch.object(PpdaController, "get_all", return_value=mock_data)

  response = client.get("/ppda/")

  assert response.status_code == 200
  assert response.json() == mock_data

def test_get_ppda_by_id(mocker, client):
  mock_data = {"id_ppda": "68d5412b-29d7-40ef-b234-64a5f55b5497", "id_institution": "Institution 1"}
  mocker.patch.object(PpdaController, "get_by_id", return_value=mock_data)

  response = client.get("/ppda/68d5412b-29d7-40ef-b234-64a5f55b5497")

  assert response.status_code == 200
  assert response.json() == mock_data

def test_get_ppda_not_found(mocker, client):
  mocker.patch.object(PpdaController, "get_by_id", return_value=None)

  response = client.get("/ppda/aaa-bbb-ccc-ddd-eee-fff")

  assert response.status_code == 404
  assert response.json() == {"detail": "Ppda not found"}

def test_create_ppda(mocker, client):
  new_data = PpdaCreate(id_institution="New Institution")
  created_data = {"id_ppda": "68d5412b-29d7-40ef-b234-64a5f55b5497", "id_institution": "New Institution"}
  mocker.patch.object(PpdaController, "create_ppda", return_value=created_data)

  response = client.post("/ppda/", json=new_data.model_dump())

  assert response.status_code == 200
  assert response.json() == created_data

def test_update_ppda(mocker, client):
  updated_data = PpdaUpdate(id_institution="Updated Institution")
  response_data = {"id_ppda": "68d5412b-29d7-40ef-b234-64a5f55b5497", "id_institution": "Updated Institution"}
  
  mocker.patch.object(PpdaController, "get_by_id", return_value=response_data)
  mocker.patch.object(PpdaController, "update_ppda", return_value=response_data)

  response = client.put("/ppda/68d5412b-29d7-40ef-b234-64a5f55b5497", json=updated_data.model_dump(exclude_unset=True))

  assert response.status_code == 200
  assert response.json() == response_data

def test_update_ppda_not_found(mocker, client):
  updated_data = PpdaUpdate(id_institution="Updated Institution")
  mocker.patch.object(PpdaController, "get_by_id", return_value=None)

  response = client.put("/ppda/aaa-bbb-ccc-ddd-eee-fff", json=updated_data.model_dump(exclude_unset=True))

  assert response.status_code == 404
  assert response.json() == {"detail": "Ppda not found"}

def test_delete_ppda(mocker, client):
  mocker.patch.object(PpdaController, "delete_ppda", return_value={"detail": "Ppda deleted"})

  response = client.delete("/ppda/68d5412b-29d7-40ef-b234-64a5f55b5497")

  assert response.status_code == 200
  assert response.json() == {"detail": "Ppda deleted"}

def test_delete_ppda_not_found(mocker, client):
  mocker.patch.object(PpdaController, "delete_ppda", return_value=None)

  response = client.delete("/ppda/aaa-bbb-ccc-ddd-eee-fff")

  assert response.status_code == 404
  assert response.json() == {"detail": "Ppda not found"}