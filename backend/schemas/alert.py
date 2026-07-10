from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AlertResponse(BaseModel):
    object: str
    actor: Optional[str] = None
    zone: Optional[str] = None
    last_action: str
    last_seen: datetime
    minutes_elapsed: float
    message: str
    severity: str  # "warning" | "critical"