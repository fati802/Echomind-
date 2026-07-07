import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./data/test_timeline_echomind.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from backend.database import Base, get_db
from backend.main import app

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(backend_dir)
    db_relative_path = TEST_DATABASE_URL.replace("sqlite:///./", "")
    db_absolute_path = os.path.join(root_dir, db_relative_path)
    os.makedirs(os.path.dirname(db_absolute_path), exist_ok=True)

    Base.metadata.create_all(bind=engine)
    yield
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

def test_timeline_categorization_and_boundaries(client):
    target_date = "2026-07-08"
    
    events_payloads = [
        # Night bounds (00:00:00 to 04:59:59)
        {"object": "water", "action": "drank", "timestamp": f"{target_date}T00:00:00", "actor": "patient", "zone": "kitchen", "confidence": 0.9},
        {"object": "pill", "action": "taken", "timestamp": f"{target_date}T04:59:59", "actor": "patient", "zone": "bedroom", "confidence": 0.9},
        
        # Morning bounds (05:00:00 to 11:59:59)
        {"object": "keys", "action": "placed", "timestamp": f"{target_date}T05:00:00", "actor": "patient", "zone": "shelf", "confidence": 0.9},
        {"object": "coffee", "action": "drank", "timestamp": f"{target_date}T11:59:59", "actor": "patient", "zone": "kitchen", "confidence": 0.9},
        
        # Afternoon bounds (12:00:00 to 14:59:59)
        {"object": "lunch", "action": "eaten", "timestamp": f"{target_date}T12:00:00", "actor": "patient", "zone": "dining room", "confidence": 0.9},
        {"object": "glasses", "action": "picked_up", "timestamp": f"{target_date}T14:59:59", "actor": "patient", "zone": "living room", "confidence": 0.9},
        
        # Evening bounds (15:00:00 to 18:59:59)
        {"object": "tea", "action": "drank", "timestamp": f"{target_date}T15:00:00", "actor": "patient", "zone": "kitchen", "confidence": 0.9},
        {"object": "book", "action": "read", "timestamp": f"{target_date}T18:59:59", "actor": "patient", "zone": "living room", "confidence": 0.9},
        
        # Night bounds (19:00:00 to 23:59:59)
        {"object": "television", "action": "watched", "timestamp": f"{target_date}T19:00:00", "actor": "patient", "zone": "living room", "confidence": 0.9},
        {"object": "medicine", "action": "taken", "timestamp": f"{target_date}T23:59:59", "actor": "patient", "zone": "bedroom", "confidence": 0.9},
    ]

    for payload in events_payloads:
        resp = client.post("/api/ingest", json=payload)
        assert resp.status_code == 201

    # Request the timeline for target_date
    response = client.get(f"/api/timeline?date={target_date}")
    assert response.status_code == 200
    data = response.json()

    assert data["date"] == target_date
    
    # Morning: coffee at 11:59:59, keys at 05:00:00
    assert len(data["morning"]) == 2
    assert data["morning"][0]["object"] == "keys"
    assert data["morning"][1]["object"] == "coffee"

    # Afternoon: lunch at 12:00:00, glasses at 14:59:59
    assert len(data["afternoon"]) == 2
    assert data["afternoon"][0]["object"] == "lunch"
    assert data["afternoon"][1]["object"] == "glasses"

    # Evening: tea at 15:00:00, book at 18:59:59
    assert len(data["evening"]) == 2
    assert data["evening"][0]["object"] == "tea"
    assert data["evening"][1]["object"] == "book"

    # Night: water (00:00:00), pill (04:59:59), television (19:00:00), medicine (23:59:59)
    # Ordered ascending
    assert len(data["night"]) == 4
    assert data["night"][0]["object"] == "water"
    assert data["night"][1]["object"] == "pill"
    assert data["night"][2]["object"] == "television"
    assert data["night"][3]["object"] == "medicine"

def test_timeline_default_date(client):
    response = client.get("/api/timeline")
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2026-07-08"
    assert len(data["night"]) == 4

def test_timeline_invalid_date(client):
    response = client.get("/api/timeline?date=invalid-date-format")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid date format. Use YYYY-MM-DD."
