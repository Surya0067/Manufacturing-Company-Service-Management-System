from pydantic import BaseModel
from typing import Optional, List
from fastapi import Body, Path
from datetime import datetime


class TicketCreate(BaseModel):
    customer_id: int
    issue_description: Optional[str]


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
        from_attributes = True


class TicketUpdate(BaseModel):
    ticket_id: int = Path(..., description="ticket_id to update")
    customer_id: int = Body(None, description="if they want to change the customer")
    issue_description: Optional[str] = Body(
        None, description="if they want to change issue description"
    )


class TicketRejectionBase(BaseModel):

    ticket_id: int
    reason: str


class TicketRejectionCreate(TicketRejectionBase):
    pass


class TicketRejectionDisplay(TicketRejectionBase):
    id: int
    user_id: int
