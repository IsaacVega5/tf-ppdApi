from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.db import get_session
from app.models.Kpi import Kpi, KpiBase
from app.controllers import KpiController
from app.utils.auth import verify_access_token

router = APIRouter(
    prefix="/kpi",
    tags=["kpi"],
    dependencies=[Depends(verify_access_token)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "KPI not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
        status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
    }
)

@router.get("/", response_model=List[Kpi], summary="List all KPIs")
async def get_all_kpis(session=Depends(get_session)):
    """
    Retrieve all KPI records in the system.
    Args:
        session: Database session dependency.
    Returns:
        List of KPI objects.
    """
    return await KpiController.get_all_kpis(session)

@router.get("/{id}", response_model=Kpi, summary="Get KPI by ID")
async def get_kpi_by_id(id: str, session=Depends(get_session)):
    """
    Retrieve a single KPI record by its ID.
    Args:
        id (str): UUID of the KPI to retrieve.
        session: Database session dependency.
    Returns:
        The requested KPI object if found.
    """
    return await KpiController.get_kpi_by_id(id, session)

@router.post("/", response_model=Kpi, status_code=status.HTTP_201_CREATED, summary="Create a new KPI")
async def create_kpi(kpi: KpiBase, session=Depends(get_session)):
    """
    Create a new KPI record.
    Args:
        kpi (KpiBase): Data for the new KPI.
        session: Database session dependency.
    Returns:
        The newly created KPI object.
    """
    return await KpiController.create_kpi(kpi, session)

@router.put("/{id}", response_model=Kpi, summary="Update KPI by ID")
async def update_kpi(id: str, kpi: KpiBase, session=Depends(get_session)):
    """
    Update an existing KPI record by its ID.
    Args:
        id (str): UUID of the KPI to update.
        kpi (KpiBase): New data for the KPI.
        session: Database session dependency.
    Returns:
        The updated KPI object if found.
    """
    return await KpiController.update_kpi(id, kpi, session)

@router.delete("/{id}", summary="Delete KPI by ID")
async def delete_kpi(id: str, session=Depends(get_session)):
    """
    Delete a KPI record by its ID.
    Args:
        id (str): UUID of the KPI to delete.
        session: Database session dependency.
    Returns:
        Confirmation message with deleted KPI record ID.
    """
    return await KpiController.delete_kpi(id, session)

@router.get("/action/{id_action}", response_model=List[Kpi], summary="Get KPIs by Action")
async def get_kpis_by_action(id_action: str, session=Depends(get_session)):
    """
    Retrieve all KPI records for a given action.
    Args:
        id_action (str): UUID of the action.
        session: Database session dependency.
    Returns:
        List of KPI objects for the action.
    """
    return await KpiController.get_kpis_by_action(id_action, session)
