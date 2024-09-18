from passlib.context import CryptContext
import jwt
import secrets

from datetime import datetime, timedelta
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def verifyPassword(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def getPasswordHash(password: str):
    return pwd_context.hash(password)

def createAccessToken(username : str,expires_delta : timedelta):
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": username ,"exp": expire }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def getSecretKey():
    secret_key = secrets.token_hex(32)
    return secret_key