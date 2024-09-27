from typing import Any, Dict, Optional, Union
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException,File, UploadFile
from curd.customer import getCustomerByID
from curd.user import getUserByID, getUserByusername
from models import Ticket, TicketRejected, TicketAssign, User, TicketProcess, SpareParts,TravelExpenseReports
from schemas import * 
import shutil
import os

UPLOAD_DIR = "expense_receipts/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def saveUploadedFile(file: UploadFile) -> str:
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_location

def createTravelExpenseReport(
    db: Session,
    service_engineer_id: int,
    ticket_id: int,
    expense_details: str,
    total_amount: float,
    image_path: str
):
    new_expense_report = TravelExpenseReports(
        service_engineer_ID=service_engineer_id,
        ticket_ID=ticket_id,
        expense_details=expense_details,
        total_amount=total_amount,
        image_path=image_path
    )
    
    db.add(new_expense_report)
    db.commit()
    db.refresh(new_expense_report)
    
    return new_expense_report