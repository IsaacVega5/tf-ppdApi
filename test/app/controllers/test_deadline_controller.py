import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers.DeadLineController import DeadLineController
from app.models.DeadLine import DeadLineBase
from fastapi import HTTPException, status
from datetime import datetime
import uuid

# Configuración de base de datos en memoria
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def sample_deadline(id_action=None, year=2025, deadline_date=None):
    return DeadLineBase(
        id_action=id_action or str(uuid.uuid4()),
        year=year,
        deadline_date=deadline_date or datetime(2025, 1, 1, 0, 0, 0)
    )

@pytest.mark.asyncio
async def test_create_and_get_deadline(session):
    data = sample_deadline("action-1")
    deadline = await DeadLineController.create_deadline(data, session)
    assert deadline.id_action == "action-1"
    fetched = await DeadLineController.get_by_id(deadline.id_deadline, session)
    assert fetched.id_deadline == deadline.id_deadline
    assert fetched.id_action == "action-1"

@pytest.mark.asyncio
async def test_update_deadline(session):
    data = sample_deadline("action-1")
    deadline = await DeadLineController.create_deadline(data, session)
    update_data = DeadLineBase(id_action="updated-action", year=2026, deadline_date=datetime(2026, 1, 1, 0, 0, 0))
    updated = await DeadLineController.update_deadline(deadline.id_deadline, update_data, session)
    assert updated.id_action == "updated-action"
    assert updated.year == 2026
    assert str(updated.deadline_date).startswith("2026-01-01")

@pytest.mark.asyncio
async def test_delete_deadline(session):
    data = sample_deadline("action-1")
    deadline = await DeadLineController.create_deadline(data, session)
    resp = await DeadLineController.delete_deadline(deadline.id_deadline, session)
    assert resp["detail"] == "Deadline deleted"
    with pytest.raises(HTTPException):
        await DeadLineController.get_by_id(deadline.id_deadline, session)

@pytest.mark.asyncio
async def test_get_deadline_not_found(session):
    with pytest.raises(HTTPException) as excinfo:
        await DeadLineController.get_by_id("non-existent-id", session)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_deadline_not_found(session):
    update_data = DeadLineBase(id_action="updated", year=2027, deadline_date=datetime(2027, 1, 1, 0, 0, 0))
    with pytest.raises(HTTPException) as excinfo:
        await DeadLineController.update_deadline("non-existent-id", update_data, session)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_deadline_not_found(session):
    with pytest.raises(HTTPException) as excinfo:
        await DeadLineController.delete_deadline("non-existent-id", session)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_deadlines(session):
    d1 = await DeadLineController.create_deadline(sample_deadline("a1"), session)
    d2 = await DeadLineController.create_deadline(sample_deadline("a2"), session)
    deadlines = await DeadLineController.get_all(session)
    ids = [d.id_deadline for d in deadlines]
    assert d1.id_deadline in ids and d2.id_deadline in ids
    assert len(deadlines) == 2
