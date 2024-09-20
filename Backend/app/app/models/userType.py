from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.db import Base


class UserType(Base):
    __tablename__ = "user_type"

    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship("User", back_populates="user_type")
