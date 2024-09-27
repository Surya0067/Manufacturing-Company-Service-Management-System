from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, File, UploadFile
from models import (
    User,
    TravelExpenseReports,
)
from schemas import *
import shutil
import os
import uuid

UPLOAD_DIR = "expense_receipts/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def saveUploadedFile(file: UploadFile) -> str:
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    file_location = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_location


def getTravelExpenseReportByID(db: Session, ticket_id: int):
    return (
        db.query(TravelExpenseReports)
        .filter(TravelExpenseReports.ticket_ID == ticket_id)
        .first()
    )


def getTravelExpenseReportsByIDs(db: Session, report_ids: List[int]):
    return (
        db.query(TravelExpenseReports)
        .filter(TravelExpenseReports.id.in_(report_ids))
        .all()
    )


def createTravelExpenseReport(
    db: Session,
    service_engineer_id: int,
    ticket_id: int,
    expense_details: str,
    total_amount: float,
    image_path: str,
):
    new_expense_report = TravelExpenseReports(
        service_engineer_ID=service_engineer_id,
        ticket_ID=ticket_id,
        expense_details=expense_details,
        total_amount=total_amount,
        image_path=image_path,
    )

    db.add(new_expense_report)
    db.commit()
    db.refresh(new_expense_report)

    return dict(message="Expense report added")


def getTravelExpenses(db: Session, current_user: User):
    if current_user.type_id == 1:
        expenses = db.query(TravelExpenseReports).all()
    else:
        expenses = (
            db.query(TravelExpenseReports)
            .join(User, TravelExpenseReports.service_engineer_ID == User.id)
            .filter(User.report_to == current_user.id)
            .all()
        )

    return expenses


def getTravelExpenseForTicketID(db: Session, ticket_id: int):
    expenses = (
        db.query(TravelExpenseReports)
        .filter(TravelExpenseReports.ticket_ID == ticket_id)
        .all()
    )

    return [
        TravelExpenseReportResponse(
            id=expense.id,
            service_engineer_ID=expense.service_engineer_ID,
            ticket_ID=expense.ticket_ID,
            expense_details=expense.expense_details,
            total_amount=expense.total_amount,
            image_path=expense.image_path,
            status=expense.status,
            created_at=expense.created_at,
            status_by=expense.status_by,
        )
        for expense in expenses
    ]


def approveOrRejectTravelExpensesInDb(
    db: Session,
    ticket_ID: int,
    user_id: int,
    approve_ids: list[int] = None,
    reject_ids: list[int] = None,
):
    travel_expenses = (
        db.query(TravelExpenseReports)
        .filter(TravelExpenseReports.id.in_(approve_ids + reject_ids))
        .all()
    )

    if not travel_expenses:
        raise HTTPException(
            status_code=404, detail="No travel expenses found for the provided IDs"
        )

    ticket_ids = {expense.ticket_ID for expense in travel_expenses}
    if len(ticket_ids) > 1:
        raise HTTPException(
            status_code=400, detail="All expenses must belong to the same ticket"
        )

    approved_expenses = []
    rejected_expenses = []
    if approve_ids:
        for expense in travel_expenses:
            if expense.id in approve_ids:
                expense.status = "Approved"
                expense.status_by = user_id
                expense.status_at = func.now()
                approved_expenses.append(expense.id)
    if reject_ids:
        for expense in travel_expenses:
            if expense.id in reject_ids:
                expense.status = "Rejected"
                expense.status_by = user_id
                expense.status_at = func.now()
                rejected_expenses.append(expense.id)
    db.commit()
    return {
        "approved_expenses": approved_expenses,
        "rejected_expenses": rejected_expenses,
    }
