import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.controllers import ActionTypeController, InstitutionTypeController
from app.models.ActionType import ActionType, ActionTypeCreate, ActionTypeUpdate
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

def test_get_all_action_types(mocker, client):
  mock_data = [
    {"id_action_type": 1, "action_type": "Type A"},
    {"id_action_type": 2, "action_type": "Type B"}
  ]
  mocker.patch.object(ActionTypeController, "get_all", return_value=mock_data)

  response = client.get("/action-type/")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data

def test_get_action_type_by_id(mocker, client):
  mock_data = {"id_action_type": 1, "action_type": "Type A"}
  mocker.patch.object(ActionTypeController, "get_by_id", return_value=mock_data)

  response = client.get("/action-type/1")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data

def test_get_action_type_not_found(mocker, client):
  mocker.patch.object(ActionTypeController, "get_by_id", return_value=None)
  response = client.get("/action-type/999")

  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert response.json() == {"detail": "Action type not found"}

def test_create_action_type(mocker, client):
  mock_data = {"id_action_type": 1, "action_type": "Type A"}
  new_data = ActionTypeCreate(action_type="Type A") 
  
  mocker.patch.object(ActionTypeController, "create_action_type", return_value=mock_data)
  response = client.post("/action-type/", json=new_data.model_dump())

  assert response.status_code == status.HTTP_201_CREATED
  assert response.json() == mock_data

def test_update_action_type(mocker, client):
  mock_data = {"id_action_type": 1, "action_type": "Updated Type"}
  updated_data = ActionTypeUpdate(action_type="Updated Type")
  mocker.patch.object(ActionTypeController, "update_action_type", return_value=mock_data)

  response = client.put("/action-type/1", json=updated_data.model_dump())

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data

def test_delete_action_type(mocker, client):
  mocker.patch.object(ActionTypeController, "delete_action_type", return_value={"message": "Action type deleted"})

  response = client.delete("/action-type/1")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {"message": "Action type deleted"}