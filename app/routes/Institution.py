
from fastapi import APIRouter, Depends, HTTPException, status

from app.controllers import InstitutionController, InstitutionTypeController
from app.db import get_session
from app.models.Institution import Institution, IntitutionCreate, IntitutionUpdate


router = APIRouter(
  prefix="/institution",
  tags=["institution"],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.get("/", description="List all institutions", response_model=list[Institution])
async def get_institutions(session = Depends(get_session)):
  institutions = await InstitutionController.get_all(session)
  return institutions

@router.get("/{id}", description="Get institution by id", response_model=Institution)
async def get_institution(id : str, session = Depends(get_session)):
  institution = await InstitutionController.get_by_id(id, session)
  if not institution:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution not found"
      )
  return institution

@router.post("/", description="Create a new institution", response_model=Institution)
async def create_institution(institution: IntitutionCreate, session = Depends(get_session)):
  intitution_type = InstitutionTypeController.get_by_id(institution.id_institution_type, session)
  if not intitution_type:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution type not found"
      )
  
  return await InstitutionController.create_institution(institution, session)

@router.delete("/{id}", description="Delete an institution")
async def delete_institution(id: str, session = Depends(get_session)):
  return await InstitutionController.delete_institution(id, session)

@router.put("/{id}", description="Update an institution", response_model=Institution)
async def update_institution(id: str, institution: IntitutionUpdate, session = Depends(get_session)):
  current_institution = await InstitutionController.get_by_id(id, session)
  if not current_institution:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, 
      detail = "Institution not found"
      )
  new_institution = await InstitutionController.update_institution(id, institution, session)
  return new_institution