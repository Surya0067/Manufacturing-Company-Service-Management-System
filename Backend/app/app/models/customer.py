from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from db.db import Base


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    address = Column(String(100), nullable=False)
    company_name = Column(String(100))
    created_at = Column(DateTime, default=func.now())

    tickets = relationship("Ticket", back_populates="customer")
