from sqlalchemy import create_engine  
from core.config import settings
from sqlalchemy.orm import sessionmaker,declarative_base

engine = create_engine(settings.DATA_BASE)
SessionLocal = sessionmaker(autocommit = False,bind = engine)
Base = declarative_base()