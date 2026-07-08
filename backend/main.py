import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers.events import router as events_router
from backend.routers.query import router as query_router
from backend.routers.timeline import router as timeline_router
from backend.services import llm

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Enable CORS for http://localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router)
app.include_router(query_router)
app.include_router(timeline_router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/llm-status")
def get_llm_status():
    provider = os.getenv("LLM_PROVIDER", "amd").lower().strip()
    amd_configured = bool(os.getenv("AMD_DEV_CLOUD_API_URL") and os.getenv("AMD_DEV_CLOUD_API_KEY"))
    fireworks_configured = bool(os.getenv("FIREWORKS_API_KEY"))

    amd_reachable = False
    if amd_configured:
        amd_reachable = llm.check_amd_health()

    fireworks_reachable = False
    if fireworks_configured:
        fireworks_reachable = llm.check_fireworks_health()

    # Determine if mock mode is the effective fallback
    if provider == "mock":
        mock_fallback = True
    elif provider == "amd":
        mock_fallback = not (amd_reachable or fireworks_reachable)
    elif provider == "fireworks":
        mock_fallback = not (fireworks_reachable or amd_reachable)
    else:
        mock_fallback = True

    return {
        "primary_provider": provider,
        "amd_reachable": amd_reachable,
        "mock_effective_fallback": mock_fallback
    }
