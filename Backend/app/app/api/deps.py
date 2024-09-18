from db.db import SessionLocal
from fastapi import HTTPException, status, Depends
import jwt
from fastapi.security import OAuth2PasswordBearer


from sqlalchemy import func
from sqlalchemy.orm import Session
from core.config import settings
from core import security
from schemas.token import TokenPayload
from curd.user import getUserByusername

oauth2 = OAuth2PasswordBearer(tokenUrl="login/token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def getCurrentUser(db: Session = Depends(get_db), token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except ():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = getUserByusername(db=db, username=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verfied == 0:
        raise HTTPException(status_code=400, detail="User is not verified")
    if user.is_active == 0:
        raise HTTPException(status_code=400, detail="Inactive User")
    return user
