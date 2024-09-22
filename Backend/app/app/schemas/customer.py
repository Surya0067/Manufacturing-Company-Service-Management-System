from pydantic import BaseModel
from fastapi import Body


class CustomerBase(BaseModel):
    name: str = Body(default=None, description="Name of the customer")
    phone: str = Body(default=None, description="Phone number of the customer")
    address: str = Body(default=None, description="Address of the customer")
    company_name: str = Body(default=None, description="Company name of the customer")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    id: int
