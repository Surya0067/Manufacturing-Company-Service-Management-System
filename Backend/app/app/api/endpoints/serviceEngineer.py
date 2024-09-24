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


@router.get("/get-all-assigned-ticket")
async def displayAllAssignedTicket(
    db: Session = Depends(get_db), current_user: User = Depends(getCurrentUser)
):
    assigned_tickets = assignedTickets(db=db, username=current_user.username)
    if assigned_tickets:
        return assigned_tickets
    raise HTTPException(status_code=404, detail="There is no assigned tickets")
