from fastapi import APIRouter, Depends
from .endpoints import login, serviceEngineer, ticketManagement, customer, ticketAssign,adminLogin

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(adminLogin.router,prefix="/admin",tags=["Only Admin"])
api_router.include_router(serviceEngineer.router, prefix="/user", tags=["Service Engineer"])
api_router.include_router(customer.router, prefix="/customer", tags=["Customer"])
api_router.include_router(
    ticketManagement.router, prefix="/ticket-management", tags=["Ticket Management"]
)
api_router.include_router(
    ticketAssign.router, prefix="/ticket-assign", tags=["Ticket Assign"]
)
