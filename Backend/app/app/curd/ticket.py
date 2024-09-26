from typing import Any, Dict, Optional, Union
from sqlalchemy import func,distinct
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException
from curd.customer import getCustomerByID
from curd.user import getUserByID, getUserByusername
from models import Ticket, TicketRejected, TicketAssign, User, TicketProcess,SpareParts
from schemas import *


# =======================================vaildation and common==========================================================
def getTicketByID(db: Session, id: int):
    return db.query(Ticket).filter(Ticket.id == id).first()


def getTicketAssignedByTicketID(db: Session, ticket_id: int):
    return (
        db.query(TicketAssign)
        .filter(TicketAssign.ticket_id == ticket_id)
        .order_by(TicketAssign.created_at.desc())
        .first()
    )


def get_and_validate_ticket(db: Session, ticket_id: int):
    ticket = getTicketByID(db=db, id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status == False:
        raise HTTPException(status_code=400, detail="Ticket has been rejected")
    return ticket


def get_and_validate_service_engineer(db: Session, username: str, current_user: User):
    service_engineer = getUserByusername(db=db, username=username)
    if not service_engineer:
        raise HTTPException(status_code=404, detail="Service engineer not found")
    if service_engineer.type_id != 3:
        raise HTTPException(status_code=400, detail="He is not a service engineer")
    if not service_engineer.is_active:
        raise HTTPException(status_code=400, detail="Service engineer is inactive")
    if current_user.type_id != 1 and service_engineer.report_to != current_user.id:
        raise HTTPException(status_code=400, detail="Service engineer not under you")

    return service_engineer


def check_ticket_already_assigned(
    db: Session, ticket_id: int, current_user: User, reassign=False
):
    db_ticket = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    ticket = getTicketByID(db=db, id=ticket_id)

    # If the ticket is not currently assigned
    if not db_ticket:
        if not ticket.is_taken:
            return None  
        raise HTTPException(status_code=404, detail="Ticket has not been assigned yet")

    # If we are reassigning, check the ownership
    if reassign:
        # If current user is not the service head who assigned it, check if it's released
        if (
            current_user.type_id != 1
            and db_ticket.service_engineer.report_to != current_user.id
        ):
            raise HTTPException(
                status_code=400, detail="This ticket owner is another service head"
            )
        return db_ticket

    # If the ticket is assigned and we are not reassigning, enforce ownership
    if ticket.is_taken and not reassign:
        raise HTTPException(status_code=400, detail="Ticket has already been assigned")

    return db_ticket


# ===========================================================ticket curd=========================================
def createTicket(db: Session, ticket: TicketCreate):
    customer = getCustomerByID(db=db, id=ticket.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    db.add(
        Ticket(
            customer_id=ticket.customer_id, issue_description=ticket.issue_description
        )
    )
    db.commit()
    return dict(message="Ticket raised")


def displayTickets(db: Session):
    tickets = (
        db.query(Ticket).filter(Ticket.is_taken == False, Ticket.status == True).all()
    )

    if tickets:
        return [
            TicketDisplay(
                ticket_id=ticket.id,
                customer_id=ticket.customer.id,
                customer_name=ticket.customer.name,
                company_name=ticket.customer.company_name,
                address=ticket.customer.address,
                phone=ticket.customer.phone,
                created_at=ticket.created_at,
                is_taken=ticket.is_taken,
                updated_at=ticket.updated_at if ticket.updated_at else None,
                issue_description=ticket.issue_description,
                status=ticket.status,
            )
            for ticket in tickets
        ]
    return []


def displaySpecficTicket(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        return TicketDisplay(
            ticket_id=ticket.id,
            customer_id=ticket.customer.id,
            customer_name=ticket.customer.name,
            company_name=ticket.customer.company_name,
            address=ticket.customer.address,
            phone=ticket.customer.phone,
            created_at=ticket.created_at,
            is_taken=ticket.is_taken,
            updated_at=ticket.updated_at if ticket.updated_at else None,
            issue_description=ticket.issue_description,
            status=ticket.status,
        )


def assignedTickets(db: Session, username: str):
    service_engineer = getUserByusername(db=db, username=username)
    assigned_tickets = (
        db.query(TicketAssign, Ticket)
        .join(Ticket)
        .filter(TicketAssign.service_engineer_id == service_engineer.id)
        .order_by(TicketAssign.created_at.desc())
        .all()
    )
    return DisplayAssignedTicket(assigned_tickets=assigned_tickets)


def assignedTicket(db: Session, username: str, ticket_id: int):
    service_engineer = getUserByusername(db=db, username=username)
    assigned_tickets = (
        db.query(TicketAssign, Ticket)
        .join(Ticket)
        .filter(
            TicketAssign.service_engineer_id == service_engineer.id,
            TicketAssign.ticket_id == ticket_id,
        )
        .order_by(TicketAssign.created_at.desc())
        .all()
    )
    return DisplayAssignedTicket(assigned_tickets=assigned_tickets)


def DisplayAssignedTicket(assigned_tickets: List):
    response_data = [
        AssignedTicketResponse(
            ticket=TicketAssignDisplay(
                ticket_id=ticket_assign.ticket_id,
                service_engineer_username=ticket_assign.service_engineer.username,
                status=ticket_assign.status,
                issue_description=ticket.issue_description,
                assigned_by=ticket_assign.assigned_by.username,
                assigned_date=ticket_assign.assigned_date,
                created_date=ticket_assign.created_at,
            ),
            customer=CustomerDisplay(
                id=ticket.customer.id,
                name=ticket.customer.name,
                address=ticket.customer.address,
                # phone = ticket.customer.phone,
                company_name=ticket.customer.company_name,
            ),
        )
        for ticket_assign, ticket in assigned_tickets
    ]

    return response_data


def ticketUpdate(db: Session, ticket_update: TicketUpdate):
    ticket = getTicketByID(db=db, id=ticket_update.ticket_id)
    if ticket:
        if ticket_update.customer_id:
            customer = getCustomerByID(db=db, id=ticket_update.customer_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            ticket.customer_id = ticket_update.customer_id
        if ticket_update.issue_description:
            ticket.issue_description = ticket_update.issue_description
        ticket.updated_at = func.now()
        db.commit()
        db.refresh(ticket)
        return dict(message="Ticket updated")
    raise HTTPException(status_code=404, detail="Ticket not found")


def ticketStatusChange(
    db: Session, ticket_rejection: TicketRejectionCreate, user_id: int
):
    ticket = getTicketByID(db=db, id=ticket_rejection.ticket_id)
    if ticket:
        db.add(
            TicketRejected(
                user_id=user_id,
                ticket_id=ticket_rejection.ticket_id,
                reason=ticket_rejection.reason,
            )
        )
        ticket.status = False
        db.commit()
        db.refresh(ticket)
        return dict(message="Ticket has been rejected")
    raise HTTPException(status_code=404, detail="ticket not found")


# ==================================================assign operatons=================================================
def assigningTickect(
    db: Session, assigned_by_id: int, ticket_details: TickectAssignCreate
):
    service_engineer = getUserByusername(
        db=db, username=ticket_details.service_engineer_username
    )
    ticket = getTicketByID(db=db, id=ticket_details.ticket_id)
    db.add(
        TicketAssign(
            ticket_id=ticket_details.ticket_id,
            assigned_by_id=assigned_by_id,
            service_engineer_id=service_engineer.id,
            assigned_date=ticket_details.assigned_date,
        )
    )
    ticket.is_taken = True
    ticket.updated_at = func.now()
    db.commit()
    db.refresh(ticket)
    return dict(message="Ticket has been assigned sucessfully")


def reassigningTicket(db: Session, assgin_by: int, resign: TickectReAssign):
    ticket = getTicketByID(db=db, id=resign.ticket_id)
    service_engineer = getUserByusername(
        db=db, username=resign.service_engineer_username
    )
    db_assign = getTicketAssignedByTicketID(db=db, ticket_id=resign.ticket_id)
    db.add(
        TicketAssign(
            ticket_id=resign.ticket_id,
            assigned_by_id=assgin_by,
            service_engineer_id=service_engineer.id,
            assigned_date=resign.assigned_date,
        )
    )

    ticket.updated_at = func.now()
    db_assign.status = "reassigned"
    db.commit()
    db.refresh(ticket)
    return dict(message="Ticket has been reassigned sucessfully")


def historyOfAssigningTicket(db: Session, ticket_id: int):
    tickets = (
        db.query(TicketAssign)
        .filter(TicketAssign.ticket_id == ticket_id)
        .order_by(TicketAssign.created_at)
        .all()
    )
    if tickets:
        return tickets
    raise HTTPException(status_code=404, detail="there is no ticket")


def releasingTickeAssign(db: Session, ticket_id: int):
    db_assign = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    db_ticket = getTicketByID(db=db, id=ticket_id)
    if db_assign:
        db_assign.status = "released"
        db_ticket.is_taken = False
        db.commit()
        db.refresh(db_assign)
        return dict(message="Ticket has been released")


# =====================================================ticket process ===================================================


def getTicketAssigned(db: Session,ticket_id):
    ticket_assigned = (
        db.query(TicketAssign)
        .filter(
            TicketAssign.ticket_id == ticket_id,
        ).order_by(
            TicketAssign.id.desc()
        )
        .first()
    )
    return ticket_assigned


def getTicketProcessByTicketID(db: Session, ticket_id: int,service_engineer_id :int):
    return db.query(TicketProcess).filter(TicketProcess.ticket_id == ticket_id,TicketProcess.service_engineer_id==service_engineer_id).first()


def newTicketProcess(
    db: Session, service_engineer_id: int, details: TicketprocessCreate
):
    ticket_assigned = getTicketAssigned(
        db=db,ticket_id=details.ticket_id
    )
    if details.priority not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Priority not matched")
    db.add(
        TicketProcess(
            ticket_id=details.ticket_id,
            service_engineer_id=service_engineer_id,
            priority=details.priority,
            problem_description = details.problem_description,
            excepted_complete_date=details.excepted_complete_date,
            spare_parts_required=details.spare_parts_required,
        )
    )
    ticket_assigned.status = "on-progress"
    db.commit()
    db.refresh(ticket_assigned)
    return dict(message="ticket process has been added")

def updateProcess(db : Session,service_engineer_id: int, details: TicketProcessUpdate):
    db_ticket_process = getTicketProcessByTicketID(
        db=db, ticket_id=details.ticket_id,service_engineer_id=service_engineer_id
    )
    if details.problem_description:
        db_ticket_process.problem_description = details.problem_description
    if details.priority:
        if details.priority not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Priority not matched")
        db_ticket_process.priority = details.priority
    if details.excepted_complete_date:
        db_ticket_process.excepted_complete_date = details.excepted_complete_date
    if details.spare_parts_required:
        db_ticket_process.spare_parts_required = details.spare_parts_required
    db.commit()
    db.refresh(db_ticket_process)
    return dict(message = "process has been updated")

def addsparePart(db: Session, spare_parts: List[SparePartUpdate], service_engineer_id: int, ticket_id: int):
    db_ticket_process = getTicketProcessByTicketID(
        db=db, ticket_id=ticket_id, service_engineer_id=service_engineer_id
    )
    
    if not db_ticket_process:
        raise HTTPException(status_code=403, detail="Ticket process not found for this service engineer.")

    spare_parts_entries = [
        SpareParts(
            ticket_id=ticket_id,
            part_name=spare_part.part_name,
            quantity=spare_part.quantity,
        )
        for spare_part in spare_parts
    ]
    
    db.add_all(spare_parts_entries) 
    db.commit()  
    return dict(message = "Spare parts added successfully")

def get_service_engineers_under_head(db: Session, current_user: User):
    return db.query(User).filter(User.report_to == current_user.id).all()

def get_spare_part_requests(db: Session, service_engineer_ids: List[int]):
    return (
        db.query(distinct(SpareParts.ticket_id), TicketAssign.service_engineer_id, User.username)
        .join(TicketAssign, SpareParts.ticket_id == TicketAssign.ticket_id)
        .join(User, TicketAssign.service_engineer_id == User.id)
        .filter(
            TicketAssign.service_engineer_id.in_(service_engineer_ids),
            SpareParts.status == 'pending'
        )
        .all()
    )

