from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.ticket import *
from api.deps import get_db, getCurrentUser, serviceHeadLogin, adminLogin
from models import User
from schemas import *

router = APIRouter()

