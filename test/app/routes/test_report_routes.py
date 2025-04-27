import pytest
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from uuid import uuid4
from app.main import app
from app.models.Report import Report
from app.controllers import ReportController
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

def get_mock_report(id_action=None):
    return Report(
        id_report=str(uuid4()),
        id_action=id_action or str(uuid4())
    )

def test_get_all_reports(mocker, client):
    mock_data = [
        get_mock_report("action-1"),
        get_mock_report("action-2")
    ]
    mocker.patch.object(ReportController, "get_all", return_value=mock_data)
    response = client.get("/report/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0]["id_action"] == "action-1"
    assert response.json()[1]["id_action"] == "action-2"

def test_get_report_by_id(mocker, client):
    mock_report = get_mock_report("action-1")
    mocker.patch.object(ReportController, "get_by_id", return_value=mock_report)
    response = client.get(f"/report/{mock_report.id_report}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_report"] == mock_report.id_report
    assert response.json()["id_action"] == "action-1"

def test_get_report_by_id_not_found(mocker, client):
    mocker.patch.object(ReportController, "get_by_id", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"))
    response = client.get("/report/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_create_report(mocker, client):
    payload = {"id_action": "action-1"}
    mock_report = get_mock_report("action-1")
    mocker.patch.object(ReportController, "create_report", return_value=mock_report)
    response = client.post("/report/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id_action"] == "action-1"
    assert "id_report" in response.json()

def test_update_report(mocker, client):
    payload = {"id_action": "updated-action"}
    mock_report = get_mock_report("updated-action")
    mocker.patch.object(ReportController, "update_report", return_value=mock_report)
    response = client.put(f"/report/{mock_report.id_report}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id_action"] == "updated-action"

def test_update_report_not_found(mocker, client):
    mocker.patch.object(ReportController, "update_report", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"))
    payload = {"id_action": "updated-action"}
    response = client.put("/report/non-existent-id", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()

def test_delete_report(mocker, client):
    mocker.patch.object(ReportController, "delete_report", return_value={"detail": "Report deleted", "id": "some-id"})
    response = client.delete("/report/some-id")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Report deleted"

def test_delete_report_not_found(mocker, client):
    mocker.patch.object(ReportController, "delete_report", side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"))
    response = client.delete("/report/non-existent-id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.text.lower()
