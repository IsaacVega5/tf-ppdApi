from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from typing import Annotated

from app.db import get_session
from app.models.User import User, UserCreate
from app.controllers import UserController
from app.utils.auth import get_current_user, get_admin_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "User already exists"}
  }
)

@router.get("/",
            response_model=List[User],
            dependencies=[Depends(get_admin_user)],
            summary="List all users",
            description="""Retrieves a list of all registered users in the system.
            
            Returns:
                List of User objects with sensitive fields omitted
            """,
            response_description="List of all users"
            )
async def get_users(session = Depends(get_session)):
  """
  Get all users.
  
  Returns:
      List[User]: A list of all registered users.
  """
  users = UserController.get_all(session)
  return users

@router.get("/me")
async def get_user_me(current_user : Annotated[User, Depends(get_current_user)]):
  return current_user

@router.get("/{id}", 
            response_model=User,
            dependencies=[Depends(get_admin_user)],
            summary="Get user by ID",
            description="""Retrieves details of a specific user.
            
            Args:
                id: UUID of the user to retrieve
            
            Returns:
                Complete user profile
            """,
            response_description="User details"
            )
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

@router.delete("/{id}",
                dependencies=[Depends(get_admin_user)],
                summary="Delete user account",
                description="""Permanently deletes a user account.
                
                Returns:
                    Confirmation message with deletion status
                """,
                response_description="Deletion confirmation"
               )
async def delete_user(id, session = Depends(get_session)):
  """
  Delete a user by ID.
  
  Args:
      id (str): The UUID of the user to delete.
  
  Returns:
      dict: Confirmation message.
  """
  return UserController.delete_user(id, session)

@router.post("/",
              response_model=User,
              dependencies=[Depends(get_admin_user)],
              status_code=status.HTTP_201_CREATED,
              summary="Register new user",
              description="""Creates a new user account after validation.
              
              Returns:
                  Newly created user profile
              """,
              response_description="Registered user data"
            )
async def post_user(user: UserCreate, session = Depends(get_session)):
  """
  Create a new user.
  
  Args:
      user (UserCreate): User data including email and password.
  
  Returns:
      User: The newly created user's data.
  """
  return UserController.create_user(user, session)
