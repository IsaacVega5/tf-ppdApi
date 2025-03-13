
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import InstitutionTypeController
from app.db import get_session
from app.models.InstitutionType import InstitutionTypeCreate, InstitutionTypeUpdate, InstitutionType

router = APIRouter(
  prefix="/institution-type",
  tags=["institution-type"],
  responses={404: {"description": "Not found"}}
)

@router.get("/", description="List all institution types", response_model=list[InstitutionType])
def get_institution_type( session = Depends(get_session)):
  institution_types = InstitutionTypeController.get_all(session)
  return institution_types

@router.get("/{id}", description="Get institution type by id", response_model=InstitutionType)
async def get_institution_type(id : int, session = Depends(get_session)):
  institution_type = InstitutionTypeController.get_by_id(id, session)
  if not institution_type:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution type not found")
  return institution_type

@router.post("/", description="Create a new institution type", response_model=InstitutionType)
async def post_institution_type(institution_type: InstitutionTypeCreate, session = Depends(get_session)):
  return InstitutionTypeController.create_institution_type(institution_type, session)

@router.delete("/{id}", description="Delete an institution type")
async def delete_institution_type(id: int, session = Depends(get_session)):
  return InstitutionTypeController.delete_institution_type(id, session)

@router.put("/{id}", description="Update an institution type", response_model=InstitutionType)
async def update_institution_type(id: int, institution_type: InstitutionTypeUpdate, session = Depends(get_session)):
  return InstitutionTypeController.update_institution_type(id, institution_type, session)