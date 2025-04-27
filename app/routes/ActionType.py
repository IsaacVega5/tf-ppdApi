
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import ActionTypeController
from app.db import get_session
from app.models.ActionType import ActionTypeCreate, ActionType, ActionTypeUpdate
from app.utils.auth import get_admin_user

router = APIRouter(
  prefix="/action-type",
  tags=["action-type"],
  dependencies=[Depends(get_admin_user)],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "Action type not found"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
  }
)

@router.get(
  "/", 
  response_model=list[ActionType],
  summary="List all action types",
  description="""
  Retrieves a complete list of all action types in the system.

  Returns:
    List[ActionType]: All registered action types with their IDs and descriptions
  """  ,
  response_description="List of action types"
)
async def get_action_type( session = Depends(get_session)):
  """
  Retrieve all action types endpoint.

  Returns every action type registered in the system.
  The list includes basic type information that can be used
  when creating or updating actions.
  """
  action_types = await ActionTypeController.get_all(session)
  return action_types

@router.get(
  "/{id_action_type}",
  response_model=ActionType,
  summary="Get action type by ID",
  description="""
  Retrieves a specific action type by its ID.

  Args:
    id_action_type (int): The ID of the action type to retrieve

  Returns:
    ActionType: The requested action type with its details
  
  Raises:
    HTTPException: 404 if action type is not found
  """,
  response_description="Action type details"
)
async def get_action_type_by_id(id_action_type: int, session = Depends(get_session)):
  action_type = await ActionTypeController.get_by_id(id_action_type, session)
  return action_type

@router.post(
  "/",
  response_model=ActionType,
  summary="Create a new action type",
  description="""
  Creates a new action type in the system.

  Args:
    action_type (ActionTypeCreate): The action type data to create

  Returns:
    ActionType: The newly created action type with its details

  Raises:
    HTTPException: 400 if action type is empty
    HTTPException: 409 if action type already exists
  """,
  response_description="Created action type details"
)
async def create_action_type(action_type: ActionTypeCreate, session = Depends(get_session)):
  """
  Create a new action type endpoint.

  Args:
    action_type (ActionTypeCreate): The action type data to create
    session (Session): Database session for operations

  Returns:
    ActionType: The newly created action type with its details

  Raises:
    HTTPException: 400 if action type is empty
    HTTPException: 409 if action type already exists
  """
  action_type = ActionType.model_validate(action_type)
  action_type = await ActionTypeController.create_action_type(action_type, session)
  return action_type

@router.put(
  "/{id_action_type}",
  response_model=ActionType,
  summary="Update an action type by ID",
  description="""
  Updates an existing action type in the system.

  Args:
    id_action_type (int): The ID of the action type to update
    action_type (ActionTypeCreate): The updated action type data

  Returns:
    ActionType: The updated action type with its details

  Raises:
    HTTPException: 404 if action type is not found
  """,
  response_description="Updated action type details"
)
async def update_action_type(id_action_type: int, action_type: ActionTypeUpdate, session = Depends(get_session)):
  """
  Update an existing action type endpoint.

  Args:
    id_action_type (int): The ID of the action type to update
    action_type (ActionTypeUpdate): The updated action type data
    session (Session): Database session for operations

  Returns:
    ActionType: The updated action type with its details

  Raises:
    HTTPException: 404 if action type is not found or invalid data provided
  """
  action_type = await ActionTypeController.update_action_type(id_action_type, action_type, session)
  return action_type

@router.delete(
  "/{id_action_type}",
  summary="Delete an action type by ID",
  description="""
  Deletes an action type from the system by its ID.

  Args:
    id_action_type (int): The ID of the action type to delete
    
  Returns:
    dict: Confirmation message indicating successful deletion

  Raises:
    HTTPException: 404 if action type is not found
  """
)
async def delete_action_type(id_action_type: int, session = Depends(get_session)):
  """
  Delete an action type endpoint.
  
  Args:
    id_action_type (int): The ID of the action type to delete
    session (Session): Database session for operations

  Returns:
    dict: Confirmation message indicating successful deletion
  
  Raises:
    HTTPException: 404 if action type is not found
  """
  return await ActionTypeController.delete_action_type(id_action_type, session)