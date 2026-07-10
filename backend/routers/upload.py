import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.inference import process_video
from backend.services.event_engine import generate_events
from backend.database import SessionLocal
from backend.models.event import Event

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):

    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Please upload a video file.")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    detections, fps = process_video(str(file_path))
    events = generate_events(detections, fps=fps)

    db = SessionLocal()
    try:
        for e in events:
            db.add(Event(**e))
        db.commit()
    finally:
        db.close()

    return {
        "message": "Video uploaded, processed, and events saved",
        "filename": file.filename,
        "detections_count": len(detections),
        "events_count": len(events)
    }