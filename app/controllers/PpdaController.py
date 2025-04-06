from fastapi import HTTPException, status
import sqlmodel as sql
from app.models.Ppda import Ppda, PpdaCreate, PpdaUpdate

async def get_all(session : sql.Session):
  """
  Retrieves all ppda from the database.
  
  Args:
      session (Session): Database session for operations.
  
  Returns:
      List[Ppda]: List of all ppda objects.
  """
  statement = sql.select(Ppda)
  ppda = session.exec(statement).all()
  return ppda

async def get_by_id(id:str, session : sql.Session):
  """
  Get a single ppda by its ID.
  
  Args:
      id (str): The UUID of the ppda to retrieve.
      session (Session): Database session for operations.
  
  Returns:
      Ppda | None: The requested ppda or None if not found.
  """
  statement = sql.select(Ppda).\
      where(Ppda.id_ppda == id)
  ppda = session.exec(statement).first()
  return ppda

async def create_ppda(ppda: PpdaCreate, session: sql.Session):
  """
  Creates a new ppda in the database.
  
  Args:
      ppda (Ppda): The ppda object to create.
      session (Session): Database session for operations.
  
  Returns:
      Ppda: The newly created ppda object.
  """
  new_ppda = Ppda(**ppda.model_dump())
  session.add(new_ppda)
  session.commit()
  session.refresh(new_ppda)
  return new_ppda

async def update_ppda(ppda: Ppda, session: sql.Session):
  """
  Updates an existing ppda in the database.
  
  Args:
      id (str): The UUID of the ppda to update.
      ppda (Ppda): The updated ppda object.
      session (Session): Database session for operations.
  
  Returns:
      Ppda: The updated ppda object.
  """
  db_ppda = await get_by_id(ppda.id_ppda, session)
  if not db_ppda:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")
  statement = sql.select(Ppda).\
      where(Ppda.id_ppda == ppda.id_ppda)
  existing_ppda = session.exec(statement).first()
  existing_ppda.id_institution = ppda.id_institution
  session.commit()
  session.refresh(existing_ppda)
  return existing_ppda

async def delete_ppda(id: str, session: sql.Session):
  """
  Deletes an existing ppda from the database by its ID.
  
  Args:
      id (str): The UUID of the ppda to delete.
      session (Session): Database session for operations.
  
  Returns:
      dict: Confirmation message.
  """
  db_ppda = await get_by_id(id, session)
  if not db_ppda:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ppda not found")
  statement = sql.select(Ppda).\
      where(Ppda.id_ppda == id)
  ppda = session.exec(statement).first()
  session.delete(ppda)
  session.commit()
  return {"message": "Ppda deleted successfully"}