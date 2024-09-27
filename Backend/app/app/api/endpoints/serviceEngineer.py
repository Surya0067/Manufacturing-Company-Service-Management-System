from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.ticket import *
from api.deps import get_db, getCurrentUser
from models import User
from schemas import *
from utilis import *

router = APIRouter()


@router.get(
    "/get-all-assigned-ticket",
    description="Service engineer can see the assigned tickets",
    response_model=List[AssignedTicketResponse],
)
async def displayAllAssignedTicket(
    db: Session = Depends(get_db), current_user: User = Depends(getCurrentUser)
):
    assigned_tickets = assignedTickets(db=db, username=current_user.username)
    if assigned_tickets:
        return assigned_tickets
    raise HTTPException(status_code=404, detail="There is no assigned tickets")


@router.get(
    "/get-assigned-ticket/{ticket_id}",
    description="Service engineer can see the specfic ticket that assigned for him",
    response_model=List[AssignedTicketResponse],
)
async def displayAllAssignedTicket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    assigned_ticket = assignedTicket(
        db=db, username=current_user.username, ticket_id=ticket_id
    )
    if assigned_ticket:
        return assigned_ticket
    raise HTTPException(status_code=404, detail="ticket may be not assigned for you")

@router.post("/request-travel-expenses/{ticket_id}")
async def request_travel_expenses(
    ticket_id: int,
    expense_data: TravelExpenseReportCreate,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser)
):
    ticket = getTicketProcessByTicketID(db=db, service_engineer_id=current_user.id, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.service_engineer_id != current_user.id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you")
    
    if ticket.status not in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Ticket is still under process")
    image_path = saveUploadedFile(image)

    new_expense_report = createTravelExpenseReport(
        db=db,
        service_engineer_id=current_user.id,
        ticket_id=ticket_id,
        expense_details=expense_data.expense_details,
        total_amount=expense_data.total_amount,
        image_path=image_path
    )

    return {"msg": "Travel expense report created successfully", "expense_report": new_expense_report}
    