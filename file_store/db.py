from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import Session, sessionmaker

from file_store.connection import get_engine

Base = declarative_base()


class FileEvent(Base):
    __tablename__ = "file_event"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    uploaded_at = Column(DateTime)


class Database:
    def __init__(self):
        self.engine = get_engine("pg8000")
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def __enter__(self):
        self.session = self.SessionLocal()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def fetch_file_events(self) -> List[FileEvent]:
        events = self.session.query(FileEvent).all()
        return events

    def insert_file_event(self, file_name: str, uploaded_at: datetime):
        new_event = FileEvent(file_name=file_name, uploaded_at=uploaded_at)
        self.session.add(new_event)
        self.session.commit()
        self.session.refresh(new_event)
