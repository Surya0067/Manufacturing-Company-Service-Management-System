from typing import Any, Dict, Optional, Union
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException
from curd.customer import getCustomerByID
from curd.user import getUserByID, getUserByusername, userVaildation
from models import WorkReport, User
from schemas import *


def getLastestWorkReport(db: Session, user_id: int):
    return (
        db.query(WorkReport)
        .filter(WorkReport.user_id == user_id)
        .order_by(WorkReport.report_date.desc())
        .first()
    )


def getWorkReportByDate(db: Session, user_id: int, report_date: date):
    return (
        db.query(WorkReport)
        .filter(WorkReport.user_id == user_id, WorkReport.report_date == report_date)
        .first()
    )


def newWorkReport(db: Session, user_id: int, report: WorkReportCreate):
    db.add(
        WorkReport(
            user_id=user_id, report=report.report, report_date=report.report_date
        )
    )
    db.commit()
    return dict(message="Report added sucessfully")


def viewWorkReportForSpecificUser(db: Session, username: int, current_user: User):
    user = userVaildation(db=db, username=username, current_user=current_user)
    return (
        db.query(WorkReport)
        .filter(WorkReport.user_id == user.id)
        .order_by(WorkReport.report_date.desc())
        .all()
    )


def viewWorkReportForSpecificUserDateRange(
    db: Session, username: str, current_user: User, start_date: date, ending_date: date
):
    user = userVaildation(db=db, username=username, current_user=current_user)
    return (
        db.query(WorkReport)
        .filter(
            WorkReport.user_id == user.id,
            WorkReport.report_date >= start_date,
            WorkReport.report_date <= ending_date,
        )
        .order_by(WorkReport.report_date.desc())
        .all()
    )
