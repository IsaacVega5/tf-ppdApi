import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers import KpiController
from app.models.Kpi import Kpi
from fastapi import HTTPException, status
import uuid

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

def sample_kpi(id_action=None, description=None):
    return Kpi(
        id_action=id_action or str(uuid.uuid4()),
        description=description or "Test KPI"
    )

@pytest.mark.asyncio
async def test_create_and_get_kpi(session):
    data = sample_kpi("action-1", "desc-1")
    kpi = await KpiController.create_kpi(data, session)
    fetched = await KpiController.get_kpi_by_id(kpi.id_kpi, session)
    assert fetched.id_kpi == kpi.id_kpi
    assert fetched.description == "desc-1"

@pytest.mark.asyncio
async def test_update_kpi(session):
    data = sample_kpi("action-2", "desc-2")
    kpi = await KpiController.create_kpi(data, session)
    kpi.description = "updated desc"
    updated = await KpiController.update_kpi(kpi.id_kpi, kpi, session)
    assert updated.description == "updated desc"

@pytest.mark.asyncio
async def test_delete_kpi(session):
    data = sample_kpi("action-3", "desc-3")
    kpi = await KpiController.create_kpi(data, session)
    resp = await KpiController.delete_kpi(kpi.id_kpi, session)
    assert resp["detail"] == "KPI deleted"
    with pytest.raises(HTTPException) as exc:
        await KpiController.get_kpi_by_id(kpi.id_kpi, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_kpis_by_action(session):
    action_id = str(uuid.uuid4())
    kpi1 = await KpiController.create_kpi(sample_kpi(action_id, "desc-a"), session)
    kpi2 = await KpiController.create_kpi(sample_kpi(action_id, "desc-b"), session)
    kpis = await KpiController.get_kpis_by_action(action_id, session)
    assert len(kpis) >= 2
    ids = [k.id_kpi for k in kpis]
    assert kpi1.id_kpi in ids and kpi2.id_kpi in ids
