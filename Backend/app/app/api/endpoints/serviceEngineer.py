from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, getCurrentUser,serviceHeadLogin
from schemas import *
from curd.user import *


router = APIRouter()





@router.patch(
    "/change-password",
    response_model=Message,
    description="User can change the password with the exitsing ",
)
async def changePassword(
    old_password: str = Body(..., description="Old password of the account"),
    new_password: str = Body(..., description="new password of the account"),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    if new_password == old_password:
        raise HTTPException(
            status_code=400, detail="new password can not be the same password"
        )
    password = updatePassword(
        db=db,
        old_password=old_password,
        new_password=new_password,
        user_id=current_user.id,
    )
    if password:
        return password
    raise HTTPException(status_code=400, detail="Cant update password")

@router.get(
    "/get-my-teammates",
    description="Service head can see his team",
    response_model=UserTeamMates,
)
async def getMyTeamates(
    db: Session = Depends(get_db), current_user: User = Depends(serviceHeadLogin)
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access declined")
    users = getServiceHeadTeammates(db=db, userid=current_user.id)
    if users:
        return dict(users=users)
    raise HTTPException(status_code=400, detail="cant able to get teammates")

@router.get("/get-service-engineer/")
async def getServiceEngneer(
    service_engineer_username: str ,db: Session = Depends(get_db), current_user: User = Depends(serviceHeadLogin)
):
    users = getServiceEngineerInHead(db=db, service_engineer_username=service_engineer_username,user_id=current_user.id)
    if users:
        return dict(users=users)
    raise HTTPException(status_code=400, detail="cant able to get teammates")

@router.patch(
    "/update-userdetails/contact",
    response_model=Message,
    description="user can update thier contact",
)
async def updateUserContact(
    details: UserUpdateContact,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    if details.phone:
        phone = getUserByPhone(db=db, phone=details.phone)
        if phone:
            raise HTTPException(status_code=400, detail="Phone Number already exits")
    if details.email:
        email = getUserByEmail(db=db, email=details.email)
        if email:
            raise HTTPException(status_code=400, detail="Email already exits")
    user = updateContact(db=db, details=details)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant update user")


@router.patch(
    "/update-userdetails/full-name",
    description="User can change their name",
    response_model=Message,
)
async def updateUserFullName(
    details: UserUpdateName,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user = updateName(db=db, details=details)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant update user")


@router.patch(
    "/update-userdetails/password",
    description="User can change their password",
    response_model=Message,
)
async def updateUserPassword(
    details: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user = resetPassword(db=db, details=details)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant update user")
