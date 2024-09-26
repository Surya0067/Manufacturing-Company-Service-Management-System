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
    ticket = getAndValidateTicket(db=db, ticket_id=ticket_process.ticket_id)
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
    ticket = getAndValidateTicket(db=db, ticket_id=ticket_process.ticket_id)
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
    ticket = getAndValidateTicket(db=db, ticket_id=ticket_id)
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
    
@router.get("/list-request-spare-parts", response_model=List[SparePartRequestResponse])
async def listOfRequestedSpareParts(
    db: Session = Depends(get_db), 
    current_user: User = Depends(serviceHeadLogin)
):
    if current_user.user_type == 1:
        ticket_requests = db.query(SpareParts).filter(SpareParts.status == 'pending').all()
    else:
        service_engineers = getServiceEngineersUnderHead(db=db, current_user=current_user)
        if not service_engineers:
            raise HTTPException(status_code=404, detail="No service engineers found under this service head")
        
        service_engineer_ids = [se.id for se in service_engineers]
        ticket_requests = getSparePartRequests(db=db, service_engineer_ids=service_engineer_ids)

    if not ticket_requests:
        raise HTTPException(status_code=404, detail="No spare part requests found")

    result = [
        SparePartRequestResponse(ticket_id=req[0], service_engineer_username=req[2])
        for req in ticket_requests
    ]

    return result



@router.get("/list-spare-parts/{ticket_id}", response_model=List[SparePartResponse],description="its shows the sapre parts")
async def listSparePartsForTicket(
    ticket_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(getCurrentUser)
):

    ticket_assign = getTicketAssignment(db, ticket_id)
    if current_user.user_type.role == "service_engineer" and ticket_assign.service_engineer_id != current_user.id:
        raise HTTPException(status_code=403, detail="This ticket is not assigned to you.")
    spare_parts = getSpareParts(db, ticket_id)
    return spare_parts  

@router.put("/spare-parts/{ticket_id}/bulk-action", response_model=SparePartsBulkActionResponse,description="Admin or service head can approve or reject the spare part rejection")
async def approveOrRejectSpareParts(
    ticket_id: int,
    approve_ids: List[int] = None,  
    reject_ids: List[int] = None,  
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin) 
):
    result = approveOrRejectSparePartsInDb(
        db=db,
        ticket_id=ticket_id,
        approve_ids=approve_ids,
        reject_ids=reject_ids,
        service_head_id=current_user.id
    )

    return {
        "message": f"Spare parts for ticket {ticket_id} have been processed successfully.",
        **result
    }

@router.put("/tickets/status-changes/",response_model=Message,description="it change the ticket status as complete or cancelled")
async def changeStatussTicket(
    ticket : TicketProcessChangeStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser)
):
    db_assigned_ticket = getTicketAssignedByTicketID(db=db,ticket_id=ticket.ticket_id)
    ticket.status = ticket.status.lower()
    if ticket.status not in ["completed","cancelled"]:
        raise HTTPException(404,"status not found")
    if current_user.type_id == 1:
        completed_ticket = statusTicketInDb(db=db, ticket_id=ticket.ticket_id,status=ticket.status)
    elif current_user.type_id == 2:
        if db_assigned_ticket.service_engineer.report_to == current_user.id:
            completed_ticket = statusTicketInDb(db=db, ticket_id=ticket.ticket_id,status=ticket.status)
        else:
            raise HTTPException(status_code=403,detail="this tickect has another service head")
    elif db_assigned_ticket.service_engineer_id == current_user.id:
            completed_ticket = statusTicketInDb(db=db, ticket_id=ticket.ticket_id,status=ticket.status)
    else:
        raise HTTPException(status_code=403,detail="You dont have access")
    if completed_ticket:
        return completed_ticket