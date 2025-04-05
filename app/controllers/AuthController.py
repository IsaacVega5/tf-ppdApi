from fastapi import HTTPException, status
from sqlmodel import Session

from app.utils.auth import verify_password, generate_access_token, generate_refresh_token
from app.models.User import User, UserLogin
from app.models.Auth import Token

import sqlmodel as sql

def login(user: UserLogin, session : Session):
  statement = sql.select(User).where(User.username == user.username)
  db_user = session.exec(statement).first()
  if not db_user or not verify_password(user.password, db_user.password):
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or password")

  token_payload = {
     "sub": db_user.username,
     "email": db_user.email
  }
  access_token = generate_access_token(token_payload)
  refresh_token = generate_refresh_token(token_payload)
  
  login_token_response = Token(
    access_token=access_token,
    refresh_token=refresh_token,
    token_type="bearer"
  )

  return login_token_response

def refresh_token(username: str, session: Session):
   # puedo hacerlo con el payload del token anterior, pero si cambio el payload entre acces y refresh token puede cagar todo.
   # puedo hacerlo con un get_user por refresh_token, pero no creo que sea corecto, el refresh token solo sirve para generar un nuevo access token
   # podría hacer el get_user genérico y hacer un get_user(token_type:str) o un get_current_user y un get_refresh_user
   
   statement = sql.select(User).where(User.username == username)
   db_user = session.exec(statement).first()
   if not db_user:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")

   token_payload = {
      "sub": db_user.username,
      "email": db_user.email
   }
   access_token = generate_access_token(token_payload)
   refresh_token = generate_refresh_token(token_payload)
   
   login_token_response = Token(
      access_token=access_token,
      refresh_token=refresh_token,
      token_type="bearer"
   )

   return login_token_response