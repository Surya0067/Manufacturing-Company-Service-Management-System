from fastapi import APIRouter, Depends
from .endpoints import login, ticketManagement, user, customer

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/user", tags=["User"])
api_router.include_router(customer.router, prefix="/customer", tags=["Customer"])
api_router.include_router(ticketManagement.router, prefix="/ticket", tags=["Ticket Management"])
