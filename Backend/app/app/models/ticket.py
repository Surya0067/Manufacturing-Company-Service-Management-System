from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from db.db import Base


class Ticket(Base):
    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    issue_description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True)
    is_taken = Column(Boolean, default=False)
    status = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="tickets")
    ticket_rejected = relationship("TicketRejected", back_populates="ticket")
    ticket_assign = relationship("TicketAssign", back_populates="ticket")
