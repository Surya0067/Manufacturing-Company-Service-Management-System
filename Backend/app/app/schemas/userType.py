from pydantic import BaseModel
from fastapi import Body
from typing import Optional


class UserTypeBase(BaseModel):
    role: str = Body(...)
    description: str = Body(...)


class UserTypeIn(UserTypeBase):
    pass


class UserTypeOut(UserTypeBase):
    id: int

    class Config:
        orm_mode = True
