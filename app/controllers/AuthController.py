from fastapi import HTTPException, status
from sqlmodel import Session

from app.utils.hashing import get_hash, verify_password
from app.utils.auth import generate_access_token, generate_refresh_token
from app.models.User import User, UserLogin
from app.models.Auth import AuthTokenResponse
from app.models.RefreshToken import RefreshToken

import sqlmodel as sql

def login(user: UserLogin, session : Session):
  statement = sql.select(User).where(User.username == user.username)
  db_user = session.exec(statement).first()
  if not db_user or not verify_password(user.password, db_user.password):
     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user or password")

  return create_token_response(db_user, session)

def refresh_token(username: str, session: Session):
   statement = sql.select(User).where(User.username == username)
   db_user = session.exec(statement).first()
   if not db_user:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")

   return create_token_response(db_user, session)

def create_token_response(db_user: User, session: Session):
   token_payload = {
      "sub": db_user.username,
      "email": db_user.email
   }
   access_token = generate_access_token(token_payload)
   refresh_token, jti, expires_at = generate_refresh_token(token_payload)

   token_hash = get_hash(refresh_token)
   session.add(RefreshToken(
      id_token=jti,
      id_user=db_user.id_user,
      token_hash=token_hash.decode('utf-8'),
      expires_at=int(expires_at.timestamp()),
   ))
   session.commit()

   token_response = AuthTokenResponse(
      access_token=access_token,
      refresh_token=refresh_token,
      token_type="bearer"
   )

   return token_response