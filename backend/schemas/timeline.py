from typing import List
from pydantic import BaseModel, Field
from backend.schemas.event import EventResponse

class TimelineResponse(BaseModel):
    date: str = Field(..., description="The date of the timeline in YYYY-MM-DD format")
    morning: List[EventResponse] = Field(..., description="Events that occurred in the morning (05:00 - 11:59)")
    afternoon: List[EventResponse] = Field(..., description="Events that occurred in the afternoon (12:00 - 14:59)")
    evening: List[EventResponse] = Field(..., description="Events that occurred in the evening (15:00 - 18:59)")
    night: List[EventResponse] = Field(..., description="Events that occurred in the night (19:00 - 04:59)")
