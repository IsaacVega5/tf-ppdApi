from unittest import result
from fastapi import HTTPException
from app.controllers import ActionTypeController, PpdaController, UserController
from app.models import ActionType
from app.models.Action import Action, ActionPublic
import sqlmodel as sql

async def get_all(session : sql.Session) -> list[Action]:
    """
    Retrieves a complete list of all actions in the system.

    Args:
        session: Database session

    Returns:
        List[Action]: All registered actions with their IDs and descriptions
    """
    actions = session.exec(sql.select(Action)).all()
    return actions

async def get_by_id(id_action: int, session : sql.Session) -> Action:
    """
    Retrieves a specific action by its ID.

    Args:
        id_action: ID of the action to retrieve
        session: Database session

    Returns:
        Action: The action with the specified ID
    """
    action = session.get(Action, str(id_action))
    if not action:
      raise HTTPException(status_code=404, detail="Action not found")
    return action

async def create_action(action: Action, session : sql.Session) -> Action:
    """
    Creates a new action in the system.

    Args:
        action: The action data to create
        session: Database session

    Returns:
        Action: The newly created action object
    
    Raises:
        HTTPException: 404 if action type, ppda or user doesn't exist
    """
    action_type = await ActionTypeController.get_by_id(action.id_action_type, session)
    if not action_type:
        raise HTTPException(status_code=404, detail="Action type not found")
    ppda = await PpdaController.get_by_id(action.id_ppda, session)
    if not ppda:
        raise HTTPException(status_code=404, detail="PPDA not found")
    user = UserController.get_by_id(action.id_user, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.add(action)
    session.commit()
    session.refresh(action)
    return action

async def update_action(action: Action, session : sql.Session) -> Action:
    """
    Updates an existing action in the system.

    Args:
        action: The action data to update
        session: Database session

    Returns:
        Action: The updated action object
    
    Raises:
        HTTPException: 404 if action, action type, ppda or user doesn't exist
    """
    db_action = await get_by_id(action.id_action, session)
    if not db_action:
        raise HTTPException(status_code=404, detail="Action not found")
    bd_action_type = await ActionTypeController.get_by_id(action.id_action_type, session)
    if not bd_action_type:
        raise HTTPException(status_code=404, detail="Action type not found")
    
    db_ppda = await PpdaController.get_by_id(action.id_ppda, session)
    if not db_ppda:
        raise HTTPException(status_code=404, detail="PPDA not found")
    
    db_user = UserController.get_by_id(action.id_user, session)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in action.model_dump(exclude_unset=True).items():
        setattr(db_action, field, value)
    session.add(db_action)
    session.commit()
    session.refresh(db_action)
    return db_action
  
async def delete_action(id_action: int, session : sql.Session) -> Action:
    """
    Deletes an action by its ID.

    Args:
        id_action: ID of the action to delete
        session: Database session

    Returns:
        dict: A message indicating the action was deleted
    
    Raises:
        HTTPException: 404 if the action is not found
    """
    action = await get_by_id(id_action, session)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    session.delete(action)
    session.commit()
    return {"message": f"Action {id_action} deleted"}

async def get_all_public(session : sql.Session) -> list[ActionPublic]:
    """
    Retrieves a complete list of all actions in the system in public format.

    Args:
        session: Database session

    Returns:
        List[Action]: All registered actions with their IDs and descriptions
    """
    statement = sql.select(
      ActionType.action_type,
      Action.id_ppda
    ).join_from(Action, ActionType)
    result = session.exec(statement).all()
    actions = [ActionPublic.model_validate(action) for action in result]
    return actions