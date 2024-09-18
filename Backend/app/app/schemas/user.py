from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    full_name : str
    username : str
    password :str
    email :str
    phone : int
    type_id : int

class UserOut(BaseModel):
    message : str