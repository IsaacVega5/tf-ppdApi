from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.db import get_session
from app.models.DeadLine import DeadLine, DeadLineBase
from app.controllers.DeadLineController import DeadLineController
from app.utils.auth import verify_access_token

router = APIRouter(
    prefix="/deadline",
    tags=["deadline"],
    dependencies=[Depends(verify_access_token)],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Deadline not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
        status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
    }
)

@router.get(
    "/",
    response_model=List[DeadLine],
    summary="List all deadlines",
    response_description="List of all deadlines"
)
async def get_deadlines(session=Depends(get_session)):
    """
    Retrieve a list of all deadlines in the system.
    Args:
        session: Database session dependency.
    Returns:
        List of DeadLine objects.
    """
    return await DeadLineController.get_all(session)

@router.get(
    "/{id}",
    response_model=DeadLine,
    summary="Get deadline by ID",
    response_description="The requested deadline object"
)
async def get_deadline(id: str, session=Depends(get_session)):
    """
    Retrieve a single deadline by its ID.
    Args:
        id (str): UUID of the deadline to retrieve.
        session: Database session dependency.
    Returns:
        The requested DeadLine object if found.
    """
    return await DeadLineController.get_by_id(id, session)

@router.post(
    "/",
    response_model=DeadLine,
    status_code=status.HTTP_201_CREATED,
    summary="Create deadline",
    response_description="The newly created deadline"
)
async def create_deadline(deadline: DeadLineBase, session=Depends(get_session)):
    """
    Create a new deadline.
    Args:
        deadline (DeadLineBase): Data for the new deadline.
        session: Database session dependency.
    Returns:
        The newly created DeadLine object.
    """
    return await DeadLineController.create_deadline(deadline, session)

@router.put(
    "/{id}",
    response_model=DeadLine,
    summary="Update deadline",
    response_description="The updated deadline"
)
async def update_deadline(id: str, deadline: DeadLineBase, session=Depends(get_session)):
    """
    Update an existing deadline by its ID.
    Args:
        id (str): UUID of the deadline to update.
        deadline (DeadLineBase): New data for the deadline.
        session: Database session dependency.
    Returns:
        The updated DeadLine object if found.
    """
    return await DeadLineController.update_deadline(id, deadline, session)

@router.delete(
    "/{id}",
    summary="Delete deadline",
    response_description="Confirmation of deletion"
)
async def delete_deadline(id: str, session=Depends(get_session)):
    """
    Delete a deadline by its ID.
    Args:
        id (str): UUID of the deadline to delete.
        session: Database session dependency.
    Returns:
        Confirmation message with deleted deadline ID.
    """
    return await DeadLineController.delete_deadline(id, session)
