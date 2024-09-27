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


@router.get(
    "/tickets/{ticket_id}/report",
    response_model=dict,
    description="API endpoint to generate a ticket lifecycle report and return the file path",
)
def get_ticket_report(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
):
    try:
        result = generateTicketReportpdf(
            ticket_id=ticket_id, db=db, file_path=REPORT_DIR
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        pdf_file_path = result["file_path"]
        return {"file_path": pdf_file_path, "message": "Report generated successfully"}

    except Exception:
        raise HTTPException(status_code=500, detail=f"Failed to generate report")


@router.get("/service_head_tracking/", response_model=ServiceHeadTrackingResponse)
def track_service_head_performance(
    service_head_username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
):
    current_month = datetime.now().month
    current_year = datetime.now().year
    service_head = getUserByusername(db=db, username=service_head_username)
    if not service_head:
        raise HTTPException(status_code=404, detail="Service Head not found.")
    if service_head.type_id != 2:
        raise HTTPException(404, "this is not a service Head")
    assigned_tickets_list = getAssignedTickets(
        service_head.id, db, current_month, current_year
    )
    assigned_tickets_count = len(assigned_tickets_list)
    completed_tickets_count = countCompletedTickets(
        service_head.id, db, current_month, current_year
    )
    team_member_count = getTeamMemberCount(service_head.id, db)
    on_progress_tickets_count = countOnProgressTickets(service_head.id, db)

    return ServiceHeadTrackingResponse(
        service_head_id=service_head.id,
        service_head_name=service_head.username,
        service_head_phone=service_head.phone,
        month=current_month,
        year=current_year,
        assigned_tickets=assigned_tickets_count,
        completed_tickets=completed_tickets_count,
        team_members=team_member_count,
        on_progress_tickets=on_progress_tickets_count,
    )


@router.get(
    "/service-engineer/{engineer_username}/performance",
    response_model=ServiceEngineerPerformanceResponse,
)
async def get_performance(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(adminLogin),
):
    performance = getServiceEngineerPerformance(db, username)
    if not performance:
        raise HTTPException(status_code=404, detail="Service Engineer not found")
    return performance
