from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Body, Path
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


class TravelExpenseReportCreate(BaseModel):
    expense_details: str
    total_amount: float

    class Config:
        orm_mode = True
