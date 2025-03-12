
from fastapi import APIRouter, Depends, HTTPException, Request

from app.controllers import InstitutionTypeController
from app.db import get_session
from app.models.InstitutionType import InstitutionTypeCreate, InstitutionTypeUpdate

router = APIRouter(
  prefix="/institution-type",
  tags=["institution-type"],
  responses={404: {"description": "Not found"}}
)

@router.get("/")
def get_institution_type( session = Depends(get_session), request : Request = None ):
  institution_types = InstitutionTypeController.get_all(session)
  return institution_types

@router.get("/{id}")
async def get_institution_type(id, session = Depends(get_session)):
  institution_type = InstitutionTypeController.get_by_id(id, session)
  if not institution_type:
    return HTTPException(status_code=404, detail="Institution type not found")
  return institution_type

@router.post("/")
async def post_institution_type(institution_type: InstitutionTypeCreate, session = Depends(get_session)):
  return InstitutionTypeController.create_institution_type(institution_type, session)

@router.delete("/{id}")
async def delete_institution_type(id, session = Depends(get_session)):
  return InstitutionTypeController.delete_institution_type(id, session)

@router.put("/{id}")
async def update_institution_type(id, institution_type: InstitutionTypeUpdate, session = Depends(get_session)):
  return InstitutionTypeController.update_institution_type(id, institution_type, session)