from fastapi import HTTPException, status
import sqlmodel as sql
from app.models import ActionType, ActionTypeUpdate

async def get_all(session : sql.Session) -> list[sql.SQLModel]:
  """
  Retrieve all action types endpoint.

  Returns every action type registered in the system.
  The list includes basic type information that can be used
  when creating or updating actions.
  """
  action_types = session.exec(sql.select(ActionType)).all()
  return action_types

async def get_by_id(id: int, session: sql.Session) -> ActionType:
  """
  Get a single action type by its ID.

  Args:
    id (int): The ID of the action type to retrieve.
    session (Session): Database session for operations.

  Returns:
    ActionType: The requested action type.

  Raises:
    HTTPException: 404 if action type is not found.
  """
  action_type = session.get(ActionType, id)
  if not action_type:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Action type not found"
    )
  return action_type

async def create_action_type(action_type: ActionType, session: sql.Session) -> ActionType:
  """
  Create a new action type endpoint.

  Args:
    action_type (ActionType): The action type data to create
    session (Session): Database session for operations

  Returns:
    ActionType: The newly created action type with its details

  Raises:
    HTTPException: 400 if action type is empty
    HTTPException: 409 if action type already exists
  """
  if not action_type.action_type.strip():
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Action type cannot be empty"
    )
  db_action_type = session.exec(
    sql.select(ActionType).where(ActionType.action_type == action_type.action_type)
  ).first()
  if db_action_type:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="Action type already exists"
    )
  session.add(action_type)
  session.commit()
  session.refresh(action_type)
  return action_type

async def update_action_type(id: int, action_type: ActionTypeUpdate, session: sql.Session) -> ActionType:
  """
  Update an existing action type.

  Args:
    id (int): The ID of the action type to update.
    action_type (ActionType): The updated action type data.
    session (Session): Database session for operations.

  Returns:
    ActionType: The updated action type.

  Raises:
    HTTPException: 404 if action type is not found.
  """
  db_action_type = session.get(ActionType, id)
  if not db_action_type:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Action type not found"
    )
  db_action_type.action_type = action_type.action_type
  session.commit()
  session.refresh(db_action_type)
  return db_action_type

async def delete_action_type(id: int, session: sql.Session) -> None:
  """
  Delete an action type by ID.

  Args:
    id (int): The ID of the action type to delete.
    session (Session): Database session for operations.

  Returns:
    dict: A message indicating the action type was deleted.
    
  Raises:
    HTTPException: 404 if action type is not found.
  """
  action_type = session.get(ActionType, id)
  if not action_type:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Action type not found"
    )
  session.delete(action_type)
  session.commit()
  return {"message": f"Action type {id} deleted"}