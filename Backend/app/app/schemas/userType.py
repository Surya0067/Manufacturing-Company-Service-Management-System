from pydantic import BaseModel
from typing import Optional

class UserTypeIn(BaseModel):
  role : str
  description : str