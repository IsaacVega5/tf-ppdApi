from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.db import get_session
from app.models.Report import Report, ReportBase
from app.controllers import ReportController
from app.utils.auth import verify_access_token

router = APIRouter(
    prefix="/report",
    tags=["report"],
    dependencies=[Depends(verify_access_token)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Report not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
        status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
    }
)

@router.get(
    "/",
    response_model=List[Report],
    summary="List all reports",
    description="""Retrieves a list of all registered reports in the system.\n\nReturns:\n    List of Report objects.""",
    response_description="List of all reports"
)
async def get_reports(session=Depends(get_session)):
    """
    Get all reports.
    Returns a list of all reports in the system.
    """
    return await ReportController.get_all(session)

@router.get(
    "/action/{id_action}",
    response_model=List[Report],
    summary="Get reports by action ID",
    description="""Retrieves all reports associated with a specific action ID.\n\nArgs:\n    id_action (str): The action ID to filter reports.\n\nReturns:\n    List of Report objects.""",
    response_description="List of reports filtered by action ID"
)
async def get_reports_by_action(id_action: str, session=Depends(get_session)):
    """
    Get all reports by action ID.
    Args:
        id_action (str): The action ID to filter reports.
    Returns a list of reports associated with the given action.
    """
    return await ReportController.get_by_action(id_action, session)

@router.get(
    "/{id}",
    response_model=Report,
    summary="Get report by ID",
    description="""Retrieves a single report by its ID.\n\nArgs:\n    id (str): The UUID of the report to retrieve.\n\nReturns:\n    Report: The requested report object.""",
    response_description="The requested report object"
)
async def get_report(id: str, session=Depends(get_session)):
    """
    Get a single report by its ID.
    Args:
        id (str): The UUID of the report to retrieve.
    Returns the report if found, otherwise raises 404.
    """
    return await ReportController.get_by_id(id, session)

@router.post(
    "/",
    response_model=Report,
    status_code=status.HTTP_201_CREATED,
    summary="Create report",
    description="""Creates a new report.\n\nArgs:\n    report (ReportBase): The report data to create.\n\nReturns:\n    The newly created report.""",
    response_description="The newly created report"
)
async def create_report(report: ReportBase, session=Depends(get_session)):
    """
    Create a new report.
    Args:
        report (ReportBase): The report data to create.
    Returns the newly created report.
    """
    return await ReportController.create_report(report, session)

@router.put(
    "/{id}",
    response_model=Report,
    summary="Update report",
    description="""Updates an existing report by its ID.\n\nArgs:\n    id (str): The UUID of the report to update.\n    report (ReportBase): The new data for the report.\n\nReturns:\n    The updated report if found, otherwise raises 404.""",
    response_description="The updated report"
)
async def update_report(id: str, report: ReportBase, session=Depends(get_session)):
    """
    Update an existing report by its ID.
    Args:
        id (str): The UUID of the report to update.
        report (ReportBase): The new data for the report.
    Returns the updated report if found, otherwise raises 404.
    """
    return await ReportController.update_report(id, report, session)

@router.delete(
    "/{id}",
    summary="Delete report",
    description="""Deletes a report by its ID.\n\nArgs:\n    id (str): The UUID of the report to delete.\n\nReturns:\n    A confirmation message if deleted, otherwise raises 404.""",
    response_description="Confirmation message"
)
async def delete_report(id: str, session=Depends(get_session)):
    """
    Delete a report by its ID.
    Args:
        id (str): The UUID of the report to delete.
    Returns a confirmation message if deleted, otherwise raises 404.
    """
    return await ReportController.delete_report(id, session)
