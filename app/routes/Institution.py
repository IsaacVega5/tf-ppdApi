
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import InstitutionController, InstitutionTypeController
from app.db import get_session
from app.models.Institution import Institution, InstitutionCreate, InstitutionUpdate
from app.utils.auth import get_admin_user

router = APIRouter(
  prefix="/institution",
  tags=["institution"],
  dependencies=[Depends(get_admin_user)],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.get("/", 
            response_model=list[Institution],
            summary="List all institutions",
            description="""Retrieves a complete list of all institutions in the system.
            
            Returns:
                List of Institution objects with their basic information and type references.
            """,
            response_description="A list of all institutions"
            )
async def get_institutions(session = Depends(get_session)):
  """
  Get all institutions endpoint.
  
  Returns every institution registered in the system regardless of type.
  The list includes basic institution information and their type references.
  """
  institutions = await InstitutionController.get_all(session)
  return institutions

@router.get("/{id}", 
            response_model=Institution,
            summary="Get institution by ID",
            description="""Retrieves detailed information about a specific institution.
            
            Args:
                id: The UUID of the institution to retrieve
                
            Returns:
                Complete Institution object including relationships
                
            Raises:
                HTTPException: 404 if institution is not found
            """,
            response_description="The requested institution details"
            )
async def get_institution(id : str, session = Depends(get_session)):
  """
  Retrieve a single institution by its unique identifier.
  
  This endpoint returns complete details about an institution including:
  - Basic information (name, creation date)
  - Institution type details
  - Associated users and relationships
  """
  institution = await InstitutionController.get_by_id(id, session)
  if not institution:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution not found"
      )
  return institution

@router.post("/", 
            response_model=Institution,
            status_code=status.HTTP_201_CREATED,
            summary="Create new institution",
            description="""Creates a new institution after validating all constraints.
            
            Required checks:
            - Institution type must exist
            - Institution name must be unique for its type
            
            Returns:
                The newly created Institution object
            """,
            response_description="The created institution details"
            )
async def create_institution(institution: InstitutionCreate, session = Depends(get_session)):
  """
  Institution creation endpoint.
  
  Before creating a new institution, the system verifies:
  1. The specified institution type exists
  2. The institution name is unique for its type category
  
  On success, returns the complete institution record including:
  - Generated UUID
  - Creation timestamp
  - Type information
  """
  intitution_type = InstitutionTypeController.get_by_id(institution.id_institution_type, session)
  if not intitution_type:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution type not found"
      )
  
  return await InstitutionController.create_institution(institution, session)

@router.delete("/{id}", 
              summary="Delete an institution",
              description="""Deletes an institution after validating it has no associated users.
              
              Safety checks:
              - Verifies institution exists
              - Confirms no users are associated
              
              Returns:
                  Success message with deletion confirmation
              """,
              response_description="Deletion confirmation message"
              )
async def delete_institution(id: str, session = Depends(get_session)):
  """
  Institution deletion endpoint.
  
  Performs cascading checks before deletion:
  1. Verifies the institution exists
  2. Ensures no users are currently associated
  
  On success, returns a confirmation message including:
  - The deleted institution's ID
  - Success status
  """
  return await InstitutionController.delete_institution(id, session)

@router.put("/{id}", 
            response_model=Institution,
            summary="Update institution details",
            description="""Updates an existing institution's information.
            
            Validations:
            - Institution must exist
            - New name must be unique for its type (if changed)
            - New type must exist (if changed)
            
            Returns:
                The updated Institution object
            """,
            response_description="The updated institution details"
            )
async def update_institution(id: str, institution: InstitutionUpdate, session = Depends(get_session)):
  """
  Institution modification endpoint.
  
  Supports partial updates of institution properties including:
  - Name changes (with uniqueness validation)
  - Type reassignment (with existence validation)
  
  Returns the complete updated institution record including:
  - All unchanged fields
  - Updated fields
  - New modification timestamp
  """
  current_institution = await InstitutionController.get_by_id(id, session)
  if not current_institution:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution not found"
      )
  new_institution = await InstitutionController.update_institution(id, institution, session)
  return new_institution