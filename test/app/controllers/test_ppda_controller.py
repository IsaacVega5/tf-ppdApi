import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi import HTTPException, status
from app.controllers.PpdaController import (
    get_all, get_by_id, create_ppda, update_ppda, delete_ppda
)
from app.models.Ppda import PpdaCreate, Ppda
from app.models.Institution import Institution
import uuid

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def sample_institution(session):
    institution = Institution(
        id_institution="inst-1",
        name="Institución Test"
    )
    session.add(institution)
    session.commit()
    return institution

@pytest.fixture
def sample_ppda_data(sample_institution):
    return PpdaCreate(
        id_institution=sample_institution.id_institution,
        name="Test ppda",
    )

@pytest.mark.asyncio
async def test_create_ppda_success(session, sample_ppda_data):
    ppda = await create_ppda(sample_ppda_data, session)
    assert ppda is not None
    assert ppda.id_institution == sample_ppda_data.id_institution
    assert ppda.id_ppda is not None

@pytest.mark.asyncio
async def test_get_all_ppda(session, sample_ppda_data):
    await create_ppda(sample_ppda_data, session)
    await create_ppda(sample_ppda_data, session)

    ppda_list = await get_all(session)
    assert len(ppda_list) == 2

@pytest.mark.asyncio
async def test_get_by_id_found(session, sample_ppda_data):
    ppda = await create_ppda(sample_ppda_data, session)
    result = await get_by_id(ppda.id_ppda, session)
    assert result is not None
    assert result.id_ppda == ppda.id_ppda

@pytest.mark.asyncio
async def test_get_by_id_not_found(session):
    result = await get_by_id(str(uuid.uuid4()), session)
    assert result is None

@pytest.mark.asyncio
async def test_update_ppda_success(session, sample_institution):
    ppda = await create_ppda(PpdaCreate(id_institution=sample_institution.id_institution, name="Test ppda"), session)
    ppda.id_institution = sample_institution.id_institution
    updated = await update_ppda(ppda, session)
    assert updated.id_ppda == ppda.id_ppda
    assert updated.id_institution == sample_institution.id_institution

@pytest.mark.asyncio
async def test_update_ppda_not_found(session):
    fake_ppda = Ppda(id_ppda="non-existent", id_institution="inst-1")
    with pytest.raises(HTTPException) as exc_info:
        await update_ppda(fake_ppda, session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ppda not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_delete_ppda_success(session, sample_ppda_data):
    ppda = await create_ppda(sample_ppda_data, session)
    result = await delete_ppda(ppda.id_ppda, session)
    assert result["message"] == "Ppda deleted successfully"
    deleted = await get_by_id(ppda.id_ppda, session)
    assert deleted is None

@pytest.mark.asyncio
async def test_delete_ppda_not_found(session):
    with pytest.raises(HTTPException) as exc_info:
        await delete_ppda(str(uuid.uuid4()), session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Ppda not found" in exc_info.value.detail
