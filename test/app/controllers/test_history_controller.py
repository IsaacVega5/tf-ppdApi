import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers import HistoryController
from app.models.History import HistoryBase
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

def sample_history(id_variable=None, id_report=None, created_at=None):
    return HistoryBase(
        id_variable=id_variable or str(uuid.uuid4()),
        id_report=id_report or str(uuid.uuid4()),
        created_at=created_at or int(datetime(2025, 1, 1, 0, 0, 0).timestamp())
    )

@pytest.mark.asyncio
async def test_create_and_get_history(session):
    data = sample_history("var-1", "rep-1")
    history = await HistoryController.create_history(data, session)
    assert history.id_variable == "var-1"
    fetched = await HistoryController.get_by_id(history.id_history, session)
    assert fetched.id_history == history.id_history
    assert fetched.id_variable == "var-1"
    assert fetched.id_report == "rep-1"

@pytest.mark.asyncio
async def test_update_history(session):
    data = sample_history("var-1", "rep-1")
    history = await HistoryController.create_history(data, session)
    update_data = sample_history("updated-var", "updated-rep", int(datetime(2026, 1, 1, 0, 0, 0).timestamp()))
    updated = await HistoryController.update_history(history.id_history, update_data, session)
    assert updated.id_variable == "updated-var"
    assert updated.id_report == "updated-rep"
    assert updated.created_at == int(datetime(2026, 1, 1, 0, 0, 0).timestamp())

@pytest.mark.asyncio
async def test_delete_history(session):
    data = sample_history("var-1", "rep-1")
    history = await HistoryController.create_history(data, session)
    deleted = await HistoryController.delete_history(history.id_history, session)
    assert deleted["detail"] == "History deleted"
    assert deleted["id"] == history.id_history
    with pytest.raises(HTTPException) as exc:
        await HistoryController.get_by_id(history.id_history, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_history_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await HistoryController.get_by_id("non-existent-id", session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_update_history_not_found(session):
    update_data = sample_history("var-1", "rep-1")
    with pytest.raises(HTTPException) as exc:
        await HistoryController.update_history("non-existent-id", update_data, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_history_not_found(session):
    with pytest.raises(HTTPException) as exc:
        await HistoryController.delete_history("non-existent-id", session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_histories(session):
    data1 = sample_history("var-1", "rep-1")
    data2 = sample_history("var-2", "rep-2")
    await HistoryController.create_history(data1, session)
    await HistoryController.create_history(data2, session)
    all_histories = await HistoryController.get_all(session)
    assert len(all_histories) >= 2

@pytest.mark.asyncio
async def test_get_by_variable(session):
    data = sample_history("var-X", "rep-1")
    await HistoryController.create_history(data, session)
    results = await HistoryController.get_by_variable("var-X", session)
    assert all(h.id_variable == "var-X" for h in results)

@pytest.mark.asyncio
async def test_get_by_report(session):
    data = sample_history("var-1", "rep-Y")
    await HistoryController.create_history(data, session)
    results = await HistoryController.get_by_report("rep-Y", session)
    assert all(h.id_report == "rep-Y" for h in results)

@pytest.mark.asyncio
async def test_get_by_var_and_report(session):
    data = sample_history("var-AB", "rep-XY")
    await HistoryController.create_history(data, session)
    results = await HistoryController.get_by_var_and_report("var-AB", "rep-XY", session)
    assert all(h.id_variable == "var-AB" and h.id_report == "rep-XY" for h in results)

