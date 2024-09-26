from sqlalchemy import Boolean,Column,Integer,String,DateTime,func,ForeignKey,Float
from sqlalchemy.orm import relationship
from db.db import Base

class SpareParts(Base):
  __tablename__ = "spare_parts"

  id = Column(Integer,primary_key=True)
  ticket_id = Column(Integer,ForeignKey("ticket.id"),nullable=False)
  part_name = Column(String(50),nullable=False)
  quantity = Column(Float,nullable=False)
  unit_price = Column(Integer,nullable=True)
  requested_at = Column(DateTime,default=func.now())
  status = Column(String(50),default="pending")
  issued_at = Column(DateTime,nullable=True)
  issued_by = Column(Integer,ForeignKey("user.id"),nullable=True)

  user = relationship("User", back_populates="spare_part")
  ticket = relationship("Ticket", back_populates="spare_parts")