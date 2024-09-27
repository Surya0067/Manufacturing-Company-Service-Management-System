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
