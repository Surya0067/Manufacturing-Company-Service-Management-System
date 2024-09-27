from pydantic import BaseModel, EmailStr
from typing import Optional, List
from fastapi import Body


# Consolidated schema for user creation and update
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = Body(None, description="Full name of the user")
    email: Optional[EmailStr] = Body(None, description="Email of the user")
    phone: Optional[str] = Body(None, description="Phone number of the user")


class UserCreate(BaseModel):
    full_name: str = Body(None, description="Full name of the user")
    email: EmailStr = Body(None, description="Email of the user")
    phone: str = Body(None, description="Phone number of the user")
    password: str = Body(..., description="Password for the account")
    type_id: int = Body(
        ..., description="1 - Admin, 2 - Service Head, 3 - Service Engineer"
    )
    report_to: str


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


class Message(BaseModel):
    message: str


class UserOut(BaseModel):
    message: str
    username: str


class UserDisplay(UserBase):
    role: str


class UserTeamMate(BaseModel):
    username: str
    full_name: str
    email: str
    phone: str
    role: str

    class Config:
        from_attributes = True


class UsersDisplay(BaseModel):
    users: List[UserDisplay]


class UserTeamMate(UserBase):
    role: str


class UserTeamMates(BaseModel):
    users: List[UserTeamMate]


class ServiceHeadTrackingResponse(BaseModel):
    service_head_id: int
    service_head_name: str
    service_head_phone: str
    month: int
    year: int
    assigned_tickets: int
    completed_tickets: int
    team_members: int
    on_progress_tickets: int


class ServiceEngineerPerformanceResponse(BaseModel):
    engineer_id: int
    name: str
    assigned_tickets: int
    completed_tickets: int
    email: str
    phone_number: str
