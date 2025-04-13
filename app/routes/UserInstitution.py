from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db import get_session
from app.controllers import UserInstitutionController
from app.models import User
from app.models.UserInstitution import UserInstitution, UserInstitutionPublic, UserInstitutionCreate, UserInstitutionUpdate
from app.utils.auth import get_current_user, get_admin_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/user-institution",
  tags=["user-institution"],
  dependencies=[Depends(get_admin_user)],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "User or institution not found"},
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "user already in institution"}
  }
)

@router.get("/", 
            response_model=List[UserInstitutionPublic], 
            summary="List all user-institution relationships", 
            description="""
            Retrieves a list of all user-institution relationships in the system.

            Returns:
                List of UserInstitutionPublic objects
            """
            )
async def get_user_institutions(current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Get all user-institution relationships.
  
  Returns:
      List[UserInstitutionPublic]: A list of all user-institution relationships
  """
  if current_user is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  if not current_user.is_admin:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
  return await UserInstitutionController.get_all(session)

@router.get("/user/{id_user}/institution/{id_institution}", 
            response_model=UserInstitutionPublic, 
            summary="Get user-institution relationship by ID", 
            description="""
            Retrieves details of a specific user-institution relationship.

            Args:
                id_user (str): The UUID of the user.
                id_institution (str): The UUID of the institution.

            Returns:
                UserInstitutionPublic: The requested user-institution relationship.
            """
            )
async def get_user_institution(id_user: str, id_institution: str, current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Get a specific user-institution relationship by ID.
  
  Args:
      id_user (str): The UUID of the user.
      id_institution (str): The UUID of the institution.
  
  Returns:
      UserInstitutionPublic: The requested user-institution relationship.
  """
  if not current_user.is_admin:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
  user_institution = await UserInstitutionController.get_by_ids(id_user, id_institution, session)
  if not user_institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")
  return user_institution

@router.get("/me",
            response_model= List[UserInstitutionPublic],
            summary="List all user-institution relationships for the current user",
            description="""
            Retrieves a list of all user-institution relationships for the current user.

            Returns:
                List of UserInstitutionPublic objects
            """
            )    
async def get_user_institutions_me(current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Get all user-institution relationships for the current user.
  
  Returns:
      List[UserInstitutionPublic]: A list of all user-institution relationships for the current user
  """
  return await UserInstitutionController.get_by_user(current_user.id_user, session)

@router.get("/institution/{id_institution}",
            response_model=List[UserInstitutionPublic],
            summary="List all user-institution relationships for an institution",
            description="""
            Retrieves a list of all user-institution relationships for a specific institution.

            Args:
                id_institution (str): The UUID of the institution.

            Returns:
                List of UserInstitutionPublic objects
            """
            )
async def get_user_institutions_by_institution(id_institution: str, current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Get all user-institution relationships for a specific institution.
  
  Args:
      id_institution (str): The UUID of the institution.
  
  Returns:
      List[UserInstitutionPublic]: A list of all user-institution relationships for the specified institution
  """
  user_institution = await UserInstitutionController.get_by_ids(current_user.id_user, id_institution, session)
  if not user_institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")
  if not current_user.is_admin or user_institution.user_rol != 'editor':
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
  return await UserInstitutionController.get_by_institution(id_institution, session)

@router.post("/", 
             response_model=UserInstitutionPublic, 
             summary="Create a new user-institution relationship", 
             description="""
             Creates a new user-institution relationship between a user and an institution.

             Args:
                 user_institution (UserInstitutionCreate): The user-institution relationship to be created

             Returns:
                 UserInstitutionPublic: The created user-institution relationship.
             Raises:
                 HTTPException: 403 if the current user is not an admin
                 HTTPException: 404 if the user or institution is not found
                 HTTPException: 404 if the user-institution relationship already exists
             """
             )
async def create_user_institution(user_institution: UserInstitutionCreate, current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Create a new user-institution relationship.
  
  Args:
      user_institution (UserInstitutionCreate): The user-institution relationship to be created
  
  Returns:
      UserInstitutionPublic: The created user-institution relationship.
  
  Raises:
      HTTPException: 403 if the current user is not an admin
      HTTPException: 404 if the user or institution is not found
      HTTPException: 409 if the user-institution relationship already exists
  """
  if not current_user.is_admin:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
  return await UserInstitutionController.create(user_institution, session)

@router.delete("/user/{id_user}/institution/{id_institution}", 
               summary="Delete a user-institution relationship", 
               description="""
               Deletes a user-institution relationship between a user and an institution.

               Args:
                   id_user (str): The UUID of the user.
                   id_institution (str): The UUID of the institution.

               Returns:
                   dict: Confirmation message
               Raises:
                   HTTPException: 403 if the current user is not an admin
                   HTTPException: 404 if the user or institution is not found
                   HTTPException: 404 if the user-institution relationship already exists
               """
               )
async def delete_user_institution(id_user: str, id_institution: str, current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Delete a user-institution relationship.
  
  Args:
      id_user (str): The UUID of the user.
      id_institution (str): The UUID of the institution.
  
  Returns:
      dict: Confirmation message
  Raises:
      HTTPException: 403 if the current user is not an admin
      HTTPException: 404 if the user or institution is not found
      HTTPException: 404 if the user-institution relationship already exists
  """
  if not current_user.is_admin:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
  return await UserInstitutionController.delete(id_user, id_institution, session)

@router.put("/",
              response_model=UserInstitution,
              summary="Update a user-institution relationship",
              description="""
              Updates a user-institution relationship between a user and an institution.

              Args:
                user_institution (UserInstitutionUpdate): The user-institution relationship to be updated

              Returns:
                  UserInstitutionPublic: The updated user-institution relationship.
              
              Raises:
                HTTPException: 403 if the current user is not an admin
                HTTPException: 403 if the current user is not an admin of the institution
                HTTPException: 404 if the user or institution is not found
                """
              )
async def update_user_institution(user_institution: UserInstitutionUpdate, current_user : Annotated[User, Depends(get_current_user)], session = Depends(get_session)):
  """
  Update a user-institution relationship.
  
  Args:
      user_institution (UserInstitutionUpdate): The user-institution relationship to be updated
  
  Returns:
      UserInstitutionPublic: The updated user-institution relationship.
  """
    
  user_institution_db = await UserInstitutionController.get_by_ids(user_institution.id_user, user_institution.id_institution, session)
  if not user_institution_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")

  if not current_user.is_admin and current_user.id_user != user_institution.id_user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
  return await UserInstitutionController.update(user_institution, session)