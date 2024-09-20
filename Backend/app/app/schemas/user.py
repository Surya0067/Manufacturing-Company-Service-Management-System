from pydantic import BaseModel
from typing import Optional
from fastapi import Body


class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    type_id: int


class Message(BaseModel):
    message: str


class UserOut(BaseModel):
    message: str
    username: str
    password: str


class UserDiplay(BaseModel):
    full_name: str
    email: str
    phone: str
    role: str
