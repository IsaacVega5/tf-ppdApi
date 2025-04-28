import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from app.main import app
from app.controllers import ActionController, PpdaController
from app.models.Action import *
from app.models import Ppda, User
from app.utils.auth import get_admin_user, get_current_user

@pytest.fixture(autouse=True)
def override_admin_user():
    app.dependency_overrides[get_admin_user] = lambda: {
        "username": "test_admin",
        "is_admin": True
    }
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def override_current_user():
    app.dependency_overrides[get_current_user] = lambda: User(
        id_user="uuid_user_1",
        username="test_user",
        email="test@test.tes",
        is_admin=True,
    )
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
  return TestClient(app)

def test_get_all_actions(mocker, client):
  mock_data = [
    {"id_action" : "uuid_action_1", "id_action_type": 1, "id_ppda": "uuid_ppda_1", "id_user": "uuid_user_1"},
    {"id_action" : "uuid_action_2", "id_action_type": 2, "id_ppda": "uuid_ppda_2", "id_user": "uuid_user_2"}
  ]
  mocker.patch.object(ActionController, "get_all", return_value=mock_data)

  response = client.get("/action/")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data

def test_get_action_by_id(mocker, client):
  mock_data_action = {"id_action" : "uuid_action_1", "id_action_type": 1, "id_ppda": "uuid_ppda_1", "id_user": "uuid_user_1"}
  mock_data_ppda = {"id_ppda": "uuid_ppda_1", "id_institution": "uuid_institution_1"}
  
  mocker.patch.object(ActionController, "get_by_id", return_value=Action(**mock_data_action))
  mocker.patch.object(PpdaController, "get_by_id", return_value=Ppda(**mock_data_ppda))
  mocker.patch("app.utils.rbac.verify_institution_role", return_value=True)
  
  response = client.get("/action/uuid_action_1")
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data_action

def test_create_action(mocker, client):
  new_data = {"id_action" : "uuid_action_1", "id_action_type": 1, "id_ppda": "uuid_ppda_1", "id_user": "uuid_user_1"}
  mocker.patch.object(PpdaController, "get_by_id", return_value=Ppda(**{"id_ppda": "uuid_ppda_1", "id_institution": "uuid_institution_1"}))
  mocker.patch.object(ActionController, "create_action", return_value=new_data)

  response = client.post("/action/", json=new_data)

  assert response.status_code == status.HTTP_201_CREATED
  assert response.json() == new_data

def test_update_action(mocker, client):
  mock_data_action = {"id_action" : "uuid_action_1", "id_action_type": 1, "id_ppda": "uuid_ppda_1", "id_user": "uuid_user_1"}
  mock_data_ppda = {"id_ppda": "uuid_ppda_1", "id_institution": "uuid_institution_1"}
  
  updated_data = ActionUpdate(id_ppda="uuid_ppda_1", id_action_type=1, id_user="uuid_user_1")
  
  mocker.patch.object(ActionController, "get_by_id", return_value=Action(**mock_data_action))
  mocker.patch.object(PpdaController, "get_by_id", return_value=Ppda(**mock_data_ppda))
  mocker.patch("app.utils.rbac.verify_institution_role", return_value=True)
  
  mocker.patch.object(ActionController, "update_action", return_value=Action(**mock_data_action))
  
  response = client.put("/action/1", json=updated_data.model_dump())

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data_action

def test_delete_action(mocker, client):
  mock_data = {"id_action" : "uuid_action_1", "id_action_type": 1, "id_ppda": "uuid_ppda_1", "id_user": "uuid_user_1"}
  mock_data_ppda = {"id_ppda": "uuid_ppda_1", "id_institution": "uuid_institution_1"}
  
  mocker.patch.object(ActionController, "get_by_id", return_value=Action(**mock_data))
  mocker.patch.object(PpdaController, "get_by_id", return_value=Ppda(**mock_data_ppda))
  
  mocker.patch.object(ActionController, "delete_action", return_value={"message": "Action uuid_action_1 deleted"})
  
  response = client.delete("/action/uuid_action_1")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {"message": "Action uuid_action_1 deleted"}

def test_get_actions_pubic(mocker, client):
  mock_data = [
    {"id_ppda": "uuid_ppda_1", "action_type": "Type A"},
    {"id_ppda": "uuid_ppda_2", "action_type": "Type B"}
  ]
  mocker.patch.object(ActionController, "get_all_public", return_value=mock_data)

  response = client.get("/action/public/")

  assert response.status_code == status.HTTP_200_OK
  assert response.json() == mock_data
