from sqlalchemy import Boolean, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from db.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(50), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    email = Column(String(50), unique=True)
    phone = Column(String(10), unique=True)
    type_id = Column(Integer, ForeignKey("user_type.id"), nullable=False)
    report_to = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    user_type = relationship("UserType", back_populates="users")
    ticket_rejected = relationship("TicketRejected", back_populates="user")
