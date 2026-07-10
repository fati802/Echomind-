from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.schemas.alert import AlertResponse
from backend.services.alert_engine import generate_alerts

router = APIRouter()

@router.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return generate_alerts(db)