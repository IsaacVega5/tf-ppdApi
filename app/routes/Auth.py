
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db import get_session

from app.models.User import UserLogin
from app.controllers import AuthController
from typing import Annotated
from app.utils.auth import get_refresh_username


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

@router.post("/token")
async def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session = Depends(get_session)
):
    return AuthController.login(
        UserLogin(
            username=form_data.username,
            password=str(form_data.password)),
        session)

@router.post("/refresh-token")
async def refresh_token(
    username : Annotated[str, Depends(get_refresh_username)],
    session = Depends(get_session)
):
    return AuthController.refresh_token(username, session)

# async def expire_token():
#     pass

