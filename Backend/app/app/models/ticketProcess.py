from sqlalchemy import Boolean,Column,Integer,String,DateTime,func,ForeignKey,Float
from sqlalchemy.orm import relationship
from db.db import Base


class TicketProcess(Base):
    __tablename__ = "ticket_process"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=False)
    service_engineer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    problem_description = Column(String(255), nullable=False)
    priority = Column(String(50), nullable=False)
    excepted_complete_date = Column(DateTime, nullable=False)
    actual_complete_date = Column(DateTime, nullable=True)
    spare_parts_required = Column(Boolean, nullable=False)
    cost = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="on-progress")
    created_at = Column(DateTime, default=func.now())

    ticket = relationship("Ticket", back_populates="ticket_process")
    user = relationship("User", back_populates="ticket_process")
