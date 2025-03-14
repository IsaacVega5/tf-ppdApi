from fastapi.testclient import TestClient
from app import main
from fastapi import status

client = TestClient(main.app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "You should not be seeing this"}