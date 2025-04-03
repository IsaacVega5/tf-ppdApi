from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from typing import Annotated

from app.db import get_session
from app.models.User import User, UserCreate
from app.controllers import UserController
from app.utils.auth import get_current_user, verify_token

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
  # dependencies=[Depends(verify_token)],
)

@router.get("/")
async def get_users(session = Depends(get_session)):
  users = UserController.get_all(session)
  return users

@router.get("/me")
async def get_user_me(current_user : Annotated[User, Depends(get_current_user)]):
  return current_user

@router.get("/{id}", dependencies=[Depends(verify_token)])
async def get_user(id, session = Depends(get_session)):
  user = UserController.get_by_id(id, session)
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  return user

@router.delete("/{id}")
async def delete_user(id, session = Depends(get_session)):
  return UserController.delete_user(id, session)

@router.post("/")
async def post_user(user: UserCreate, session = Depends(get_session)):
  return UserController.create_user(user, session)
