from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException
from core.security import verifyPassword, getPasswordHash
from models import User, UserType
from schemas import *


def getUserByusername(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def getUserByID(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def getUserByEmail(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def getUserByPhone(db: Session, phone: str):
    return db.query(User).filter(User.phone == phone).first()


def getEmployeecount(db: Session, type_id: int):
    return db.query(User).filter(User.type_id == type_id).count()


def getAllUser(db: Session):
    report_to_alias = aliased(User)
    users = (
        db.query(User, report_to_alias.username.label("report_to_username"))
        .outerjoin(report_to_alias, User.report_to == report_to_alias.id)
        .order_by(User.type_id)
        .all()
    )
    if users:
        return displayUserResponse(users)
    raise HTTPException(status_code=400, detail="There is no user")


def displayServiceHead(db: Session):
    users = db.query(User).filter(User.type_id == 2, User.is_active == True).all()
    if users:
        return displayUserTeammatesResponse(users)
    raise HTTPException(status_code=400, detail="There is no user")


def displayServiceEngineer(db: Session):
    users = db.query(User).filter(User.type_id == 3, User.is_active == True).all()
    if users:
        return displayUserTeammatesResponse(users)
    raise HTTPException(status_code=400, detail="There is no user")


def UsersByUserTypeID(db: Session, type_id: int):
    report_to_alias = aliased(User)
    users = (
        db.query(User, report_to_alias.username.label("report_to_username"))
        .outerjoin(report_to_alias, User.report_to == report_to_alias.id)
        .filter(User.type_id == type_id)
        .all()
    )
    if users:
        return displayUserResponse(users)
    raise HTTPException(status_code=400, detail="There is no user")


def displayUserResponse(users):
    return [
        UserDisplay(
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.user_type.role,
            username=user.username,
            report_to=report_to_username if report_to_username else None,
        )
        for user, report_to_username in users
    ]


def getServiceHeadTeammates(db: Session, userid: int):
    users = (
        db.query(User).filter(User.report_to == userid, User.is_active == True).all()
    )
    if users:
        return displayUserTeammatesResponse(users)
    raise HTTPException(status_code=400, detail="There is no user")


def getServiceEngineerInHead(db: Session, service_engineer_username: str, user_id: int):
    service_engineer = (
        db.query(User)
        .filter(User.username == service_engineer_username, User.report_to == user_id)
        .first()
    )
    if service_engineer:
        return UserTeamMate(
            username=service_engineer.username,
            full_name=service_engineer.full_name,
            email=service_engineer.email,
            phone=service_engineer.phone,
            role=service_engineer.user_type.role,
        )
    raise HTTPException(status_code=404, detail="service engineer not found")


def displayUserTeammatesResponse(users):
    return [
        UserTeamMate(
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role=user.user_type.role,
        )
        for user in users
    ]


def createUser(db: Session, user: UserCreate, user_id: int):
    # Generate a unique username based on the user type
    if user.type_id == 1:  # Admin
        count = getEmployeecount(db=db, type_id=1)
        username = f"admin{count + 1}"
    elif user.type_id == 2:  # Service Head
        count = getEmployeecount(db=db, type_id=2)
        username = f"serHed{count + 1}"
    elif user.type_id == 3:  # Service Engineer
        count = getEmployeecount(db=db, type_id=3)
        username = f"serEng{count + 1}"
    else:
        raise HTTPException(status_code=404, detail="User type not found")

    report_to_user = getUserByusername(db=db, username=user.report_to)
    if report_to_user:
        if (
            user.type_id == 1
            and report_to_user is not None
            and report_to_user.type_id != 1
        ):
            raise HTTPException(
                status_code=400, detail="Admin must report to another admin or no one."
            )

        elif user.type_id == 2 and report_to_user.type_id != 1:
            raise HTTPException(
                status_code=400, detail="Service Head must report to an admin."
            )

        elif user.type_id == 3 and report_to_user.type_id not in [1, 2]:
            raise HTTPException(
                status_code=400,
                detail="Service Engineer must report to a Service Head or Admin.",
            )
    new_user = User(
        full_name=user.full_name,
        username=username,
        password=getPasswordHash(password=user.password),
        email=user.email,
        report_to=report_to_user.id,
        phone=user.phone,
        type_id=user.type_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return dict(message="User created successfully", username=username)


def updatePassword(db: Session, old_password: str, new_password: str, user_id: int):
    user = getUserByID(db=db, user_id=user_id)
    if user:
        if verifyPassword(plain_password=old_password, hashed_password=user.password):
            password = getPasswordHash(new_password)
            user.password = password
            db.commit()
            db.refresh(user)
            return dict(message="password Updated")
        raise HTTPException(status_code=400, detail="Password Wrong")

    raise HTTPException(status_code=404, detail="user not found")


def updateContact(db: Session, details: UserUpdateContact):
    user = getUserByusername(db=db, username=details.username)
    if user:
        if details.phone is not None:
            user.phone = details.phone
        if details.email is not None:
            user.email = details.email
        db.commit()
        db.refresh(user)
        return dict(message="Update successfully")
    raise HTTPException(status_code=404, detail="Username not found")


def updateName(db: Session, details: UserUpdateName):
    user = getUserByusername(db=db, username=details.username)
    if user:
        user.full_name = details.name
        db.commit()
        db.refresh(user)
        return dict(message="Update successfully")
    raise HTTPException(status_code=404, detail="Username not found")


def resetPassword(db: Session, details: UserUpdatePassword):
    user = getUserByusername(db=db, username=details.username)
    if user:
        user.password = getPasswordHash(password=details.password)
        db.commit()
        db.refresh(user)
        return dict(message="Update successfully")
    raise HTTPException(status_code=404, detail="Username not found")


def updateReportto(db: Session, details: UserUpdateRepportTo):
    user = getUserByusername(db=db, username=details.username)
    report_to_user = getUserByusername(db=db, username=details.report_to)
    if not report_to_user:
        raise HTTPException(status_code=404, detail="report to - user not found")
    if user.type_id == 1 and report_to_user is not None and report_to_user.type_id != 1:
        raise HTTPException(
            status_code=400, detail="Admin must report to another admin or no one."
        )

    elif user.type_id == 2 and report_to_user.type_id != 1:
        raise HTTPException(
            status_code=400, detail="Service Head must report to an admin."
        )

    elif user.type_id == 3 and report_to_user.type_id not in [1, 2]:
        raise HTTPException(
            status_code=400,
            detail="Service Engineer must report to a Service Head or Admin.",
        )
    if user:
        user.report_to = report_to_user.id
        db.commit()
        db.refresh(user)
        return dict(message="Update successfully")
    raise HTTPException(status_code=404, detail="Username not found")


def disableUser(db: Session, username: str):
    user = getUserByusername(db=db, username=username)
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
        return dict(message="disabled  User")
    raise HTTPException(status_code=404, detail="Username not found")


def reactiveUserByUsername(db: Session, username: str):
    user = getUserByusername(db=db, username=username)
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
        return dict(message="User reactived")
    raise HTTPException(status_code=404, detail="Username not found")


def authenticate(db: Session, username: str, password: str):
    user = getUserByusername(db=db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verifyPassword(password, user.password):
        raise HTTPException(status_code=400, detail="Invaild user name or password")
    return user
