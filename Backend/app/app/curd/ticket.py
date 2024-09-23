from typing import Any, Dict, Optional, Union
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from fastapi import HTTPException, status
from curd.customer import getCustomerByID
from models import Ticket, TicketRejected
from schemas import *


def getTicketByID(db: Session, id: int):
    return db.query(Ticket).filter(Ticket.id == id).first()


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
    # Query only the Ticket model, SQLAlchemy will automatically load the related Customer due to the relationship
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
