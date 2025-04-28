
from re import A
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import ActionController, PpdaController
from app.db import get_session
from app.models import Role, User
from app.models.Action import Action, ActionCreate, ActionUpdate, ActionPublic
from app.utils.auth import get_admin_user, get_current_user
from app.utils.rbac import verify_institution_role

router = APIRouter(
  prefix="/action",
  tags=["action"],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "Action not found"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
  }
)

@router.get(
  "/",
  response_model=list[Action],
  summary="Get all actions",
  description="""
  Retrieves a complete list of all actions in the system.

  Returns:
    List[Action]: All registered actions with their IDs and descriptions
  """,
  response_description="List of actions"
)
async def get_action(session = Depends(get_session), user : Annotated[User, Depends(get_admin_user)] = None): 
  """
  Retrieves a complete list of all actions in the system.

  Returns:
    List[Action]: All registered actions with their IDs and descriptions
  """
  
  return await ActionController.get_all(session)

@router.get(
  "/public", 
  summary="Get all actions in public format",
  description="""
  Retrieves a complete list of all actions in the system in public format.

  Returns:
    List[ActionPublic]: All registered actions with their IDs and descriptions in public format
  """,
  response_model=list[ActionPublic]
  )
async def get_all_actions_public(session = Depends(get_session)):
  """
  Retrieves a complete list of all actions in the system in public format.

  Returns:
    List[ActionPublic]: All registered actions with their IDs and descriptions in public format
  """
  return await ActionController.get_all_public(session)

@router.get(
  "/{id_action}",
  response_model=Action,
  summary="Get action by ID",
  description="""
  Retrieves a specific action by its ID.

  Args:
    id_action (int): ID of the action to retrieve

  Returns:
    Action: The requested action object

  Raises:
    HTTPException: 404 if the action is not found
  """,
  response_description="Action object"
)
async def get_action_by_id(id_action: str, session = Depends(get_session), user : Annotated[User, Depends(get_current_user)] = None):
  """
  Retrieves a specific action by its ID.

  Args:
    id_action (int): ID of the action to retrieve

  Returns:
    Action: The requested action object

  Raises:
    HTTPException: 404 if the action is not found
  """
  action = await ActionController.get_by_id(id_action, session)
  if not action:
    raise HTTPException(status_code=404, detail="Action not found")
  ppda = await PpdaController.get_by_id(action.id_ppda, session)
  verify_institution_role(
    institution_ids=[ppda.id_institution],
    required_role=Role.VIEWER,
    current_user=user,
    session=session
  )
  
  return action

@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=Action,
  summary="Create a new action",
  description="""
  Creates a new action in the system.

  Args:
    action (Action): The action data to create

  Returns:
    Action: The newly created action object

  Raises:
    HTTPException: 400 if the action is empty
    HTTPException: 409 if the action already exists
  """,
  response_description="Created action object"
)
async def create_action(action: ActionCreate, user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Creates a new action in the system.

  Args:
    action (Action): The action data to create

  Returns:
    Action: The newly created action object
  
  Raises:
    HTTPException: 404 if action type, ppda or user doesn't exist
  """
  ppda = await PpdaController.get_by_id(action.id_ppda, session)
  verify_institution_role(
    institution_ids=[ppda.id_institution],
    required_role=Role.EDITOR,
    current_user=user,
    session=session
  )
  action = Action.model_validate(action)
  action.id_user = user.id_user
  return await ActionController.create_action(action, session)

@router.put(
  "/{id_action}",
  response_model=Action,
  summary="Update an action",
  description="""
  Updates an existing action in the system.

  Args:
    id_action (int): ID of the action to update
    action (Action): The updated action data

  Returns:
    Action: The updated action object

  Raises:
    HTTPException: 404 if the action is not found
  """,
  response_description="Updated action object"
)
async def update_action(id_action: str, action: ActionUpdate, user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Updates an existing action in the system.

  Args:
    id_action (int): ID of the action to update
    action (Action): The updated action data

  Returns:
    Action: The updated action object
    
  Raises:
      HTTPException: 404 if action, action type, ppda or user doesn't exist 
  """
  ppda = await PpdaController.get_by_id(action.id_ppda, session)
  verify_institution_role(
    institution_ids=[ppda.id_institution],
    required_role=Role.EDITOR,
    current_user=user,
    session=session
  )
  action = Action.model_validate(action)
  action.id_action = id_action
  
  return await ActionController.update_action(action, session)

@router.delete(
  "/{id_action}",
  summary="Delete an action",
  description="""
  Deletes an action by its ID.

  Args:
    id_action (int): ID of the action to delete

  Returns:
    None

  Raises:
    HTTPException: 404 if the action is not found
  """,
  response_description="Deleted action message"
)
async def delete_action(id_action: str, session = Depends(get_session), user : Annotated[User, Depends(get_current_user)] = None):
  """
  Deletes an action by its ID.

  Args:
    id_action (int): ID of the action to delete

  Returns:
    None

  Raises:
    HTTPException: 404 if the action is not found
  """
  action = await ActionController.get_by_id(id_action, session)
  ppda = await PpdaController.get_by_id(action.id_ppda, session)
  verify_institution_role(
    institution_ids=[ppda.id_institution],
    required_role=Role.EDITOR,
    current_user=user,
    session=session
  )
  return await ActionController.delete_action(id_action, session)
