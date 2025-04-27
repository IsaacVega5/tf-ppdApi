import sqlmodel as sql
from fastapi import HTTPException, status
from app.models.History import History, HistoryBase
from typing import List

async def get_all(session: sql.Session) -> List[History]:
    """
    Retrieve all history records from the database.
    Args:
        session (sql.Session): Database session for operations.
    Returns:
        List[History]: List of all history records.
    """
    statement = sql.select(History)
    histories = session.exec(statement).all()
    return histories

async def get_by_id(id: str, session: sql.Session) -> History:
    """
    Retrieve a single history record by its unique identifier.
    Args:
        id (str): The UUID of the history record to retrieve.
        session (sql.Session): Database session for operations.
    Returns:
        History: The requested history record object.
    Raises:
        HTTPException: 404 if history record is not found.
    """
    statement = sql.select(History).where(History.id_history == id)
    history = session.exec(statement).first()
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    return history

async def create_history(history_data: HistoryBase, session: sql.Session) -> History:
    """
    Create a new history record in the database.
    Args:
        history_data (HistoryBase): Data for the new history record.
        session (sql.Session): Database session for operations.
    Returns:
        History: The newly created history record object.
    """
    history = History(**history_data.model_dump()) if hasattr(history_data, 'model_dump') else History(**dict(history_data))
    session.add(history)
    session.commit()
    session.refresh(history)
    return history

async def update_history(id: str, history_data: HistoryBase, session: sql.Session) -> History:
    """
    Update an existing history record in the database.
    Args:
        id (str): The UUID of the history record to update.
        history_data (HistoryBase): Partial or full data to update.
        session (sql.Session): Database session for operations.
    Returns:
        History: The updated history record object.
    Raises:
        HTTPException: 404 if history record is not found.
    """
    statement = sql.select(History).where(History.id_history == id)
    history = session.exec(statement).first()
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    for key, value in history_data.model_dump().items() if hasattr(history_data, 'model_dump') else dict(history_data).items():
        setattr(history, key, value)
    session.add(history)
    session.commit()
    session.refresh(history)
    return history

async def delete_history(id: str, session: sql.Session) -> dict:
    """
    Delete a history record from the database by its ID.
    Args:
        id (str): The UUID of the history record to delete.
        session (sql.Session): Database session for operations.
    Returns:
        dict: Confirmation message with deleted history record ID.
    Raises:
        HTTPException: 404 if history record is not found.
    """
    statement = sql.select(History).where(History.id_history == id)
    history = session.exec(statement).first()
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History not found")
    session.delete(history)
    session.commit()
    return {"detail": "History deleted", "id": id}

# Métodos adicionales de consulta
async def get_by_var_and_report(id_variable: str, id_report: str, session: sql.Session):
    """
    Get all history records for a given variable and report.
    """
    statement = sql.select(History).where(
        (History.id_variable == id_variable) & (History.id_report == id_report)
    )
    return session.exec(statement).all()

async def get_by_variable(id_variable: str, session: sql.Session):
    """
    Get all history records for a given variable.
    """
    statement = sql.select(History).where(History.id_variable == id_variable)
    return session.exec(statement).all()

async def get_by_report(id_report: str, session: sql.Session):
    """
    Get all history records for a given report.
    """
    statement = sql.select(History).where(History.id_report == id_report)
    return session.exec(statement).all()

async def get_by_kpi(id_kpi: str, session: sql.Session):
    """
    Get all history records for a given KPI (requires join to Variable or Report).
    """
    # Suponiendo que Variable tiene id_kpi y que History -> Variable -> KPI
    from app.models.Variable import Variable
    statement = sql.select(History).join(Variable).where(Variable.id_kpi == id_kpi)
    return session.exec(statement).all()

async def get_by_action(id_action: str, session: sql.Session):
    """
    Get all history records for a given Action (requires join to Report or Variable).
    """
    # Suponiendo que Report tiene id_action y que History -> Report -> Action
    from app.models.Report import Report
    statement = sql.select(History).join(Report).where(Report.id_action == id_action)
    return session.exec(statement).all()
