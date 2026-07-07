import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Override database URL for testing
TEST_DATABASE_URL = "sqlite:///./data/test_echomind.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from backend.database import Base, get_db
from backend.main import app

# Setup test DB engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Resolve the physical absolute path for cleanup
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(backend_dir)
    db_relative_path = TEST_DATABASE_URL.replace("sqlite:///./", "")
    db_absolute_path = os.path.join(root_dir, db_relative_path)
    os.makedirs(os.path.dirname(db_absolute_path), exist_ok=True)

    # Initialize tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(db_absolute_path):
        try:
            os.remove(db_absolute_path)
        except PermissionError:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_ingest_creates_row(client):
    payload = {
        "object": "glasses",
        "action": "placed",
        "actor": "patient",
        "zone": "dining table",
        "timestamp": "2026-07-07T14:15:00",
        "confidence": 0.88,
        "source_frame": "dining_table_001.jpg"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["object"] == "glasses"
    assert data["actor"] == "patient"
    assert data["zone"] == "dining table"

def test_get_events_no_filters(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert events[0]["object"] == "glasses"

def test_get_events_object_filter(client):
    # Ingest a second event with a different object
    payload = {
        "object": "keys",
        "action": "picked_up",
        "actor": "caregiver",
        "zone": "study table",
        "timestamp": "2026-07-07T14:20:00",
        "confidence": 0.92,
        "source_frame": "keys_002.jpg"
    }
    client.post("/api/ingest", json=payload)

    # Filter for 'keys'
    response = client.get("/api/events?object=keys")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["object"] == "keys"

def test_get_events_bad_or_nonexistent_filter_returns_empty(client):
    # Filter for nonexistent object
    response = client.get("/api/events?object=nonexistent_item")
    assert response.status_code == 200
    assert response.json() == []

    # Filter for nonexistent actor
    response = client.get("/api/events?actor=nonexistent_person")
    assert response.status_code == 200
    assert response.json() == []

    # Filter with invalid date string
    response = client.get("/api/events?date=not-a-valid-date")
    assert response.status_code == 200
    assert response.json() == []
