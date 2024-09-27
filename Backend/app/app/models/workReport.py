from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Date
from sqlalchemy.orm import relationship
from db.db import Base


class WorkReport(Base):
    __tablename__ = "work_report"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    report = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    report_date = Column(Date, nullable=False)

    user = relationship("User", back_populates="work_report")
