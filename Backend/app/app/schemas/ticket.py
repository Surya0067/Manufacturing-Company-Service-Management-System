from pydantic import BaseModel
from typing import Optional, List
from fastapi import Body
from datetime import datetime

class TicketCreate(BaseModel):
  customer_id : int
  issue_description : str
  
class TicketDisplay(BaseModel):
    ticket_id: int
    customer_id: int
    customer_name: str
    company_name: str
    address: str
    phone: str
    created_at: datetime
    is_taken: bool
    updated_at: Optional[datetime]
    issue_description: Optional[str]
    status: bool

    class Config:
        orm_mode = True

