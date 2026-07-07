from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class EventBase(BaseModel):
    object: str = Field(..., description="The name of the object (e.g. glasses, medicine box)")
    action: str = Field(..., description="The action performed (e.g. placed, picked_up)")
    actor: Optional[str] = Field(None, description="The person performing the action (patient/caregiver)")
    zone: Optional[str] = Field(None, description="The location/zone where it happened")
    timestamp: datetime = Field(..., description="Date and time of the event")
    confidence: float = Field(..., description="Model confidence score")
    source_frame: Optional[str] = Field(None, description="Reference path or identifier for source video frame")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

    model_config = {
        "from_attributes": True
    }
