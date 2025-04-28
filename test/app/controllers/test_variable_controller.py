import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.controllers import VariableController
from app.models.Variable import Variable
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

def sample_variable(id_kpi=None, formula=None, verification_medium=None):
    return Variable(
        id_kpi=id_kpi or str(uuid.uuid4()),
        formula=formula or "Test Formula",
        verification_medium=verification_medium or "Test Medium"
    )

@pytest.mark.asyncio
async def test_create_and_get_variable(session):
    data = sample_variable("kpi-1", "formula-1", "medium-1")
    variable = await VariableController.create_variable(data, session)
    fetched = await VariableController.get_variable_by_id(variable.id_variable, session)
    assert fetched.id_variable == variable.id_variable
    assert fetched.formula == "formula-1"
    assert fetched.verification_medium == "medium-1"

@pytest.mark.asyncio
async def test_update_variable(session):
    data = sample_variable("kpi-2", "formula-2", "medium-2")
    variable = await VariableController.create_variable(data, session)
    variable.formula = "updated formula"
    variable.verification_medium = "updated medium"
    updated = await VariableController.update_variable(variable.id_variable, variable, session)
    assert updated.formula == "updated formula"
    assert updated.verification_medium == "updated medium"

@pytest.mark.asyncio
async def test_delete_variable(session):
    data = sample_variable("kpi-3", "formula-3", "medium-3")
    variable = await VariableController.create_variable(data, session)
    resp = await VariableController.delete_variable(variable.id_variable, session)
    assert resp["detail"] == "Variable deleted"
    with pytest.raises(HTTPException) as exc:
        await VariableController.get_variable_by_id(variable.id_variable, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_all_variables(session):
    # Create multiple variables
    var1 = await VariableController.create_variable(sample_variable("kpi-4", "formula-4", "medium-4"), session)
    var2 = await VariableController.create_variable(sample_variable("kpi-5", "formula-5", "medium-5"), session)
    
    # Get all variables
    variables = await VariableController.get_all_variables(session)
    
    # Check that our created variables are in the list
    variable_ids = [var.id_variable for var in variables]
    assert var1.id_variable in variable_ids
    assert var2.id_variable in variable_ids

@pytest.mark.asyncio
async def test_get_variables_by_kpi(session):
    kpi_id = str(uuid.uuid4())
    # Create variables for the same KPI
    var1 = await VariableController.create_variable(sample_variable(kpi_id, "formula-a", "medium-a"), session)
    var2 = await VariableController.create_variable(sample_variable(kpi_id, "formula-b", "medium-b"), session)
    # Create variable for a different KPI
    var3 = await VariableController.create_variable(sample_variable(str(uuid.uuid4()), "formula-c", "medium-c"), session)
    
    # Get variables by KPI
    variables = await VariableController.get_variables_by_kpi(kpi_id, session)
    
    # Check results
    assert len(variables) == 2
    variable_ids = [var.id_variable for var in variables]
    assert var1.id_variable in variable_ids
    assert var2.id_variable in variable_ids
    assert var3.id_variable not in variable_ids
