from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, getCurrentUser,adminLogin
from schemas import *
from curd.user import *


router = APIRouter()

@router.post("/create-user", response_model=UserOut, description="Only admin can ")
async def createNewUser(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
):
    user = None
    email = getUserByEmail(db=db, email=user_in.email)
    phone = getUserByPhone(db=db, phone=user_in.phone)
    if email:
        raise HTTPException(status_code=400, detail="Email already exits")
    if phone:
        raise HTTPException(status_code=400, detail="Phone number already exits")
    user = createUser(db=db, user=user_in, user_id=current_user.id)
    if user:
        return user
    raise HTTPException(status_code=400, detail="cant create an account")

@router.get(
    "/get-users/",
    response_model=UsersDisplay,
    description="Only Admin can see the every user",
)
async def getUsers(
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
):
    if current_user.type_id == 1:
        users = getAllUser(db=db)
        if users:
            return {"users": users}

@router.get("/get-all-servicehead", description="Admin can get the list of all service heads", response_model=List[UserTeamMate])
async def getAllServiceHead(db: Session = Depends(get_db), current_user: User = Depends(adminLogin)):
    service_head = displayServiceHead(db=db)
    if not service_head:
        raise HTTPException(status_code=404, detail="No service heads found")
    return service_head

@router.get("/get-all-serviceEnginner", description="Admin can get the list of all service engineer", response_model=List[UserTeamMate])
async def getAllServiceEngineer(db: Session = Depends(get_db), current_user: User = Depends(adminLogin)):
    service_engineer = displayServiceEngineer(db=db)
    if not service_engineer:
        raise HTTPException(status_code=404, detail="No service engineer found")
    return service_engineer

@router.get(
    "/get-users/type-id/{type_id}",
    description="Only admin can get list of users by type ID",
    response_model=UsersDisplay,
)
async def getUserByUserTypeID(
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
    type_id: int = Path(..., description="Type ID for filtering users by their type"),
):
    users = UsersByUserTypeID(db=db, type_id=type_id)
    if users:
            return {"users": users}

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
