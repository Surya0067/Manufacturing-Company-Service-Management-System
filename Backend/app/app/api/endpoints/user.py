from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, getCurrentUser
from schemas import *
from curd.user import *


router = APIRouter()


@router.post("/create-user", response_model=UserOut, description="Only admin can ")
async def createNewUser(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user = None
    email = getUserByEmail(db=db, email=user_in.email)
    phone = getUserByPhone(db=db, phone=user_in.phone)
    if email:
        raise HTTPException(status_code=400, detail="Email already exits")
    if phone:
        raise HTTPException(status_code=400, detail="Phone number already exits")
    if current_user.type_id == 1:
        user = createUser(db=db, user=user_in, user_id=current_user.id)
    if current_user.type_id == 2 and user_in.type_id == 3:
        user = createUser(db=db, user=user_in, user_id=current_user.id)
    if user:
        return user
    raise HTTPException(status_code=400, detail="cant create an account")


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
    "/get-user/username/{username}",
    response_model=UserDisplay,
    description="User can search the user by Username",
)
async def getUsername(
    username: str = Path(..., description="Username that user want to search"),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user = getUserByusername(db=db, username=username)
    if user:
        return UserDisplay(
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            phone=user.phone,
            role=user.user_type.role,
            # report_to=user.report_to,
        )
    raise HTTPException(status_code=404, detail="User not found")


@router.get(
    "/get-users/",
    response_model=UsersDisplay,
    description="Only Admin can see the every user",
)
async def getUsers(
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    if current_user.type_id == 1:
        users = getAllUser(db=db)
        if users:
            return {"users": users}
    raise HTTPException(status_code=404, detail="User Dont have access")


@router.get(
    "/get-users/type-id/{type_id}",
    description="Only admin can get list of users by type ID",
    response_model=UsersDisplay,
)
async def getUserByUserTypeID(
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
    type_id: int = Path(..., description="Type ID for filtering users by their type"),
):
    if current_user.type_id == 1:
        users = UsersByUserTypeID(db=db, type_id=type_id)
        if users:
            return {"users": users}
    raise HTTPException(status_code=404, detail="User doesn't have access")


@router.get(
    "/get-my-teammates",
    description="Service head can see his team",
    response_model=UserTeamMates,
)
async def getMyTeamates(
    db: Session = Depends(get_db), current_user: User = Depends(getCurrentUser)
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access declined")
    users = getServiceHeadTeammates(db=db, userid=current_user.id)
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
    user_name = getUserByusername(db=db, username=details.username)
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
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
    "/update-userdetails/name",
    description="User can change their name",
    response_model=Message,
)
async def updateUserName(
    details: UserUpdateName,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user_name = getUserByusername(db=db, username=details.username)
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
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
    user_name = getUserByusername(db=db, username=details.username)
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
    user = resetPassword(db=db, details=details)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant update user")


@router.patch(
    "/update-userdetails/report_to",
    description="User can change their report_to,who act like a manager for Employee",
    response_model=Message,
)
async def updateUserReportTO(
    details: UserUpdateRepportTo,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user_name = getUserByusername(db=db, username=details.username)
    if not user_name:
        raise HTTPException(status_code=404, detail="user not found")
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
    user = updateReportto(db=db, details=details)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant update user")


@router.delete(
    "/delete-user/username/{username}", description="Admin can able to disable the user"
)
async def deleteUser(
    username: str = Path(..., description="username of the user to disable"),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user_name = getUserByusername(db=db, username=username)
    if not user_name:
        raise HTTPException(status_code=404, detail="user not found")
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
    if user_name.is_active == False:
        raise HTTPException(status_code=400, detail="user Already disabled")
    user = disableUser(db=db, username=username)
    if user:
        return user
    raise HTTPException(status_code=400, detail="cant be disabled")


@router.patch(
    "/re-active-user/{username}", description="only admin can able reactive an account"
)
async def reactiveUser(
    username: str = Path(..., description="username of the user to reactive"),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    user_name = getUserByusername(db=db, username=username)
    if not user_name:
        raise HTTPException(status_code=404, detail="user not found")
    if (
        current_user.type_id == 2 and user_name.type_id != 3
    ) or current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
    if user_name.is_active == True:
        raise HTTPException(status_code=400, detail="user Already in use")
    user = reactiveUserByUsername(db=db, username=username)
    if user:
        return user
    raise HTTPException(status_code=400, detail="cant able to reactive")
