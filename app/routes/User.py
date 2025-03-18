from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address


from app.db import get_session
from app.models.User import User, UserCreate, UserLogin
from app.controllers import UserController

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.get("/")
async def get_users(session = Depends(get_session), request : Request = None):
  users = UserController.get_all(session)
  return users

@router.get("/{id}")
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

@router.post("/login")
async def login(user: UserLogin, session = Depends(get_session)):
  return UserController.login(user, session)