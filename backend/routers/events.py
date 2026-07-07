from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.event import Event
from backend.schemas.event import EventCreate, EventResponse

router = APIRouter()

@router.post("/api/ingest", response_model=EventResponse, status_code=201)
def ingest_event(event_in: EventCreate, db: Session = Depends(get_db)):
    db_event = Event(
        object=event_in.object,
        action=event_in.action,
        actor=event_in.actor,
        zone=event_in.zone,
        timestamp=event_in.timestamp,
        confidence=event_in.confidence,
        source_frame=event_in.source_frame
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/api/events", response_model=List[EventResponse])
def get_events(
    date: Optional[str] = Query(None, description="Filter by day (YYYY-MM-DD)"),
    object: Optional[str] = Query(None, description="Filter by object type"),
    actor: Optional[str] = Query(None, description="Filter by actor/person"),
    db: Session = Depends(get_db)
):
    query = db.query(Event)

    # Apply date filter
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(func.date(Event.timestamp) == parsed_date)
        except ValueError:
            # "get with a bad/nonexistent filter returns empty list not an error"
            return []

    # Apply object filter
    if object:
        query = query.filter(Event.object == object)

    # Apply actor filter
    if actor:
        query = query.filter(Event.actor == actor)

    # Returns most recent first
    query = query.order_by(Event.timestamp.desc())

    return query.all()
