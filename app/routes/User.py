from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address


from app.db import get_session
from app.models.User import User, UserCreate, UserLogin
from app.controllers import UserController

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.get("/")
async def get_users(session = Depends(get_session), request : Request = None):
  """
  Get all users.
  
  Returns:
      List[User]: A list of all registered users.
  """
  users = UserController.get_all(session)
  return users

@router.get("/{id}")
async def get_user(id, session = Depends(get_session)):
  """
  Get a specific user by ID.
  
  Args:
      id (str): The UUID of the user to retrieve.
  
  Returns:
      User: The requested user's data.
  
  Raises:
      HTTPException: 404 if user is not found.
  """
  user = UserController.get_by_id(id, session)
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  return user

@router.delete("/{id}")
async def delete_user(id, session = Depends(get_session)):
  """
  Delete a user by ID.
  
  Args:
      id (str): The UUID of the user to delete.
  
  Returns:
      dict: Confirmation message.
  """
  return UserController.delete_user(id, session)

@router.post("/")
async def post_user(user: UserCreate, session = Depends(get_session)):
  """
  Create a new user.
  
  Args:
      user (UserCreate): User data including email and password.
  
  Returns:
      User: The newly created user's data.
  """
  return UserController.create_user(user, session)

@router.post("/login")
async def login(user: UserLogin, session = Depends(get_session)):
  """
  Authenticate a user.
  
  Args:
      user (UserLogin): User credentials (email and password).
  
  Returns:
      User: Authenticated user's data.
  """
  return UserController.login(user, session)