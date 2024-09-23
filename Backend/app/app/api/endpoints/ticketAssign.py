from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.ticket import *
from api.deps import get_db, getCurrentUser,serviceHeadLogin,adminLogin
from models import User
from schemas import *

router = APIRouter()


@router.post(
    "/ticket",
    description="service head and admin can assign the ticket to the service engineer",
)
async def ticketAssigning(
    ticket_assign: TickectAssignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="access declined")
    ticket = assigningTickect(
        db=db, assigned_by_id=current_user.id, ticket_details=ticket_assign
    )
    if ticket:
        return ticket
