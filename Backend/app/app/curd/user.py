from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import verifyPassword, getPasswordHash
from models import User, UserType
from schemas import UserCreate, UserTypeIn


def getUserByusername(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def getUserByID(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def getEmployeecount(db: Session, type_id: int):
    return db.query(User).filter(User.type_id == type_id).count()


def createUser(db: Session, user=UserCreate):
    if user.type_id == 1:
        count = getEmployeecount(db=db, type_id=1)
        username = f"admin{count + 1}"
    elif user.type_id == 2:
        count = getEmployeecount(db=db, type_id=2)
        username = f"serHed{count+1}"
    elif user.type_id == 3:
        count = getEmployeecount(db=db, type_id=3)
        username = f"serEng{count+1}"
    else:
        raise HTTPException(status_code=404, detail="User type not found")
    password = getPasswordHash(password=username)
    new_user = User(
        full_name=user.full_name,
        username=username,
        password=password,
        email=user.email,
        phone=user.phone,
        type_id=user.type_id,
    )
    db.add(new_user)
    db.commit()
    return dict(message="User Created", username=username, password=username)

def updatePassword(db : Session,old_password : str,new_password : str,user_id : int):
    user = getUserByID(db=db,user_id=user_id)
    if user:
        if verifyPassword(plain_password=old_password,hashed_password=user.password):
            password = getPasswordHash(new_password)
            user.password = password
            db.commit()
            db.refresh(user)
            return dict(message = "password Updated")
        raise HTTPException(status_code=400,detail="Password Wrong")
        
    raise HTTPException(status_code=404,detail="user not found")


def authenticate(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verifyPassword(password, user.password):
        raise HTTPException(status_code=400, detail="Invaild user name or password")
    return user
