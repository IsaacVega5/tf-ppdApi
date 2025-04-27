import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.controllers import ReportController
from uuid import uuid4
import asyncio

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def session():
    with Session(engine) as session:
        yield session

def get_report_data(id_action=None):
    return {"id_action": id_action or str(uuid4())}

@pytest.mark.asyncio
async def test_create_and_get_report(session):
    data = get_report_data("action-1")
    report = await ReportController.create_report(data, session)
    assert report.id_action == "action-1"
    # Obtener por ID
    fetched = await ReportController.get_by_id(report.id_report, session)
    assert fetched.id_report == report.id_report
    assert fetched.id_action == "action-1"

@pytest.mark.asyncio
async def test_update_report(session):
    data = get_report_data("action-1")
    report = await ReportController.create_report(data, session)
    update_data = {"id_action": "updated-action"}
    updated = await ReportController.update_report(report.id_report, update_data, session)
    assert updated.id_action == "updated-action"

@pytest.mark.asyncio
async def test_delete_report(session):
    data = get_report_data("action-1")
    report = await ReportController.create_report(data, session)
    resp = await ReportController.delete_report(report.id_report, session)
    assert resp["detail"] == "Report deleted"
    with pytest.raises(Exception):
        await ReportController.get_by_id(report.id_report, session)

@pytest.mark.asyncio
async def test_get_report_not_found(session):
    with pytest.raises(Exception) as excinfo:
        await ReportController.get_by_id("non-existent-id", session)
    assert "not found" in str(excinfo.value).lower()

@pytest.mark.asyncio
async def test_update_report_not_found(session):
    with pytest.raises(Exception) as excinfo:
        await ReportController.update_report("non-existent-id", {"id_action": "test"}, session)
    assert "not found" in str(excinfo.value).lower()

@pytest.mark.asyncio
async def test_delete_report_not_found(session):
    with pytest.raises(Exception) as excinfo:
        await ReportController.delete_report("non-existent-id", session)
    assert "not found" in str(excinfo.value).lower()

@pytest.mark.asyncio
async def test_get_reports_by_action(session):
    # Crea dos reportes con la misma acción y uno con otra
    data1 = get_report_data("action-1")
    data2 = get_report_data("action-1")
    data3 = get_report_data("action-2")
    await ReportController.create_report(data1, session)
    await ReportController.create_report(data2, session)
    await ReportController.create_report(data3, session)
    # Ejecuta el filtro
    reports = await ReportController.get_by_action("action-1", session)
    assert isinstance(reports, list)
    assert len(reports) == 2
    assert all(r.id_action == "action-1" for r in reports)

@pytest.mark.asyncio
async def test_get_all_reports(session):
    data1 = get_report_data("action-1")
    data2 = get_report_data("action-2")
    await ReportController.create_report(data1, session)
    await ReportController.create_report(data2, session)
    reports = await ReportController.get_all(session)
    assert isinstance(reports, list)
    assert len(reports) == 2
