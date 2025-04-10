import pytest
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime
from uuid import uuid4
from app.main import app
from app.controllers import PpdaController, InstitutionController
from app.models.Ppda import PpdaCreate, PpdaUpdate, Ppda
from app.utils.auth import verify_access_token

@pytest.fixture(autouse=True)
def override_auth_dependency():
    # Override para bypassear la autenticación
    app.dependency_overrides[verify_access_token] = lambda: True
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    return TestClient(app)

def get_mock_ppda(id_institution=None):
    now = datetime.now().isoformat()
    return Ppda(
        id_ppda=str(uuid4()),
        id_institution=id_institution or str(uuid4()),
        created_at=now,
        updated_at=now
    )

def test_get_all_ppda(mocker, client):
    mock_data = [
        get_mock_ppda("68d5412b-29d7-40ef-b234-64a5f55b5497"),
        get_mock_ppda("d4185081-2f8b-4714-8855-f48f9262c6c7")
    ]
    mocker.patch.object(PpdaController, "get_all", return_value=mock_data)

    response = client.get("/ppda/")

    assert response.status_code == status.HTTP_200_OK
    # Convertimos los modelos a dict para la comparación
    assert response.json() == [item.model_dump() for item in mock_data]

def test_get_ppda_by_id(mocker, client):
    mock_data = get_mock_ppda("68d5412b-29d7-40ef-b234-64a5f55b5497")
    mocker.patch.object(PpdaController, "get_by_id", return_value=mock_data)

    response = client.get(f"/ppda/{mock_data.id_ppda}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_data.model_dump()

def test_get_ppda_not_found(mocker, client):
    mocker.patch.object(PpdaController, "get_by_id", return_value=None)

    response = client.get(f"/ppda/{str(uuid4())}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Ppda not found"}

def test_create_ppda(mocker, client):
    institution_id = str(uuid4())
    new_data = PpdaCreate(id_institution=institution_id)
    
    # Mock para verificar que existe la institución
    mocker.patch.object(
        InstitutionController, 
        "get_by_id", 
        return_value={"id_institution": institution_id}
    )
    
    created_data = get_mock_ppda(institution_id)
    mocker.patch.object(PpdaController, "create_ppda", return_value=created_data)

    response = client.post("/ppda/", json=new_data.model_dump())

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created_data.model_dump()

def test_create_ppda_institution_not_found(mocker, client):
    institution_id = str(uuid4())
    new_data = PpdaCreate(id_institution=institution_id)
    
    # Mock para simular que no existe la institución
    mocker.patch.object(InstitutionController, "get_by_id", return_value=None)

    response = client.post("/ppda/", json=new_data.model_dump())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Institution not found"}

def test_update_ppda(mocker, client):
    ppda_id = str(uuid4())
    institution_id = str(uuid4())
    
    updated_data = PpdaUpdate(id_institution=institution_id)
    response_data = get_mock_ppda(institution_id)
    response_data.id_ppda = ppda_id
    
    # Mocks para las verificaciones
    mocker.patch.object(
        PpdaController, 
        "get_by_id", 
        return_value=response_data
    )
    mocker.patch.object(
        InstitutionController,
        "get_by_id",
        return_value={"id_institution": institution_id}
    )
    mocker.patch.object(
        PpdaController, 
        "update_ppda", 
        return_value=response_data
    )

    response = client.put(
        f"/ppda/{ppda_id}", 
        json=updated_data.model_dump(exclude_unset=True)
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == response_data.model_dump()

def test_update_ppda_not_found(mocker, client):
    ppda_id = str(uuid4())
    updated_data = PpdaUpdate(id_institution=str(uuid4()))
    
    mocker.patch.object(PpdaController, "get_by_id", return_value=None)

    response = client.put(
        f"/ppda/{ppda_id}", 
        json=updated_data.model_dump(exclude_unset=True)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Ppda not found"}

def test_update_ppda_institution_not_found(mocker, client):
    ppda_id = str(uuid4())
    institution_id = str(uuid4())
    
    # Mock para ppda existente (usamos el modelo real)
    existing_ppda = get_mock_ppda("old_institution")
    existing_ppda.id_ppda = ppda_id
    mocker.patch.object(
        PpdaController, 
        "get_by_id", 
        return_value=existing_ppda
    )
    # Mock para institución no encontrada
    mocker.patch.object(InstitutionController, "get_by_id", return_value=None)

    updated_data = PpdaUpdate(id_institution=institution_id)
    response = client.put(
        f"/ppda/{ppda_id}", 
        json=updated_data.model_dump(exclude_unset=True)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Institution not found"}

def test_delete_ppda(mocker, client):
    ppda_id = str(uuid4())
    ppda_data = get_mock_ppda()
    ppda_data.id_ppda = ppda_id
    
    mocker.patch.object(
        PpdaController, 
        "get_by_id", 
        return_value=ppda_data
    )
    mocker.patch.object(
        PpdaController, 
        "delete_ppda", 
        return_value={"detail": "Ppda deleted"}
    )

    response = client.delete(f"/ppda/{ppda_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Ppda deleted"}

def test_delete_ppda_not_found(mocker, client):
    ppda_id = str(uuid4())
    mocker.patch.object(PpdaController, "get_by_id", return_value=None)

    response = client.delete(f"/ppda/{ppda_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Ppda not found"}