from pydantic import BaseModel
from typing import Optional, List
from fastapi import Body


# Consolidated schema for user creation and update
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = Body(None, description="Full name of the user")
    email: Optional[str] = Body(None, description="Email of the user")
    phone: Optional[str] = Body(None, description="Phone number of the user")


class UserCreate(UserBase):
    password: str = Body(..., description="Password for the account")
    type_id: int = Body(
        ..., description="1 - Admin, 2 - Service Head, 3 - Service Engineer"
    )


class UserUpdateBase(BaseModel):
    username: str = Body(..., description="Username that need to be updated")


class UserUpdateContact(UserUpdateBase):
    phone: Optional[str] = Body(None, description="Phone number of the user")
    email: Optional[str] = Body(None, description="Email of the user")


class UserUpdateName(UserUpdateBase):
    name: str = Body(..., description="Name of the empolyee")


class UserUpdatePassword(UserUpdateBase):
    password: str


class UserUpdateRepportTo(UserUpdateBase):
    report_to: str


# Output schemas for displaying user data
class Message(BaseModel):
    message: str


class UserOut(BaseModel):
    message: str
    username: str


class UserDisplay(UserBase):
    role: str
    # report_to: Optional[int] = Body(None, description="Supervisor of the user")


class UsersDisplay(BaseModel):
    users: List[UserDisplay]


class UserTeamMate(UserBase):
    role: str


class UserTeamMates(BaseModel):
    users: List[UserTeamMate]
