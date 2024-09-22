from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException, status
from models import Customer
from schemas import CustomerCreate,CustomerUpdate

def getCustomerByID(db : Session , id : int):
  return db.query(Customer).filter(Customer.id == id).first()
  

def createNewCustomer(db : Session,user : CustomerCreate):
  db.add(Customer(
    name = user.name,
    phone = user.phone,
    address= user.address,
    company_name = user.company_name
  ))
  db.commit()
  return dict(message = "Customer Created")

def updateCustomer(*,db : Session,customer:CustomerUpdate):
  customer_details = getCustomerByID(db=db,id=customer.id)
  if not customer_details:
    raise HTTPException(status_code=404,detail="Customer Not Found")
  if customer.name is None and customer.address is None and customer.company_name is None and customer.phone is None:
    raise HTTPException(status_code=400, detail="There is nothing to update")
  if customer.name:
    customer_details.name = customer.name
  if customer.phone:
    customer_details.phone = customer.phone
  if customer.address: 
    customer_details.address = customer.address
  if customer.company_name:
    customer_details.company_name = customer.company_name
  db.commit()
  db.refresh(customer_details)
  return dict(message = "Customer details updated")
