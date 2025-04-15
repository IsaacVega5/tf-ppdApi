from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from app.db import get_session
from app.models import Ppda, PpdaCreate, PpdaUpdate, User
from app.controllers import InstitutionController, PpdaController
from app.utils.auth import get_admin_user, get_current_user
from app.utils.rbac import verify_institution_role

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/ppda",
  tags=["ppda"],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "Ppda not found"},
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "Ppda already exists"}
  }
)

@router.get("/",
            response_model=List[Ppda],
            dependencies=[Depends(get_admin_user)],
            summary="List all ppda",
            description="""Retrieves a list of all registered ppda in the system.
            
            Returns:
                List of Ppda objects with sensitive fields omitted
            """,
            response_description="List of all ppda"
            )
async def get_ppda(session = Depends(get_session)):
  """
  Get all ppda.
  
  Returns:
      List[Ppda]: A list of all registered ppda.
  """
  ppda = await PpdaController.get_all(session)
  return ppda

@router.get("/{id}",
            response_model=Ppda,
            summary="Get ppda by ID",
            description="""Retrieves a single ppda by its ID.
            
            Args:
                id (str): The UUID of the ppda to retrieve.
            
            Returns:
                Ppda: The requested ppda object.
            """,
            response_description="The requested ppda object"
            )
async def get_ppda_by_id(
  id: str,
  user : Annotated[User, Depends(get_current_user)],
  session = Depends(get_session)
):
  """Retrieves a single ppda by its ID.
    Args:
        id (str): The UUID of the ppda to retrieve.
    
    Returns:
        Ppda: The requested ppda object.
  """
  ppda = await PpdaController.get_by_id(id, session)
  
  if not ppda:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")

  verify_institution_role(
    institution_id=ppda.id_institution,
    required_role="viewer",
    current_user=user,
    session=session
  )

  return ppda

# TODO: Get all MY ppda's
# TODO: Get all ppda's by institution

@router.post("/",
             response_model=Ppda,
             summary="Create a new ppda",
             description="""Creates a new ppda in the system.
             
             Args:
                 ppda (Ppda): The ppda object to create.
             
             Returns:
                 Ppda: The newly created ppda object.
             """,
             response_description="The newly created ppda object"
            )
async def create_ppda(
  ppda: PpdaCreate,
  user : Annotated[User, Depends(get_current_user)],
  session = Depends(get_session)):
  """
  Create a new ppda.
  
  Args:
      ppda (Ppda): The ppda object to create.
  
  Returns:
      Ppda: The newly created ppda object.
  
  Raises:
      HTTPException: 404 if institution doesn't exist.
  """
  institution = await InstitutionController.get_by_id(ppda.id_institution, session)
  if not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
  
  verify_institution_role(
    institution_id=institution.id_institution,
    required_role="editor",
    current_user=user,
    session=session
  )

  ppda = await PpdaController.create_ppda(ppda, session)
  return ppda

@router.put("/{id}",
            response_model=Ppda,
            summary="Update ppda by ID",
            description="""Updates an existing ppda by its ID.
            
            Args:
                id (str): The UUID of the ppda to update.
                ppda (Ppda): The updated ppda object.
            
            Returns:
                Ppda: The updated ppda object.
            """,
            response_description="The updated ppda object"
            )
async def update_ppda(
  id: str,
  ppda: PpdaUpdate,
  user: Annotated[User, Depends(get_current_user)],
  session = Depends(get_session)
):
  """Updates an existing ppda by its ID.
    Args:
        id (str): The UUID of the ppda to update.
        ppda (Ppda): The updated ppda object.
    
    Returns:
        Ppda: The updated ppda object.
    
    Raises:
        HTTPException: 404 if ppda not found.
        HTTPException: 404 if institution not found.
  """
  ppda_db = await PpdaController.get_by_id(id, session)
  if not ppda_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")
  
  institution = await InstitutionController.get_by_id(ppda.id_institution, session)
  if not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
  
  verify_institution_role(
    institution_id=[ppda.id_institution, ppda_db.id_institution],
    current_user=user,
    required_role="editor",
    session=session
  )
  
  ppda_db.id_institution = ppda.id_institution

  ppda = await PpdaController.update_ppda(ppda_db, session)
  return ppda

@router.delete("/{id}",
               dependencies=[Depends(get_admin_user)],
               summary="Delete ppda by ID",
               description="""Deletes an existing ppda by its ID.
            
            Args:
                id (str): The UUID of the ppda to delete.
            
            Returns:
                dict: Confirmation message.
                
            Raises:
                HTTPException: 404 if ppda not found
            """,
               response_description="None"
               )
async def delete_ppda(id: str, session = Depends(get_session)):
  """Deletes an existing ppda by its ID.
    Args:
        id (str): The UUID of the ppda to delete.
    
    Returns:
        dict: Confirmation message.
    Raises:
        HTTPException: 404 if ppda not found
  """
  ppda = await PpdaController.get_by_id(id, session)
  if not ppda:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")
  return await PpdaController.delete_ppda(id, session)