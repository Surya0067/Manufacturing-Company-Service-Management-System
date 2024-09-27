from db.db import Base
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    func,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship


class TravelExpenseReports(Base):
    __tablename__ = "travel_expense_reports"

    id = Column(Integer, primary_key=True)
    service_engineer_ID = Column(Integer, ForeignKey("user.id"))
    ticket_ID = Column(Integer, ForeignKey("ticket.id"))
    expense_details = Column(String(255), nullable=False)
    total_amount = Column(Float, nullable=False)
    image_path = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    status = Column(String(50), default="Pending")
    status_by = Column(Integer, ForeignKey("user.id"))
    status_at = Column(DateTime, nullable=True)

    service_engineer = relationship(
        "User", foreign_keys=[service_engineer_ID], back_populates="travel_expenses"
    )
    status_changer = relationship(
        "User", foreign_keys=[status_by], back_populates="approved_expenses"
    )
    ticket = relationship("Ticket", back_populates="travel_expenses")
