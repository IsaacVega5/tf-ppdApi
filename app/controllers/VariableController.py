import sqlmodel as sql
from fastapi import HTTPException, status
from app.models.Variable import Variable, VariableBase
from typing import List, Optional

async def get_all_variables(session: sql.Session) -> List[Variable]:
    """
    Retrieve all variable records from the database.
    Args:
        session (sql.Session): Database session for operations.
    Returns:
        List[Variable]: List of all variable records.
    """
    statement = sql.select(Variable)
    variables = session.exec(statement).all()
    return variables

async def get_variable_by_id(id: str, session: sql.Session) -> Variable:
    """
    Retrieve a single variable record by its unique identifier.
    Args:
        id (str): The UUID of the variable to retrieve.
        session (sql.Session): Database session for operations.
    Returns:
        Variable: The requested variable record object.
    Raises:
        HTTPException: 404 if variable is not found.
    """
    statement = sql.select(Variable).where(Variable.id_variable == id)
    variable = session.exec(statement).first()
    if not variable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variable not found")
    return variable

async def create_variable(variable_data: VariableBase, session: sql.Session) -> Variable:
    """
    Create a new variable record in the database.
    Args:
        variable_data (VariableBase): Data for the new variable record.
        session (sql.Session): Database session for operations.
    Returns:
        Variable: The newly created variable record object.
    """
    variable = Variable(**variable_data.model_dump())
    session.add(variable)
    session.commit()
    session.refresh(variable)
    return variable

async def update_variable(id: str, variable_data: VariableBase, session: sql.Session) -> Variable:
    """
    Update an existing variable record in the database.
    Args:
        id (str): The UUID of the variable to update.
        variable_data (VariableBase): Partial or full data to update.
        session (sql.Session): Database session for operations.
    Returns:
        Variable: The updated variable record object.
    Raises:
        HTTPException: 404 if variable is not found.
    """
    variable = await get_variable_by_id(id, session)
    for key, value in variable_data.model_dump(exclude_unset=True).items():
        setattr(variable, key, value)
    session.add(variable)
    session.commit()
    session.refresh(variable)
    return variable

async def delete_variable(id: str, session: sql.Session) -> dict:
    """
    Delete a variable record from the database by its ID.
    Args:
        id (str): The UUID of the variable to delete.
        session (sql.Session): Database session for operations.
    Returns:
        dict: Confirmation message with deleted variable record ID.
    Raises:
        HTTPException: 404 if variable is not found.
    """
    variable = await get_variable_by_id(id, session)
    session.delete(variable)
    session.commit()
    return {"detail": "Variable deleted", "id": id}

# Métodos adicionales de consulta
async def get_variables_by_kpi(id_kpi: str, session: sql.Session) -> List[Variable]:
    """
    Retrieve all variable records associated with a specific KPI.
    Args:
        id_kpi (str): The UUID of the KPI to filter variables.
        session (sql.Session): Database session for operations.
    Returns:
        List[Variable]: List of variables for the given KPI.
    """
    statement = sql.select(Variable).where(Variable.id_kpi == id_kpi)
    variables = session.exec(statement).all()
    return variables
