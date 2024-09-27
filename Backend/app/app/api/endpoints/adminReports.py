from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from api.deps import get_db, adminLogin
from schemas import *
from curd.user import *
from curd.ticket import *
from curd.Report import *
from models import *
from pathlib import Path


router = APIRouter()

REPORT_DIR = "reports"

# Ensure the directory exists
Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)


@router.get("/tickets/{ticket_id}/report", response_model=dict,description="API endpoint to generate a ticket lifecycle report and return the file path")
def get_ticket_report(ticket_id: int, db: Session = Depends(get_db)):
    try:
        result = generateTicketReportpdf(ticket_id=ticket_id, db=db, file_path=REPORT_DIR)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        pdf_file_path = result["file_path"]
        return {"file_path": pdf_file_path, "message": "Report generated successfully"}

    except Exception:
        raise HTTPException(status_code=500, detail=f"Failed to generate report")