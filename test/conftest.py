import os
import pytest
from unittest.mock import patch
from sqlmodel import SQLModel, create_engine, Session

# Parcheo global para tests de rutas: SQLite en memoria
os.environ["DATABASE"] = "sqlite"
test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

# Fixture global para parchear engine y get_session en todos los tests de rutas
@pytest.fixture(autouse=True, scope="session")
def patch_engine_and_session():
    def get_test_session():
        with Session(test_engine) as session:
            yield session
    with patch("app.db.engine", test_engine), patch("app.db.get_session", get_test_session):
        SQLModel.metadata.create_all(test_engine)
        yield  # Todos los tests usan este contexto
        SQLModel.metadata.drop_all(test_engine)
