from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.event import Event
from backend.schemas.timeline import TimelineResponse

router = APIRouter()

@router.get("/api/timeline", response_model=TimelineResponse)
def get_timeline(
    date: Optional[str] = Query(None, description="Date for the timeline (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        # Get the date of the most recent event in the database
        most_recent_event = db.query(Event).order_by(Event.timestamp.desc()).first()
        if most_recent_event:
            target_date = most_recent_event.timestamp.date()
        else:
            target_date = datetime.now().date()

    # Query all events for target_date
    events = db.query(Event).filter(
        func.date(Event.timestamp) == target_date
    ).order_by(Event.timestamp.asc()).all()

    morning = []
    afternoon = []
    evening = []
    night = []

    for event in events:
        hour = event.timestamp.hour
        # morning: 05:00 - 11:59 (hour 5 to 11)
        # afternoon: 12:00 - 14:59 (hour 12 to 14)
        # evening: 15:00 - 18:59 (hour 15 to 18)
        # night: 19:00 - 04:59 (hour >= 19 or hour < 5)
        if 5 <= hour < 12:
            morning.append(event)
        elif 12 <= hour < 15:
            afternoon.append(event)
        elif 15 <= hour < 19:
            evening.append(event)
        else:
            night.append(event)

    return TimelineResponse(
        date=target_date.strftime("%Y-%m-%d"),
        morning=morning,
        afternoon=afternoon,
        evening=evening,
        night=night
    )
