from fastapi import HTTPException, status
import sqlmodel as sql

from app.controllers import InstitutionController, UserController
from app.models import UserInstitution, UserRol, UserInstitutionPublic, UserInstitutionCreate, UserInstitutionUpdate

async def get_all(session : sql.Session):
  """
  Retrieve all user-institution relationships from the database.

  This endpoint retrieves all records from the UserInstitution junction table
  and their related UserRol records. The results are transformed into a list of
  UserInstitutionPublic objects for client consumption.

  Returns:
      List[UserInstitutionPublic]: A list of user-institution records with their
          respective user roles
  """
  statement = sql.select(
    UserInstitution,
    UserRol
  ).join(UserRol)
  user_institution_list = session.exec(statement).all()
  if not user_institution_list:
    return []
  user_institution_list = [
    UserInstitutionPublic(
      id_user = user_intitution.id_user,
      id_institution = user_intitution.id_institution,
      is_active = user_intitution.is_active,
      user_rol = user_rol.user_rol_name
    ) for (user_intitution, user_rol) in user_institution_list
  ]
  return user_institution_list

async def get_by_ids(id_user : str, id_institution : str, session : sql.Session):
  """
  Retrieve a specific user-institution relationship from the database.

  This endpoint retrieves a single record from the UserInstitution junction
  table and its related UserRol record. The results are transformed into a
  UserInstitutionPublic object for client consumption.

  Args:
      id_user (str): The UUID of the user.
      id_institution (str): The UUID of the institution.

  Returns:
      UserInstitutionPublic: The user-institution relationship with its user role
      None: If the user-institution relationship is not found

  Raises:
      HTTPException: 404 if the user or institution is not found
  """
  user = UserController.get_by_id(id_user, session)
  institution = await InstitutionController.get_by_id(id_institution, session)
  if not user or not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")
  
  statement = sql.select(
    UserInstitution,
    UserRol
  ).where(UserInstitution.id_user == id_user).where(UserInstitution.id_institution == id_institution).join(UserRol)
  res = session.exec(statement).first()
  if not res:
    return None
  (user_institution, user_rol) = res
  user_institution = UserInstitutionPublic(
    id_user = user_institution.id_user,
    id_institution = user_institution.id_institution,
    is_active = user_institution.is_active,
    user_rol = user_rol.user_rol_name
  )
  return user_institution

async def get_by_user(id_user : str, session : sql.Session):
  """
  Retrieve all user-institution relationships for a specific user from the database.

  This endpoint retrieves all records from the UserInstitution junction table
  associated with a specific user and their related UserRol records. The results
  are transformed into a list of UserInstitutionPublic objects for client
  consumption.

  Args:
      id_user (str): The UUID of the user.

  Returns:
      List[UserInstitutionPublic]: A list of user-institution records with their
          respective user roles
  """
  statement = sql.select(
    UserInstitution,
    UserRol
  ).where(UserInstitution.id_user == id_user).join(UserRol)
  user_institution_list = session.exec(statement).all()
  user_institution_list = [
    UserInstitutionPublic(
      id_user = user_intitution.id_user,
      id_institution = user_intitution.id_institution,
      is_active = user_intitution.is_active,
      user_rol = user_rol.user_rol_name
    ) for (user_intitution, user_rol) in user_institution_list
  ]
  return user_institution_list

async def get_by_institution(id_institution : str, session : sql.Session):
  """
  Retrieve all user-institution relationships for a specific institution from the database.

  This endpoint retrieves all records from the UserInstitution junction table
  associated with a specific institution and their related UserRol records. The
  results are transformed into a list of UserInstitutionPublic objects for client
  consumption.

  Args:
      id_institution (str): The UUID of the institution.

  Returns:
      List[UserInstitutionPublic]: A list of user-institution records with their
          respective user roles
  
  Raises:
      HTTPException: 404 If the institution is not found
  """
  institution = await InstitutionController.get_by_id(id_institution, session)
  
  if not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")
  
  statement = sql.select(
    UserInstitution,
    UserRol
  ).where(UserInstitution.id_institution == id_institution).join(UserRol)
  user_institution_list = session.exec(statement).all()
  user_institution_list = [
    UserInstitutionPublic(
      id_user = user_intitution.id_user,
      id_institution = user_intitution.id_institution,
      is_active = user_intitution.is_active,
      user_rol = user_rol.user_rol_name
    ) for (user_intitution, user_rol) in user_institution_list
  ]
  return user_institution_list

async def create(user_institution: UserInstitutionCreate, session : sql.Session):
  """
  Create a new user-institution relationship in the database.

  This endpoint creates a new record in the UserInstitution junction table and
  its related UserRol record. The results are transformed into a
  UserInstitutionPublic object for client consumption.

  Args:
      user_institution (UserInstitutionCreate): The user-institution relationship
          to be created

  Returns:
      UserInstitutionPublic: The created user-institution relationship with its
          user role
  
  Raises:
      HTTPException: 404 if the user or institution is not found
      HTTPException: 404 if the user-institution relationship already exists
  """
  user = UserController.get_by_id(user_institution.id_user, session)
  institution = await InstitutionController.get_by_id(user_institution.id_institution, session)
  if not user or not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")
  
  user_institution_db = await get_by_ids(user_institution.id_user, user_institution.id_institution, session)
  if user_institution_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User-institution relationship already exists")
  
  new_user_institution = UserInstitution()
  new_user_institution.id_user = user_institution.id_user
  new_user_institution.id_institution = user_institution.id_institution
  new_user_institution.id_user_rol = user_institution.id_user_rol
  session.add(new_user_institution)
  session.commit()
  session.refresh(new_user_institution)
  
  user_institution = await get_by_ids(user_institution.id_user, user_institution.id_institution, session)
  return user_institution

async def delete(id_user : str, id_institution : str, session : sql.Session):
  """
  Delete a user-institution relationship from the database.

  This endpoint deletes a record from the UserInstitution junction table and its
  related UserRol record. The results are transformed into a
  UserInstitutionPublic object for client consumption.

  Args:
      id_user (str): The UUID of the user.
      id_institution (str): The UUID of the institution.

  Returns:
      dict: Confirmation message
  
  Raises:
      HTTPException: 404 if the user or institution is not found
      HTTPException: 404 if the user-institution relationship does not exist
  """
  user = UserController.get_by_id(id_user, session)
  institution = await InstitutionController.get_by_id(id_institution, session)
  if not user or not institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or institution not found")
  
  user_institution = session.exec(
    sql.select(UserInstitution).\
      where(UserInstitution.id_user == id_user).\
      where(UserInstitution.id_institution == id_institution)
    ).first()
  if not user_institution:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User-institution relationship not found")
  session.delete(user_institution)
  session.commit()
  return {
    "message": "User-institution relationship deleted successfully"
  }
  
async def update(user_institution: UserInstitutionUpdate, session : sql.Session):
  """
  Update an existing user-institution relationship in the database.

  This function updates a record in the UserInstitution junction table and
  its related UserRol record based on the provided UserInstitutionUpdate
  data. The updated record is returned as a UserInstitutionPublic object.

  Args:
      user_institution (UserInstitutionUpdate): The partial/full data for the
          user-institution relationship to update.
      session (sql.Session): The database session for operations.

  Returns:
      UserInstitutionPublic: The updated user-institution relationship.

  Raises:
      HTTPException: 404 if the user-institution relationship is not found.
  """

  user_institution_db = session.exec(
    sql.select(UserInstitution).\
      where(UserInstitution.id_user == user_institution.id_user).\
      where(UserInstitution.id_institution == user_institution.id_institution)
  ).first()
  if not user_institution_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User-institution relationship not found")
  
  updated_user_institution = user_institution.model_dump(exclude_unset=True)
  user_institution_db.sqlmodel_update(updated_user_institution)
  session.add(user_institution_db)
  session.commit()
  session.refresh(user_institution_db)
  return user_institution_db