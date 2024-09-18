from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from curd.user import authenticate
from schemas import Token
from api.deps import get_db,getCurrentUser
from core.security import createAccessToken
from core.config import settings


router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    This endpoint allows users to obtain an access token by providing their username and password. It authenticates the user and, if successful, returns a JWT (JSON Web Token) that can be used for subsequent API requests requiring authentication.
    """
    user = authenticate(db=db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    if user.is_verfied == 0:
        raise HTTPException(status_code=400, detail="User is not verified")
    if user.is_active == 0:
        raise HTTPException(status_code=400, detail="Inactive User")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = createAccessToken(
        username=user.username, expires_delta=access_token_expires
    )

    return {"access_token": token, "token_type": "bearer"}


