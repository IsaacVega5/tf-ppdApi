
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.db import get_session

from app.models.User import UserLogin
from app.models.Auth import AuthTokenResponse
from app.controllers import AuthController
from typing import Annotated
from app.utils.auth import get_refresh_username


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect username or password"},
        status.HTTP_405_METHOD_NOT_ALLOWED: {"description": "Http method not allowed.<br><br><i>(Use POST instead)</i><br><br>"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid request data.<br><br><i>(Maybe a missing field? Check the parameters)</i>"}
    }
)

@router.post(
        "/token",
        response_model=AuthTokenResponse,
        summary="Generate a brand new token pair",
        description="Generate a new token pair by providing a valid username and password.",
        response_description="A new token pair with a acces token and an refresh token"
)
async def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session = Depends(get_session)
):
    """Generate a new token pair by providing a valid username and password"""
    
    return AuthController.login(
        UserLogin(
            username=form_data.username,
            password=str(form_data.password)),
        session)

@router.post(
        "/refresh-token",
        response_model=AuthTokenResponse,
        summary="Generate a new updated token pair",
        description="Generate a new token pair by providing a valid refresh token.<br><br>A new refresh token is generated.<br><br>The previous refresh_token gets revoked and can't be used anymore.",
        response_description="A token pair with a new access token and a new refresh token"
)
async def refresh_token(
    username : Annotated[str, Depends(get_refresh_username)],
    session = Depends(get_session)
):
    """Generate new token pair using a valid refresh token"""

    return AuthController.refresh_token(username, session)
