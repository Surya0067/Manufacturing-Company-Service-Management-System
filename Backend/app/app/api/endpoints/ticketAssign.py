from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.ticket import *
from api.deps import get_db,serviceHeadLogin
from models import User
from schemas import *

router = APIRouter()


@router.post(
    "/ticket",
    description="Service head and admin can assign the ticket to the service engineer",
    response_model=Message,
)
async def ticketAssigning(
    ticket_assign: TickectAssignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = getAndValidateTicket(db=db, ticket_id=ticket_assign.ticket_id)

    checkTicketAlreadyAssigned(
        db=db, ticket_id=ticket_assign.ticket_id, current_user=current_user
    )

    service_engineer = getAndValidateServiceEngineer(
        db=db,
        username=ticket_assign.service_engineer_username,
        current_user=current_user,
    )

    ticket = assigningTickect(
        db=db, assigned_by_id=current_user.id, ticket_details=ticket_assign
    )
    return ticket


@router.post(
    "/ticket-reassign",
    description="Service head and admin can reassign the ticket to the service engineer",
    response_model=Message,
)
async def ticketReAssigning(
    ticket_assign: TickectReAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = getAndValidateTicket(db=db, ticket_id=ticket_assign.ticket_id)

    db_ticket = checkTicketAlreadyAssigned(
        db=db,
        ticket_id=ticket_assign.ticket_id,
        current_user=current_user,
        reassign=True,
    )
    if db_ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found or not assigned")

    service_engineer = getAndValidateServiceEngineer(
        db=db,
        username=ticket_assign.service_engineer_username,
        current_user=current_user,
    )

    if db_ticket.status == "released":
        raise HTTPException(
            status_code=400, detail="released tickets cannot be reassigned"
        )

    if db_ticket.service_engineer_id != service_engineer.id:
        reassigned = reassigningTicket(
            db=db, assgin_by=current_user.id, resign=ticket_assign
        )
        if reassigned:
            return reassigned
    raise HTTPException(status_code=400, detail="service engineer are same")


@router.get(
    "/history-of-assigned/{ticket_id}",
    description="Here we can see the history of ticket assigning",
    response_model=List[TickectAssignHistory],
)
async def ticketAssignHistory(
    ticket_id: int = Path(
        ..., description="Ticket id for getting history of assigning"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = getTicketByID(db=db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db_ticket = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket has not been assigned yet")
    if (
        current_user.type_id != 1
        and db_ticket.service_engineer.report_to != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="This ticket owner is another service head"
        )
    tickets = historyOfAssigningTicket(db=db, ticket_id=ticket_id)
    if tickets:
        return [
            TickectAssignHistory(
                ticket_id=ticket.ticket_id,
                service_engineer_username=ticket.service_engineer.username,
                status=ticket.status,
                assigned_by=ticket.assigned_by.username,
                assigned_date=ticket.assigned_date,
                created_date=ticket.created_at,
            )
            for ticket in tickets
        ]


@router.delete(
    "/release-ticket",
    description="Service head can release the ticket which he assigned to a sevice engineer",
    response_model=Message,
)
async def releasedTicket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    ticket = getTicketByID(db=db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db_ticket = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket has not been assigned yet")
    if (
        current_user.type_id != 1
        and db_ticket.service_engineer.report_to != current_user.id
    ):
        raise HTTPException(
            status_code=400, detail="This ticket owner is another service head"
        )
    cancelling_ticket = releasingTickeAssign(db=db, ticket_id=ticket_id)
    if cancelling_ticket:
        return cancelling_ticket
