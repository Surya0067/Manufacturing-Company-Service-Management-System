from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Body, Path, Form
from datetime import datetime, date


class WorkReportBase(BaseModel):
    report: str
    report_date: date


class WorkReportCreate(WorkReportBase):
    pass


class WorkReportDisplay(WorkReportBase):
    id: int
    user_id: int
    created_at: int


class WorkReportForSpecificDate(BaseModel):
    start_date: date
    ending_date: date


class TravelExpenseBulkActionResponse(BaseModel):
    approved_expenses: Optional[List[int]] = []
    rejected_expenses: Optional[List[int]] = []
    message: str


class TravelExpenseDisplay(BaseModel):
    ticket_id: int
    service_engineer_username: str
    created_at: datetime

    class Config:
        orm_mode = True


class TravelExpenseReportResponse(BaseModel):
    id: int
    service_engineer_ID: int
    ticket_ID: int
    expense_details: str
    total_amount: float
    image_path: str
    status: str
    created_at: datetime
    status_by: Optional[int]

    class Config:
        orm_mode = True
