from fastapi import APIRouter, Depends, Request

from app.db import get_session
from app.models.User import User

router = APIRouter(
  prefix="/user",
  tags=["user"],
  responses={404: {"description": "Not found"}}
)

@router.get("/")
async def get_users(session = Depends(get_session), request : Request = None):
  users = session.query(User).all()
  return users

@router.get("/{id}")
async def get_user(id, session = Depends(get_session)):
  user = session.query(User).get(id)
  return user