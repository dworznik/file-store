from sqlalchemy import Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata


class FileEvent(Base):
    __tablename__ = "file_event"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
