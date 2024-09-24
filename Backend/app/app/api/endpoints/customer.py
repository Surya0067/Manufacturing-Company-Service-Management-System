from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from curd.customer import *
from curd.ticket import createTicket
from api.deps import get_db, getCurrentUser, adminLogin, serviceHeadLogin
from models import User
from schemas import (
    Message,
    CustomerCreate,
    CustomerUpdate,
    CustomerDisplay,
    TicketCreate,
)

router = APIRouter()


@router.post(
    "/create-Customer",
    description="Customer can be created by Service head and Admin Only",
    response_model=Message,
)
async def createCustomer(
    user_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    user = createNewCustomer(db=db, user=user_in)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant Create an customer")


@router.patch(
    "/update-customer",
    description="Customer details can be Edited by Service head and Admin Only",
    response_model=Message,
)
async def updateCustomerDetails(
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    user = updateCustomer(db=db, customer=customer)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant edit an customer-details")


@router.get(
    "/view-customer-details/{customer_id}",
    response_model=CustomerDisplay,
    description="User can see the customer ",
)
async def viewCustomerDetails(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin),
):
    customer = viewCustomer(db=db, customer_id=customer_id)
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access Declined")
    if customer:
        return customer


@router.post("/raise-ticket", description="customer can raise the ticket")
async def customerRaiseTicket(new_ticket: TicketCreate, db: Session = Depends(get_db)):
    ticket = createTicket(db=db, ticket=new_ticket)
    if ticket:
        return ticket
    raise HTTPException(status_code=400, detail="tickect can not be raised")
