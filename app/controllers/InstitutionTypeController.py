from fastapi import HTTPException
from sqlmodel import Session

import sqlmodel as sql

from app.models import InstitutionType, InstitutionTypeCreate

def get_all(session : Session):
  statement = sql.select(InstitutionType)
  institution_types = session.exec(statement).all()
  return institution_types

def get_by_id(id: int, session : Session):
  statement = sql.select(InstitutionType).where(InstitutionType.id_institution_type == id)
  institution_type = session.exec(statement).first()
  return institution_type

def create_institution_type(institution_type: InstitutionTypeCreate, session : Session):
  new_institution_type = InstitutionType.model_validate(institution_type)
  session.add(new_institution_type)
  session.commit()
  session.refresh(new_institution_type)
  return new_institution_type

def delete_institution_type(id: str, session : Session):
  statement = sql.delete(InstitutionType).where(InstitutionType.id_institution_type == id)
  session.exec(statement)
  session.commit()
  return {"message": "Institution type deleted"}

def update_institution_type(id: str, institution_type: InstitutionTypeCreate, session : Session):
  statement = sql.update(InstitutionType).where(InstitutionType.id_institution_type == id).values(institution_type.model_dump())
  session.exec(statement)
  session.commit()
  return get_by_id(id, session)