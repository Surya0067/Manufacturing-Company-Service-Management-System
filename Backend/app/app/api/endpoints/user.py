from fastapi import APIRouter, Body, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, getCurrentUser
from schemas import UserTypeIn, UserTypeOut, Message, UserCreate, UserOut, UserDiplay
from curd.user import *

router = APIRouter()


@router.post("/create-user", response_model=UserOut)
async def createNewUser(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    if current_user.user_type == 1:
        user = createUser(db=db, user=user_in)
    if current_user.type_id == 2 and user_in.type_id == 3 :
      user = createUser(db=db, user=user_in)
    if user:
        return user
    raise HTTPException(status_code=400, detail="cant create an account")

@router.post("/reset-password")
async def resetPassword(old_password : str = Body(...),new_password : str = Body(...) ,    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser)):
    if new_password == old_password:
        raise HTTPException(status_code=400,detail="new password can not be the same password")
    password = updatePassword(db=db,old_password=old_password,new_password=new_password,user_id=current_user.id)
    if password:
      return password
    raise HTTPException(status_code=400,detail="Cant update password")


@router.get("/get-user/{username}", response_model=UserDiplay)
async def getUser(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user = getUserByusername(db=db, username=username)
    if user:
        return UserDiplay(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.user_type.role,
        )
    raise HTTPException(status_code=404,detail="User not found")