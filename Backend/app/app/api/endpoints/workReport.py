from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from curd.Report import *
from api.deps import get_db, getCurrentUser,serviceHeadLogin
from models import User
from schemas import *

router = APIRouter()


@router.post("/add-report")
async def CreateWorkReport(
    report: WorkReportCreate,
    db: User = Depends(get_db),
    current_user: User = Depends(getCurrentUser),
):
    db_report = getLastestWorkReport(db=db, user_id=current_user.id)
    existing_report = getWorkReportByDate(db=db, user_id=current_user.id, report_date=report.report_date)
    if existing_report:
        raise HTTPException(status_code=400, detail="A report for this date has already been submitted.")
    if db_report:
        if report.report_date < db_report.report_date:
            raise HTTPException(status_code=400, detail="A report for this date has already been submitted.")
        missing_days = (report.report_date - db_report.report_date).days
        if missing_days > 1:
            raise HTTPException(
                status_code=400,
                detail=f"Please submit the missing reports for the last {missing_days - 1} day(s) before submitting this report.",
            )
    new_report = newWorkReport(db=db, report=report, user_id=current_user.id)
    if new_report:
        return new_report

@router.get("/my-Work-reports")
async def myWorkReports(db : Session = Depends(get_db),current_user : User = Depends(getCurrentUser)):
    work_reports = viewWorkReportForSpecificUser(db=db,username=current_user.username,current_user=current_user)
    if work_reports:
        return work_reports
    raise HTTPException(404,"Work reports not found")

@router.get("/view-work-report/username/{username}")
async def viewWorkReports(username : str,db : Session = Depends(get_db),current_user : User = Depends(serviceHeadLogin)):
    work_reports = viewWorkReportForSpecificUser(db=db,username=username,current_user=current_user)
    if work_reports:
        return work_reports
    raise HTTPException(404,"Work reports not found")

@router.post("/view-work-report/specific-date-range/username/{username}")
async def viewWorkReportSpecificDateRange(
    username: str,
    dates: WorkReportForSpecificDate,
    db: Session = Depends(get_db),
    current_user: User = Depends(serviceHeadLogin)
):
    work_reports = viewWorkReportForSpecificUserDateRange(
        db=db, username=username, current_user=current_user, start_date=dates.start_date, ending_date=dates.ending_date
    )
    if work_reports:
        return work_reports
    raise HTTPException(404, "Work reports not found within the specified date range")

    