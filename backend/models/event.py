from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    object = Column(String, nullable=False)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=True)
    zone = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    confidence = Column(Float, nullable=False)
    source_frame = Column(String, nullable=True)
