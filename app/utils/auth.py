import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from app.db import get_session

from jwt.exceptions import InvalidTokenError

from app.models.Auth import TokenData
from app.controllers import UserController
from app.models.RefreshToken import RefreshToken

import uuid
import sqlmodel as sql

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
refresh_token_expire_days = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def generate_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=secret_key,
        algorithm=algorithm
    )

    return encoded_jwt

def generate_refresh_token(data: dict, expires_at: datetime | None = None):
    to_encode = data.copy()
    if expires_at:
        expire = expires_at
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
    jti = str(uuid.uuid4())
    to_encode.update({
        "exp": expire,
        "jti": jti,
        "token_type": "refresh"
    })
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=secret_key,
        algorithm=algorithm
    )
    return encoded_jwt, jti, expire

async def verify_token_by_type(token: Annotated[str, Depends(oauth2_scheme)], token_type: str):
    # TODO: valdrá la pena validar que token_type sea access o refresh, y qué error arrojaría si no.
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )
        if payload.get("token_type") != token_type:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return payload

async def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    return await verify_token_by_type(token=token, token_type="access")

async def verify_refresh_token(token: Annotated[str, Depends(oauth2_scheme)], session: sql.Session):
    payload = await verify_token_by_type(token=token, token_type="refresh")

    token_jti = payload.get("jti")
    if not token_jti:
        raise HTTPException(status_code=401, detail="Refresh token missing identifier")
    
    statement = sql.select(RefreshToken).where(RefreshToken.id_token == token_jti)
    db_token = session.exec(statement).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    if not bcrypt.checkpw(token.encode('utf-8'), db_token.token_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if db_token.expires_at < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    if db_token.used or db_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token is no longer valid")

    db_token.used = True
    session.commit()

    return payload

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session = Depends(get_session)
):    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    payload = await verify_access_token(token=token)
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    token_data = TokenData(username=username)

    user = UserController.get_by_username(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session = Depends(get_session)
):    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    not_admin_exception = HTTPException(
        status_code=401,
        detail="User is not admin"
    )

    payload = await verify_access_token(token=token)
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    token_data = TokenData(username=username)

    user = UserController.get_by_username(token_data.username, session)
    if user is None:
        raise credentials_exception
    if user.is_admin != True:
        raise not_admin_exception
    return user

async def get_refresh_username(
        token: Annotated[str, Depends(oauth2_scheme)],
        session = Depends(get_session)
):    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    payload = await verify_refresh_token(token, session)
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    return username

# async def get_current_active_user(
#         current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user