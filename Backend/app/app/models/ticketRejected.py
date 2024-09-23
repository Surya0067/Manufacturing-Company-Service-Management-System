from db.db import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship


class TicketRejected(Base):
    __tablename__ = "ticket_rejected"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("ticket.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    reason = Column(String(255), nullable=False)

    user = relationship("User", back_populates="ticket_rejected")
    ticket = relationship("Ticket", back_populates="ticket_rejected")
