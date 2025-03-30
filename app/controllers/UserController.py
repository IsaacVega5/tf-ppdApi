from fastapi import HTTPException, status
from sqlmodel import Session
from app.utils.auth import get_password_hash, verify_password

import sqlmodel as sql

from app.models.User import UserCreate, User, UserLogin

def create_user(user: UserCreate, session: Session):
    # Primero verificar si el email ya existe
    existing_user = session.exec(
        sql.select(User).where(User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Hash de la contraseña
    user.password = get_password_hash(user.password)
    
    new_user = User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_all(session : Session):
  statement = sql.select(User)
  users = session.exec(statement).all()
  return users

def get_by_id(id: int, session : Session):
  statement = sql.select(User).where(User.id_user == id)
  user = session.exec(statement).first()
  return user

def login(user: UserLogin, session : Session):
  #TODO: Use JWT
  statement = sql.select(User).where(User.email == user.email)
  db_user = session.exec(statement).first()
  if not db_user or not verify_password(user.password, db_user.password):
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or password")
  
  return db_user

def delete_user(id: str, session: Session):
    # Primero verificar si el usuario existe
    user = session.get(User, id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found"
        )
    
    # Si existe, proceder con la eliminación
    statement = sql.delete(User).where(User.id_user == id)
    session.exec(statement)
    session.commit()
    return {"message": f"User was deleted successfully"}