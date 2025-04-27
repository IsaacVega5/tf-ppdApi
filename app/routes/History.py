from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.db import get_session
from app.models.History import History, HistoryBase
from app.controllers import HistoryController
from app.utils.auth import verify_access_token

router = APIRouter(
    prefix="/history",
    tags=["history"],
    dependencies=[Depends(verify_access_token)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "History record not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
        status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
    }
)

@router.get("/", response_model=List[History], summary="List all history records")
async def get_all_history(session=Depends(get_session)):
    """
    Retrieve all history records in the system.
    Args:
        session: Database session dependency.
    Returns:
        List of History objects.
    """
    return await HistoryController.get_all(session)

@router.get("/{id}", response_model=History, summary="Get history by ID")
async def get_history_by_id(id: str, session=Depends(get_session)):
    """
    Retrieve a single history record by its ID.
    Args:
        id (str): UUID of the history record to retrieve.
        session: Database session dependency.
    Returns:
        The requested History object if found.
    """
    return await HistoryController.get_by_id(id, session)

@router.post("/", response_model=History, status_code=status.HTTP_201_CREATED, summary="Create history record")
async def create_history(history: HistoryBase, session=Depends(get_session)):
    """
    Create a new history record.
    Args:
        history (HistoryBase): Data for the new history record.
        session: Database session dependency.
    Returns:
        The newly created History object.
    """
    return await HistoryController.create_history(history, session)

@router.put("/{id}", response_model=History, summary="Update history record")
async def update_history(id: str, history: HistoryBase, session=Depends(get_session)):
    """
    Update an existing history record by its ID.
    Args:
        id (str): UUID of the history record to update.
        history (HistoryBase): New data for the history record.
        session: Database session dependency.
    Returns:
        The updated History object if found.
    """
    return await HistoryController.update_history(id, history, session)

@router.delete("/{id}", summary="Delete history record")
async def delete_history(id: str, session=Depends(get_session)):
    """
    Delete a history record by its ID.
    Args:
        id (str): UUID of the history record to delete.
        session: Database session dependency.
    Returns:
        Confirmation message with deleted history record ID.
    """
    return await HistoryController.delete_history(id, session)

@router.get("/variable/{id_variable}", response_model=List[History], summary="Get history by variable")
async def get_history_by_variable(id_variable: str, session=Depends(get_session)):
    """
    Retrieve all history records for a given variable.
    Args:
        id_variable (str): UUID of the variable.
        session: Database session dependency.
    Returns:
        List of History objects for the variable.
    """
    return await HistoryController.get_by_variable(id_variable, session)

@router.get("/report/{id_report}", response_model=List[History], summary="Get history by report")
async def get_history_by_report(id_report: str, session=Depends(get_session)):
    """
    Retrieve all history records for a given report.
    Args:
        id_report (str): UUID of the report.
        session: Database session dependency.
    Returns:
        List of History objects for the report.
    """
    return await HistoryController.get_by_report(id_report, session)

@router.get("/var-report/{id_variable}/{id_report}", response_model=List[History], summary="Get history by variable and report")
async def get_history_by_var_and_report(id_variable: str, id_report: str, session=Depends(get_session)):
    """
    Retrieve all history records for a specific variable and report combination.
    Args:
        id_variable (str): UUID of the variable.
        id_report (str): UUID of the report.
        session: Database session dependency.
    Returns:
        List of History objects for the variable and report.
    """
    return await HistoryController.get_by_var_and_report(id_variable, id_report, session)

@router.get("/kpi/{id_kpi}", response_model=List[History], summary="Get history by KPI")
async def get_history_by_kpi(id_kpi: str, session=Depends(get_session)):
    """
    Retrieve all history records for a given KPI.
    Args:
        id_kpi (str): UUID of the KPI.
        session: Database session dependency.
    Returns:
        List of History objects for the KPI.
    """
    return await HistoryController.get_by_kpi(id_kpi, session)

@router.get("/action/{id_action}", response_model=List[History], summary="Get history by Action")
async def get_history_by_action(id_action: str, session=Depends(get_session)):
    """
    Retrieve all history records for a given Action.
    Args:
        id_action (str): UUID of the Action.
        session: Database session dependency.
    Returns:
        List of History objects for the Action.
    """
    return await HistoryController.get_by_action(id_action, session)
