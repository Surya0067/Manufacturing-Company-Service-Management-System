from fastapi import APIRouter, Depends
from .endpoints import login
api_router = APIRouter()

api_router.include_router(login.router, prefix="/login",tags=["login"])
