from fastapi import HTTPException, status
from sqlmodel import Session
from app.utils.hashing import get_hash

import sqlmodel as sql

from app.models.User import UserCreate, User

def create_user(user: UserCreate, session: Session):
    """
    Creates a new user.
    
    Args:
        user (UserCreate): User data including email and plain text password.
        session (Session): Database session for operations.
    
    Returns:
        User: The newly created user object.
    
    Raises:
        HTTPException: 409 Conflict if email is already registered.
    """
    existing_user = session.exec(
        sql.select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username is already in use"
        )
    
    # Hash de la contraseña
    user.password = get_hash(user.password)
    
    new_user = User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_all(session : Session):
  """
  Retrieves all users from the database.
  
  Args:
      session (Session): Database session for operations.
  
  Returns:
      List[User]: List of all user objects.
  """
  statement = sql.select(User)
  users = session.exec(statement).all()
  return users

def get_by_id(id: int, session : Session):
  """
  Retrieves a single user by their ID.
  
  Args:
      id (int): The ID of the user to retrieve.
      session (Session): Database session for operations.
  
  Returns:
      User | None: The requested user or None if not found.
  """
  statement = sql.select(User).where(User.id_user == id)
  user = session.exec(statement).first()
  return user

def get_by_username(username: str, session : Session):
  statement = sql.select(User).where(User.username == username)
  user = session.exec(statement).first()
  return user

def delete_user(id: str, session: Session):
    """
    Deletes a user from the database by their ID.
    
    Args:
        id (str): The ID of the user to delete.
        session (Session): Database session for operations.
    
    Returns:
        dict: Confirmation message.
    
    Raises:
        HTTPException: 404 Not Found if user doesn't exist.
    """
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found"
        )
    
    statement = sql.delete(User).where(User.id_user == id)
    session.exec(statement)
    session.commit()
    return {"message": f"User was deleted successfully"}