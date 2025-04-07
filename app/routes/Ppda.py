from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from app.db import get_session
from app.models import Ppda, PpdaCreate, PpdaUpdate
from app.controllers import InstitutionController, PpdaController
from app.utils.auth import verify_access_token

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/ppda",
  tags=["ppda"],
  dependencies=[Depends(verify_access_token)],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "Ppda not found"},
    status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "Ppda already exists"}
  }
)

@router.get("/",
            response_model=List[Ppda],
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
async def get_ppda_by_id(id:str, session = Depends(get_session)):
  """Retrieves a single ppda by its ID.
    Args:
        id (str): The UUID of the ppda to retrieve.
    
    Returns:
        Ppda: The requested ppda object.
  """
  ppda = await PpdaController.get_by_id(id, session)
  if not ppda:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")
  return ppda

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
async def create_ppda(ppda: PpdaCreate, session = Depends(get_session)):
  """
  Create a new ppda.
  
  Args:
      ppda (Ppda): The ppda object to create.
  
  Returns:
      Ppda: The newly created ppda object.
  
  Raises:
      HTTPException: 404 if institution doesn't exist.
  """
  Institution = await InstitutionController.get_by_id(ppda.id_institution, session)
  if not Institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
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
async def update_ppda(id: str, ppda: PpdaUpdate, session = Depends(get_session)):
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
  
  ppda_db.id_institution = ppda.id_institution
  ppda = await PpdaController.update_ppda(ppda_db, session)
  return ppda

@router.delete("/{id}",
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