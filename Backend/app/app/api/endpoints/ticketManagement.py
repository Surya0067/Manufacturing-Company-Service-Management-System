from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.ticket import *
from api.deps import get_db, getCurrentUser, serviceHeadLogin, adminLogin
from models import User
from schemas import *

router = APIRouter()


@router.post(
    "/create-ticket",
    description="Tickect can be created by admin and service head only",
)
async def createNewTicket(
    new_ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = createTicket(db=db, ticket=new_ticket)
    if ticket:
        return ticket
    raise HTTPException(status_code=400, detail="tickect can not be raised")


@router.get(
    "/display-all-tickets",
    description="Displaying every ticket only for service head and admin",
    response_model=list[TicketDisplay],
)
async def getAllTickets(
    db: Session = Depends(get_db), current_user: User = Depends(serviceHeadLogin)
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access Declined")
    tickets = displayTickets(db=db)
    if tickets:
        return tickets
    raise HTTPException(status_code=404, detail="No tickets found")


@router.get(
    "/display-ticket/{ticket_id}",
    description="Displaying a specfic ticket only for service head and admin",
    response_model=TicketDisplay,
)
async def getTicket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = displaySpecficTicket(db=db, ticket_id=ticket_id)
    if ticket:
        return ticket
    raise HTTPException(status_code=404, detail="No tickets found")


@router.patch(
    "/edit-ticket/",
    description="Only service head and admin can update the ticket",
    response_model=Message,
)
async def updateTicket(
    ticket: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = ticketUpdate(db=db, ticket_update=ticket)
    if ticket:
        return ticket
    raise HTTPException(status_code=400, detail="cant able to update the ticket")


@router.delete(
    "/delete-ticket/",
    description="only admin and service head can cancel the tickets with proper reason",
)
async def deleteTicket(
    ticket_rejection: TicketRejectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = ticketStatusChange(
        ticket_rejection=ticket_rejection, db=db, user_id=current_user.id
    )
    if ticket:
        return ticket
    raise HTTPException(status_code=400, detail="Cant able to delete the ticket")
