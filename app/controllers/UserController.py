from fastapi import HTTPException
from sqlmodel import Session
import hashlib

import sqlmodel as sql

from app.models.User import UserCreate, User, UserLogin


def create_user(user: UserCreate, session : Session):
  user.password = hashlib.sha256(user.password.encode()).hexdigest()
  
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
  user.password = hashlib.sha256(user.password.encode()).hexdigest()
  statement = sql.select(User).where(User.email == user.email).where(User.password == user.password)
  user = session.exec(statement).first()
  if not user:
    return HTTPException(status_code=404, detail="User not found")
  
  return user

def delete_user(id: str, session : Session):
  statement = sql.delete(User).where(User.id_user == id)
  session.exec(statement)
  session.commit()
  return {"message": "User deleted"}