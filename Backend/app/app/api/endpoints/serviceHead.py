from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, getCurrentUser, serviceHeadLogin
from schemas import *
from curd.user import *
from curd.ticket import *
from models import *

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


@router.get("/get-service-engineer/{service_engineer_username}")
async def getServiceEngneer(
    service_engineer_username: str = Path(
        ..., description="username that service want to search"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    users = getServiceEngineerInHead(
        db=db,
        service_engineer_username=service_engineer_username,
        user_id=current_user.id,
    )
    if users:
        return dict(users=users)
    raise HTTPException(status_code=400, detail="cant able to get teammates")


@router.patch(
    "/update-service-engineer-details/contact",
    description="user can update thier contact",
)
async def updateUserContact(
    details: UserUpdateContact,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    service_engineer = getUserByusername(db=db, username=details.username)
    if service_engineer:
        if service_engineer.is_active == False:
            raise HTTPException(status_code=400, detail="service is inactive")
        if service_engineer.report_to == current_user.id:
            if details.phone:
                phone = getUserByPhone(db=db, phone=details.phone)
                if phone:
                    raise HTTPException(
                        status_code=400, detail="Phone Number already exits"
                    )
            if details.email:
                email = getUserByEmail(db=db, email=details.email)
                if email:
                    raise HTTPException(status_code=400, detail="Email already exits")
            user = updateContact(db=db, details=details)
            if user:
                return user
        raise HTTPException(status_code=400, detail="Service engineer not under you")
    raise HTTPException(status_code=404, detail="Service engineer not found")


@router.patch(
    "/update-service-engineer-details/full-name",
    description="User can change their name",
    response_model=Message,
)
async def updateUserFullName(
    details: UserUpdateName,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    service_engineer = getUserByusername(db=db, username=details.username)
    if service_engineer:
        if service_engineer.is_active == False:
            raise HTTPException(status_code=400, detail="service is inactive")
        if service_engineer.report_to == current_user.id:
            user = updateName(db=db, details=details)
            if user:
                return user
        raise HTTPException(status_code=400, detail="Service engineer not under you")
    raise HTTPException(status_code=404, detail="Service engineer not found")


@router.patch(
    "/update-Service-engineer-details/password",
    description="Service head can change thier service engineer password",
    response_model=Message,
)
async def updateUserPassword(
    details: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    service_engineer = getUserByusername(db=db, username=details.username)
    if service_engineer:
        if service_engineer.is_active == False:
            raise HTTPException(status_code=400, detail="service is inactive")
        if service_engineer.report_to == current_user.id:
            user = resetPassword(db=db, details=details)
            if user:
                return user
        raise HTTPException(status_code=400, detail="Service engineer not under you")
    raise HTTPException(status_code=404, detail="Service engineer not found")


@router.post(
    "/update-labour-cost",
    description="We can update the labour cost after the completion of ticket process",
    response_model=Message,
)
async def addLabourCost(
    details: TicketLabourCost,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket_process = getTicketProcess(db=db, ticket_id=details.ticket_id)
    if not ticket_process:
        raise HTTPException(404, "ticket is not in ticket process")
    if not ticket_process.status in ["completed", "cancelled"]:
        raise HTTPException(400, "ticket id either in process or cancelled")
    if current_user.id != ticket_process.user.report_to:
        raise HTTPException(400, "this ticket is under some other service head")
    if ticket_process.labour_cost:
        raise HTTPException(409, "labour cost already added")
    labour_cost = addLabourCost(db=db, details=details)
    if labour_cost:
        return labour_cost
