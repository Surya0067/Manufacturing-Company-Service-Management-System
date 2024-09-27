from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Body, Path
from datetime import datetime, date
from .customer import CustomerDisplay


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


class TicketAssignBase(BaseModel):
    ticket_id: int
    service_engineer_username: str


class TickectAssignCreate(TicketAssignBase):
    assigned_date: date


class TickectReAssign(TicketAssignBase):
    assigned_date: date


class TickectAssignHistory(TicketAssignBase):
    status: str
    assigned_by: str
    assigned_date: date
    created_date: datetime

    class Config:
        from_attributes = True


class TicketAssignDisplay(TicketAssignBase):
    status: str
    assigned_by: str
    issue_description: str
    assigned_date: date
    created_date: datetime

    class Config:
        from_attributes = True


class AssignedTicketResponse(BaseModel):
    ticket: TicketAssignDisplay
    customer: CustomerDisplay


class TicketProcessBase(BaseModel):
    ticket_id: int


class TicketprocessCreate(TicketProcessBase):
    problem_description: str = Field(
        ..., description="Problem satement that service engineer found"
    )
    priority: str = Field(..., description="priority must be low,medium,high")
    excepted_complete_date: datetime = Field(
        ..., description="date that service engineer expect to complete"
    )
    spare_parts_required: bool = Field(
        ..., description="1 for spare part needed, 0 for spare paer dont needed"
    )


class TicketProcessUpdate(TicketProcessBase):
    problem_description: Optional[str] = Field(
        default=None, description="Problem satement that service engineer found"
    )
    priority: Optional[str] = Field(
        default=None, description="priority must be low,medium,high"
    )
    excepted_complete_date: Optional[datetime] = Field(
        default=None, description="date that service engineer expect to complete"
    )
    spare_parts_required: Optional[bool] = Field(
        default=None,
        description="1 for spare part needed, 0 for spare paer dont needed",
    )


class SparePartBase(BaseModel):
    ticket_id: int


class SparePartUpdate(BaseModel):
    part_name: str
    quantity: float


class SparePartRequestResponse(SparePartBase):
    service_engineer_username: str


class SparePartResponse(BaseModel):
    id: int
    part_name: str
    quantity: float
    status: str

    class Config:
        orm_mode = True


class SparePartsBulkActionResponse(BaseModel):
    message: str
    approved_parts: list[int]
    rejected_parts: list[int]


class TicketProcessChangeStatus(TicketProcessBase):
    status: str
