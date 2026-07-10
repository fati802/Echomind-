import os
import backend.config
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers.events import router as events_router
from backend.routers.query import router as query_router
from backend.routers.timeline import router as timeline_router
from backend.services import llm
from backend.routers.upload import router as upload_router
from backend.routers import alerts
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://echomind-psi.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router)
app.include_router(query_router)
app.include_router(timeline_router)
app.include_router(upload_router)
app.include_router(alerts.router)
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/llm-status")
def get_llm_status():
    provider = os.getenv("LLM_PROVIDER", "amd").lower().strip()
    amd_configured = bool(os.getenv("AMD_DEV_CLOUD_API_URL") and os.getenv("AMD_DEV_CLOUD_API_KEY"))
    fireworks_key_present = bool(os.getenv("FIREWORKS_API_KEY"))

    amd_reachable = False
    if amd_configured:
        amd_reachable = llm.check_amd_health()

    # Determine effective mode
    if provider == "amd":
        if amd_reachable:
            effective_mode = "amd"
        elif fireworks_key_present:
            effective_mode = "fireworks_fallback"
        else:
            effective_mode = "mock_fallback"
    elif provider == "fireworks":
        if fireworks_key_present:
            effective_mode = "fireworks"
        elif amd_reachable:
            effective_mode = "amd"
        else:
            effective_mode = "mock_fallback"
    else:
        effective_mode = "mock"

    return {
        "configured_provider": provider,
        "amd_reachable": amd_reachable,
        "fireworks_key_present": fireworks_key_present,
        "effective_mode": effective_mode
    }
