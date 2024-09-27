from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, Dict, Optional, Union
from sqlalchemy import func, distinct,extract
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException
from curd.customer import getCustomerByID
from curd.user import getUserByID, getUserByusername, userVaildation
from curd.ticket import *
from models import *
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


def generateTicketReportpdf(ticket_id: int, db: Session, file_path: str):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(404,"ticket not found")

    # PDF Setup
    pdf_file_name = f"{file_path}/ticket_report-{ticket_id}.pdf"
    c = canvas.Canvas(pdf_file_name, pagesize=A4)
    width, height = A4

    report_data = []
    report_data.append(f"Ticket ID: {ticket.id}")
    report_data.append(f"Customer: {ticket.customer.name}")
    report_data.append(f"Issue Description: {ticket.issue_description}")
    report_data.append(f"Created At: {ticket.created_at}")
    report_data.append(f"Status: {'Rejected' if ticket.ticket_rejected else 'In Progress'}")

    
    if ticket.ticket_rejected:
        rejection = ticket.ticket_rejected[0]
        report_data.append(f"Rejected By: {rejection.user.username}")
        report_data.append(f"Reason: {rejection.reason}")
        report_data.append(f"Rejection Date: {rejection.created_at}")
    else:
        latest_assignment = db.query(TicketAssign).filter(TicketAssign.ticket_id == ticket_id).order_by(TicketAssign.id.desc()).first()
        if latest_assignment:
            report_data.append(f"Assigned To: {latest_assignment.service_engineer.username}")
            report_data.append(f"Assigned By: {latest_assignment.assigned_by.username}")
            report_data.append(f"Assignment Date: {latest_assignment.assigned_date}")
            report_data.append(f"Assignment Status: {latest_assignment.status}")
            if latest_assignment.status == "Cancelled":
                report_data.append("Assignment was cancelled.")

        if ticket.ticket_process:
            process = ticket.ticket_process[0]
            report_data.append(f"Service Engineer: {process.user.username}")
            report_data.append(f"Problem Description: {process.problem_description}")
            report_data.append(f"Priority: {process.priority}")
            report_data.append(f"Expected Completion Date: {process.excepted_complete_date}")
            report_data.append(f"Actual Completion Date: {process.actual_complete_date or 'Not Completed'}")
            report_data.append(f"Spare Parts Required: {'Yes' if process.spare_parts_required else 'No'}")

            total_spare_cost = 0
            if process.spare_parts_required:
                spare_parts = db.query(SpareParts).filter(SpareParts.ticket_id == ticket_id).all()
                total_spare_cost = 0
                report_data.append("Spare Parts Details:")
                for part in spare_parts:
                    cost = part.quantity * part.unit_price
                    total_spare_cost += cost
                    report_data.append(f"  - {part.part_name} (Quantity: {part.quantity}, Unit Price: {part.unit_price}, Cost: {cost})")
                report_data.append(f"Total Spare Parts Cost: {total_spare_cost}")

            final_cost = (process.labour_cost or 0) + total_spare_cost
            report_data.append(f"Labour Cost: {process.labour_cost or 0}")
            report_data.append(f"Total Ticket Cost: {final_cost}")

    y_position = height - 50
    for line in report_data:
        if y_position < 50:
            c.showPage()
            y_position = height - 50
        c.drawString(50, y_position, line)
        y_position -= 40
    c.save()

    return {"file_path": pdf_file_name, "message": "Report generated successfully"}


def getAssignedTickets(service_head_id: int, db: Session, current_month: int, current_year: int):
    service_engineer_alias = aliased(User)

    return db.query(TicketProcess).select_from(TicketProcess).join(
        TicketAssign, TicketProcess.ticket_id == TicketAssign.ticket_id
    ).join(
        service_engineer_alias, TicketAssign.service_engineer_id == service_engineer_alias.id
    ).filter(
        service_engineer_alias.report_to == service_head_id,
        extract('month', TicketProcess.created_at) == current_month,
        extract('year', TicketProcess.created_at) == current_year
    ).all()


def countCompletedTickets(service_head_id: int, db: Session, current_month: int, current_year: int):
    service_engineer_alias = aliased(User)

    return db.query(TicketProcess).select_from(TicketProcess).join(
        TicketAssign, TicketProcess.ticket_id == TicketAssign.ticket_id
    ).join(
        service_engineer_alias, TicketAssign.service_engineer_id == service_engineer_alias.id
    ).filter(
        service_engineer_alias.report_to == service_head_id,
        TicketProcess.status == "completed",
        extract('month', TicketProcess.actual_complete_date) == current_month,
        extract('year', TicketProcess.actual_complete_date) == current_year
    ).count()


def getTeamMemberCount(service_head_id: int, db: Session):
    return db.query(User).filter(User.report_to == service_head_id).distinct(User.id).count()

def countOnProgressTickets(service_head_id: int, db: Session):
    service_engineer_alias = aliased(User)

    return db.query(TicketProcess).select_from(TicketProcess).join(
        TicketAssign, TicketProcess.ticket_id == TicketAssign.ticket_id
    ).join(
        service_engineer_alias, TicketAssign.service_engineer_id == service_engineer_alias.id
    ).filter(
        service_engineer_alias.report_to == service_head_id,
        TicketProcess.status == "on-progress"
    ).count()

def getServiceEngineerPerformance(db: Session, username: str):
    engineer = getUserByusername(db=db,username=username)
    if not engineer:
        return None
    if  engineer.type_id !=3:
        raise HTTPException(404,"this user is not an service engineer")
    assigned_tickets = db.query(TicketAssign).filter(TicketAssign.service_engineer_id == engineer.id).count()
    completed_tickets = db.query(TicketAssign).filter(TicketAssign.service_engineer_id == engineer.id, Ticket.status == 'completed').count()
    return ServiceEngineerPerformanceResponse(
        engineer_id=engineer.id,
        name=engineer.username,
        assigned_tickets=assigned_tickets,
        completed_tickets=completed_tickets,
        email=engineer.email,
        phone_number=engineer.phone,
    )
