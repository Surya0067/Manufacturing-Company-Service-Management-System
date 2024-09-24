from typing import Any, Dict, Optional, Union
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException
from curd.customer import getCustomerByID
from curd.user import getUserByID, getUserByusername
from models import Ticket, TicketRejected, TicketAssign, User
from schemas import *


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

# def check_ticket_already_assigned(
#     db: Session, ticket_id: int, current_user: User, reassign=False
# ):
#     db_ticket = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
#     ticket = getTicketByID(db=db, id=ticket_id)

#     # If the ticket is not currently assigned
#     if not db_ticket:
#         if not ticket.is_taken:
#             return None  # Ticket can be assigned as it's not taken
#         raise HTTPException(status_code=404, detail="Ticket has not been assigned yet")

#     # If we are reassigning, check the ownership
#     if reassign:
#         # If current user is not the service head who assigned it, check if it's released
#         if current_user.type_id != 1 and db_ticket.service_engineer.report_to != current_user.id:
#             raise HTTPException(status_code=400, detail="This ticket owner is another service head")
#         return db_ticket

#     # If the ticket is assigned and we are not reassigning, enforce ownership
#     if ticket.is_taken and not reassign:
#         raise HTTPException(status_code=400, detail="Ticket has already been assigned")

#     return db_ticket


def check_ticket_already_assigned(
    db: Session, ticket_id: int, current_user: User, reassign=False
):
    db_ticket = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    ticket = getTicketByID(db=db, id=ticket_id)

    # If the ticket is not currently assigned
    if not db_ticket:
        if not ticket.is_taken:
            return None  # Ticket can be assigned as it's not taken
        raise HTTPException(status_code=404, detail="Ticket has not been assigned yet")

    # If we are reassigning, check the ownership
    if reassign:
        # If current user is not the service head who assigned it, check if it's released
        if current_user.type_id != 1 and db_ticket.service_engineer.report_to != current_user.id:
            raise HTTPException(status_code=400, detail="This ticket owner is another service head")
        return db_ticket

    # If the ticket is assigned and we are not reassigning, enforce ownership
    if ticket.is_taken and not reassign:
        raise HTTPException(status_code=400, detail="Ticket has already been assigned")

    return db_ticket




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

def cancellingTickeAssign(db: Session, ticket_id: int):
    db_assign = getTicketAssignedByTicketID(db=db, ticket_id=ticket_id)
    db_ticket = getTicketByID(db=db, id=ticket_id)
    if db_assign:
        db_assign.status = "cancelled" 
        db_ticket.is_taken = False 
        db.commit()
        db.refresh(db_assign)
        return dict(message="Ticket has been released")
