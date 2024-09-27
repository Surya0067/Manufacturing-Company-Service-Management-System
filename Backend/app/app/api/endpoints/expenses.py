from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db, getCurrentUser, serviceHeadLogin
from schemas import *
from curd.ticket import getTicketProcessByTicketID, getTicketByID
from curd.user import *
from models import *
from utilis import *

router = APIRouter()


@router.post("/request-travel-expenses/{ticket_id}")
async def request_travel_expenses(
    ticket_id: int,
    expense_details: str = Form(...),
    total_amount: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    ticket = getTicketProcessByTicketID(
        db=db, service_engineer_id=current_user.id, ticket_id=ticket_id
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.service_engineer_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="This ticket is not assigned to you"
        )

    if ticket.status not in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Ticket is still under process")

    image_path = saveUploadedFile(image)

    new_expense_report = createTravelExpenseReport(
        db=db,
        service_engineer_id=current_user.id,
        ticket_id=ticket_id,
        expense_details=expense_details,
        total_amount=total_amount,
        image_path=image_path,
    )
    if new_expense_report:
        return new_expense_report


@router.get(
    "/display-all-travel-expenses",
    description="Displaying all travel expense reports only for service heads and admins",
    response_model=List[TravelExpenseDisplay],
)
async def travelExpenses(
    db: Session = Depends(get_db), current_user: User = Depends(getCurrentUser)
):
    expenses = getTravelExpenses(db=db, current_user=current_user)

    if expenses:
        return [
            TravelExpenseDisplay(
                ticket_id=expense.ticket_ID,
                service_engineer_username=expense.service_engineer.username,
                created_at=expense.created_at,
            )
            for expense in expenses
        ]

    raise HTTPException(status_code=404, detail="No travel expenses found")


@router.get(
    "/get-expenses-report/{ticket_id}/ticket-id",
    response_model=List[TravelExpenseReportResponse],
)
async def viewExpenseReportByTicketID(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    ticket = getTicketByID(db=db, id=ticket_id)
    if not ticket:
        raise HTTPException(404, "tickect not found")
    ticket_expense = getTravelExpenseReportByID(db=db, ticket_id=ticket_id)
    if not ticket_expense:
        raise HTTPException(404, "ticket does have any expenses")
    allowed_user_ids = (
        [ticket_expense.service_engineer_ID, ticket_expense.service_engineer.report_to]
        if ticket_expense.service_engineer
        else []
    )
    if current_user.type_id == 1 or current_user.id in allowed_user_ids:
        expenses = getTravelExpenseForTicketID(db=db, ticket_id=ticket_id)
    else:
        raise HTTPException(400, "access denied")
    if expenses:
        return expenses


@router.put(
    "/travel-expenses/bulk-action/{ticket_id}",
    response_model=TravelExpenseBulkActionResponse,
)
async def approveOrRejectTravelExpenses(
    ticket_id: int,
    approve_ids: List[int] = None,
    reject_ids: List[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    result = approveOrRejectTravelExpensesInDb(
        db=db,
        ticket_ID=ticket_id,
        user_id=current_user.id,
        approve_ids=approve_ids,
        reject_ids=reject_ids,
    )

    return {"message": "Travel expenses processed successfully.", **result}
