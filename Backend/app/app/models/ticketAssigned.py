from db.db import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship


class TicketAssign(Base):
    __tablename__ = "ticket_assign"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("ticket.id"))
    assigned_by_id = Column(Integer, ForeignKey("user.id"))
    service_engineer_id = Column(Integer, ForeignKey("user.id"))
    assigned_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())

    assigned_by = relationship(
        "User", foreign_keys=[assigned_by_id], back_populates="tickets_assigned_by"
    )
    service_engineer = relationship(
        "User", foreign_keys=[service_engineer_id], back_populates="tickets_as_engineer"
    )
    ticket = relationship("Ticket", back_populates="ticket_assign")
