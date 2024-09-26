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


@router.post("/setting-intial-process/",description="user can create the process state of the ticket",response_model=Message)
async def createTicketProcess(
    ticket_process: TicketprocessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    ticket = get_and_validate_ticket(db=db, ticket_id=ticket_process.ticket_id)
    ticket_assigned = getTicketAssigned(
        db=db, ticket_id=ticket_process.ticket_id
    )
    db_ticket_process = getTicketProcessByTicketID(
        db=db, ticket_id=ticket_process.ticket_id,service_engineer_id=current_user.id
    )
    if ticket_assigned==None or ticket_assigned.service_engineer_id != current_user.id:
        raise HTTPException(status_code=400,detail="This tickect not assigned for you")
    if db_ticket_process or ticket_assigned.status == "on-progress":
        raise HTTPException(status_code=409, detail="ticket has already on-progress")
    ticket_process = newTicketProcess(
        db=db, service_engineer_id=current_user.id, details=ticket_process
    )
    if ticket_process:
        return ticket_process
    raise HTTPException(status_code=400, detail="Cant able to add ticket process")

@router.put("/update-ticket-process/",description="the user can change the process details",response_model=Message)
async def updateTicketProcess(
    ticket_process: TicketProcessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    ticket = get_and_validate_ticket(db=db, ticket_id=ticket_process.ticket_id)
    ticket_assigned = getTicketAssigned(
        db=db, ticket_id=ticket_process.ticket_id
    )
    db_ticket_process = getTicketProcessByTicketID(
        db=db, ticket_id=ticket_process.ticket_id,service_engineer_id=current_user.id
    )
    if ticket_assigned==None or ticket_assigned.service_engineer_id != current_user.id:
        raise HTTPException(status_code=400,detail="This tickect not assigned for you")
    if not db_ticket_process:
        raise HTTPException(status_code=400,detail="This tickect has no process history")
    update = updateProcess(db=db,service_engineer_id=current_user.id,details=ticket_process)
    if update:
        return update
    
@router.post("/add-spare-parts/{ticket_id}")
async def addSpareParts(
    ticket_id: int,
    spare_parts: List[SparePartUpdate],
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser)
):
    ticket = get_and_validate_ticket(db=db, ticket_id=ticket_id)
    db_ticket_process = getTicketProcessByTicketID(
        db=db, ticket_id=ticket_id, service_engineer_id=current_user.id
    )
    if not db_ticket_process:
        raise HTTPException(status_code=403, detail=f"This user doesn't handle ticket no: {ticket_id}.")
    
    if not db_ticket_process.spare_parts_required:
        raise HTTPException(status_code=403, detail="This ticket is not eligible for spare parts.")
    
    spare_part_entries = addsparePart(
        db=db, ticket_id=ticket_id, service_engineer_id=current_user.id, spare_parts=spare_parts
    )
    if spare_part_entries:
        return spare_part_entries
    
