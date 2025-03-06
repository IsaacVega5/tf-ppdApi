from fastapi import APIRouter, Depends, HTTPException, Request

from app.db import get_session
from app.models.User import User, UserCreate, UserLogin
from app.controllers import UserController

router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={404: {"description": "Not found"}}
)

@router.get("/")
async def get_users(session = Depends(get_session), request : Request = None):
  users = UserController.get_all(session)
  return users

@router.get("/{id}")
async def get_user(id, session = Depends(get_session)):
  user = UserController.get_by_id(id, session)
  if not user:
    return HTTPException(status_code=404, detail="User not found")
  return user

@router.delete("/{id}")
async def delete_user(id, session = Depends(get_session)):
  return UserController.delete_user(id, session)

@router.post("/")
async def post_user(user: UserCreate, session = Depends(get_session)):
  return UserController.create_user(user, session)

@router.post("/login")
async def login(user: UserLogin, session = Depends(get_session)):
  return UserController.login(user, session)