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

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expire_minutes = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
refresh_token_expire_days = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=bcrypt.gensalt())
    return hashed_password

def generate_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=secret_key,
        algorithm=algorithm
    )

    return encoded_jwt

def generate_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=secret_key,
        algorithm=algorithm
    )
    return encoded_jwt

async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]):
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
    except InvalidTokenError:
        raise credentials_exception
    return payload


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session = Depends(get_session)
):    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )

    payload = await verify_token(token)
    username = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    token_data = TokenData(username=username)

    user = UserController.get_by_username(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


# async def get_current_active_user(
#         current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user