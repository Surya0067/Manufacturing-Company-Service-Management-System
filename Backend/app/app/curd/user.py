from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from core.security import verifyPassword
from models import User,UserType
from schemas import UserCreate,UserTypeIn

def getUserByusername(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def createUserType(db: Session,user_type = UserTypeIn):
    db.add(UserType(
        role = user_type.role,
        description=user_type.description
    ))
    db.commit()

def createUser(db : Session,user = UserCreate):
    new_user = User(full_name = user.full_name,username = user.username,password = user.password,email = user.email,phone_number = user.phone,)


def authenticate(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verifyPassword(password, user.hashed_password):
        return None
    return user