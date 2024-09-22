from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from curd.customer import createNewCustomer, updateCustomer
from api.deps import get_db, getCurrentUser
from models import User
from schemas import Message, CustomerCreate, CustomerUpdate

router = APIRouter()


@router.post(
    "/create-Customer",
    description="Customer can be created by Service head and Admin Only",
    response_model=Message,
)
async def createCustomer(
    user_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access Declined")
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
    current_user: User = Depends(getCurrentUser),
):
    if current_user.type_id == 3:
        raise HTTPException(status_code=400, detail="Access Declined")
    user = updateCustomer(db=db, customer=customer)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Cant edit an customer-details")
