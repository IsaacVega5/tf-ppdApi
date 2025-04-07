
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import InstitutionTypeController
from app.db import get_session
from app.models.InstitutionType import InstitutionTypeCreate, InstitutionTypeUpdate, InstitutionType

router = APIRouter(
  prefix="/institution-type",
  tags=["institution-type"],
  responses={
    status.HTTP_404_NOT_FOUND: {"description": "Institution type not found"},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid request data"},
    status.HTTP_409_CONFLICT: {"description": "Conflict with existing data"}
  }
)

@router.get("/", 
            response_model=list[InstitutionType],
            summary="List all institution types",
            description="""Retrieves a complete list of all institution types in the system.
            
            Institution types categorize institutions (e.g., 'University', 'Hospital').
            
            Returns:
                List[InstitutionType]: All registered institution types with their IDs and names
            """,
            response_description="List of institution types"
            )
def get_institution_type( session = Depends(get_session)):
  """
  Retrieve all institution types endpoint.
  
  Returns every institution type registered in the system.
  The list includes basic type information that can be used
  when creating or updating institutions.
  """
  institution_types = InstitutionTypeController.get_all(session)
  return institution_types

@router.get("/{id}",
            response_model=InstitutionType,
            summary="Get institution type by ID",
            description="""Retrieves details of a specific institution type.
            
            Args:
                id: The integer ID of the institution type to retrieve
                
            Returns:
                InstitutionType: Complete type information
                
            Raises:
                HTTPException: 404 if institution type is not found
            """,
            response_description="Institution type details"
            )
async def get_institution_type(id : int, session = Depends(get_session)):
  """
  Retrieve a single institution type by its unique identifier.
  
  This endpoint returns complete details about an institution type including:
  - Type ID (primary key)
  - Type name
  - Associated institutions count (through relationship)
  """
  institution_type = InstitutionTypeController.get_by_id(id, session)
  if not institution_type:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution type not found")
  return institution_type

@router.post("/", 
              response_model=InstitutionType,
              status_code=status.HTTP_201_CREATED,
              summary="Create new institution type",
              description="""Creates a new institution type category.
              
              Required validations:
              - Type name must not be empty
              - Type name must be unique
              
              Returns:
                  The newly created InstitutionType object with generated ID
              """,
              response_description="The created institution type"
            )
async def post_institution_type(institution_type: InstitutionTypeCreate, session = Depends(get_session)):
  """
  Institution type creation endpoint.
  
  Before creating a new institution type, the system verifies:
  1. The type name is not empty or whitespace
  2. The type name doesn't already exist
  
  On success, returns the complete type record including:
  - Generated ID (auto-increment)
  - Type name
  """
  return InstitutionTypeController.create_institution_type(institution_type, session)

@router.delete("/{id}", 
                summary="Delete an institution type",
                description="""Deletes an institution type if not in use.
                
                Safety checks:
                - Verifies type exists
                - Confirms no institutions are using this type
                
                Returns:
                    Success message with deletion confirmation
                """,
                response_description="Deletion confirmation message"
              )
async def delete_institution_type(id: int, session = Depends(get_session)):
  """
  Institution type deletion endpoint.
  
  Performs cascading checks before deletion:
  1. Verifies the type exists
  2. Ensures no institutions are currently using this type
  
  On success, returns a confirmation message including:
  - The deleted type's ID
  - Success status
  """
  return InstitutionTypeController.delete_institution_type(id, session)

@router.put("/{id}", 
            response_model=InstitutionType,
            summary="Update institution type",
            description="""Updates an existing institution type's name.
            
            Validations:
            - Institution type must exist
            - New name must not be empty
            - New name must be unique
            
            Returns:
                The updated InstitutionType object
            """,
            response_description="The updated institution type"
           )
async def update_institution_type(id: int, institution_type: InstitutionTypeUpdate, session = Depends(get_session)):
  """
  Institution type modification endpoint.
  
  Supports updating of type name with validation:
  - New name must be non-empty
  - New name must be unique
  
  Returns the complete updated type record including:
  - Original ID
  - Updated name
  """
  return InstitutionTypeController.update_institution_type(id, institution_type, session)