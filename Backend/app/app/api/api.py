from fastapi import APIRouter
from .endpoints import (
    login,
    serviceHead,
    ticketManagement,
    customer,
    ticketAssign,
    adminLogin,
    serviceEngineer,
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(adminLogin.router, prefix="/admin", tags=["Only Admin"])
api_router.include_router(
    serviceHead.router, prefix="/service-head", tags=["Service Head"]
)
api_router.include_router(
    serviceEngineer.router, prefix="/service-engineer", tags=["Service Engineer"]
)
api_router.include_router(customer.router, prefix="/customer", tags=["Customer"])
api_router.include_router(
    ticketManagement.router, prefix="/ticket-management", tags=["Ticket Management"]
)
api_router.include_router(
    ticketAssign.router, prefix="/ticket-assign", tags=["Ticket Assign"]
)
