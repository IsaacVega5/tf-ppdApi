from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import VariableController, KpiController
from app.db import get_session
from app.models.Variable import Variable, VariableBase
from app.utils.auth import get_admin_user

router = APIRouter(
  prefix="/variable",
  tags=["variable"],
  dependencies=[Depends(get_admin_user)],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.get("/", 
            response_model=list[Variable],
            summary="List all variables",
            description="""Retrieves a complete list of all variables in the system.
            
            Returns:
                List of Variable objects with their basic information and KPI references.
            """,
            response_description="A list of all variables"
            )
async def get_variables(session = Depends(get_session)):
  """
  Get all variables endpoint.
  
  Returns every variable registered in the system.
  The list includes basic variable information and their KPI references.
  """
  variables = await VariableController.get_all_variables(session)
  return variables

@router.get("/{id}", 
            response_model=Variable,
            summary="Get variable by ID",
            description="""Retrieves detailed information about a specific variable.
            
            Args:
                id: The UUID of the variable to retrieve
                
            Returns:
                Complete Variable object including relationships
                
            Raises:
                HTTPException: 404 if variable is not found
            """,
            response_description="The requested variable details"
            )
async def get_variable(id : str, session = Depends(get_session)):
  """
  Retrieve a single variable by its unique identifier.
  
  This endpoint returns complete details about a variable including:
  - Basic information (formula, verification medium)
  - Associated KPI details
  - Historical data references
  """
  variable = await VariableController.get_variable_by_id(id, session)
  return variable

@router.post("/", 
            response_model=Variable,
            status_code=status.HTTP_201_CREATED,
            summary="Create new variable",
            description="""Creates a new variable after validating all constraints.
            
            Required checks:
            - Associated KPI must exist
            
            Returns:
                The newly created Variable object
            """,
            response_description="The created variable details"
            )
async def create_variable(variable: VariableBase, session = Depends(get_session)):
  """
  Variable creation endpoint.
  
  Before creating a new variable, the system verifies:
  1. The specified KPI exists (if a KPI reference is provided)
  
  On success, returns the complete variable record including:
  - Generated UUID
  - Formula and verification medium information
  - KPI reference
  """
  if variable.id_kpi:
    try:
      # Verify KPI exists if ID is provided
      kpi = await KpiController.get_kpi_by_id(variable.id_kpi, session)
    except HTTPException:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="KPI not found"
      )
  
  return await VariableController.create_variable(variable, session)

@router.delete("/{id}", 
              summary="Delete a variable",
              description="""Deletes a variable and all its associated history records.
              
              Safety checks:
              - Verifies variable exists
              
              Returns:
                  Success message with deletion confirmation
              """,
              response_description="Deletion confirmation message"
              )
async def delete_variable(id: str, session = Depends(get_session)):
  """
  Variable deletion endpoint.
  
  Performs cascading deletion of:
  1. The variable record
  2. Any associated history records
  
  On success, returns a confirmation message including:
  - The deleted variable's ID
  - Success status
  """
  return await VariableController.delete_variable(id, session)

@router.put("/{id}", 
            response_model=Variable,
            summary="Update variable details",
            description="""Updates an existing variable's information.
            
            Validations:
            - Variable must exist
            - New KPI must exist (if changed)
            
            Returns:
                The updated Variable object
            """,
            response_description="The updated variable details"
            )
async def update_variable(id: str, variable: VariableBase, session = Depends(get_session)):
  """
  Variable modification endpoint.
  
  Supports partial updates of variable properties including:
  - Formula updates
  - Verification medium changes
  - KPI reassignment (with existence validation)
  
  Returns the complete updated variable record including all changed fields.
  """
  # Controller ya verifica que la variable exista
  if variable.id_kpi:
    try:
      # Verify KPI exists if ID is provided
      kpi = await KpiController.get_kpi_by_id(variable.id_kpi, session)
    except HTTPException:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="KPI not found"
      )
      
  return await VariableController.update_variable(id, variable, session)

@router.get("/kpi/{id_kpi}", 
            response_model=list[Variable],
            summary="Get variables by KPI ID",
            description="""Retrieves all variables associated with a specific KPI.
            
            Args:
                id_kpi: The UUID of the KPI to filter variables
                
            Returns:
                List of Variable objects belonging to the specified KPI
                
            Raises:
                HTTPException: 404 if KPI is not found
            """,
            response_description="List of variables for the specified KPI"
            )
async def get_variables_by_kpi(id_kpi: str, session = Depends(get_session)):
  """
  Retrieve all variables associated with a specific KPI.
  
  This endpoint returns:
  - All variables linked to the requested KPI
  - Empty list if no variables exist for this KPI
  
  The KPI existence is verified before retrieving variables.
  """
  try:
    # Verify KPI exists
    kpi = await KpiController.get_kpi_by_id(id_kpi, session)
  except HTTPException:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail="KPI not found"
    )
    
  variables = await VariableController.get_variables_by_kpi(id_kpi, session)
  return variables
