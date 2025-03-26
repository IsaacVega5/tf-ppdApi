import sqlmodel as sql

from app.models import Institution, InstitutionCreate, InstitutionUpdate

async def get_all(session : sql.Session):
  statement = sql.select(Institution)
  institutions = session.exec(statement).all()
  return institutions

async def get_by_id(id:str, session : sql.Session):
  statement = sql.select(Institution).\
    where(Institution.id_institution == id)
  institution = session.exec(statement).first()
  return institution

async def create_institution(institution: InstitutionCreate, session : sql.Session):
  new_institution = Institution.model_validate(institution)
  session.add(new_institution)
  session.commit()
  return await get_by_id(new_institution.id_institution, session)

async def delete_institution(id: str, session : sql.Session):
  statement = sql.delete(Institution).where(Institution.id_institution == id)
  session.exec(statement)
  session.commit()
  return {"message": "Institution deleted"}

async def update_institution(id: str, institution: InstitutionUpdate, session : sql.Session):
  changes = institution.model_dump(exclude_unset=True)
  if not changes:
    return await get_by_id(id, session)
  statement = sql.update(Institution).\
    where(Institution.id_institution == id).\
      values(changes)
  session.exec(statement)
  session.commit()
  return await get_by_id(id, session)