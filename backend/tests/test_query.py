import os
import pytest
import httpx
import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Override database URL for testing
TEST_DATABASE_URL = "sqlite:///./data/test_query_echomind.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Helper to clean environment before import
if "FIREWORKS_API_KEY" in os.environ:
    del os.environ["FIREWORKS_API_KEY"]

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

@pytest.fixture(autouse=True)
def clean_db(db_session):
    from backend.models.event import Event
    db_session.query(Event).delete()
    db_session.commit()
    yield


def test_query_matching_mock_mode(client):
    # Ingest an event to match
    payload = {
        "object": "keys",
        "action": "placed",
        "actor": "patient",
        "zone": "study table",
        "timestamp": "2026-07-07T14:15:00",
        "confidence": 0.90,
        "source_frame": "keys_frame.jpg"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 201

    # Ensure API key is missing
    with patch.dict(os.environ, {}):
        if "FIREWORKS_API_KEY" in os.environ:
            del os.environ["FIREWORKS_API_KEY"]
            
        query_payload = {"question": "Where are my keys?"}
        response = client.post("/api/query", json=query_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "keys" in data["answer"]
        assert "study table" in data["answer"]
        assert data["mode"] == "mock"
        assert len(data["referenced_events"]) >= 1
        assert data["referenced_events"][0]["object"] == "keys"

def test_query_no_matching_events_mock_mode(client):
    with patch.dict(os.environ, {}):
        if "FIREWORKS_API_KEY" in os.environ:
            del os.environ["FIREWORKS_API_KEY"]
            
        query_payload = {"question": "Where is my remote?"}
        response = client.post("/api/query", json=query_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "I don't have a record of that yet"
        assert data["referenced_events"] == []
        assert data["mode"] == "mock"

def test_query_malformed_question(client):
    # 1. Empty string
    response = client.post("/api/query", json={"question": ""})
    assert response.status_code == 422

    # 2. Only whitespace
    response = client.post("/api/query", json={"question": "   "})
    assert response.status_code == 422

    # 3. Missing question field
    response = client.post("/api/query", json={})
    assert response.status_code == 422

def test_ask_alias_mock_mode(client):
    # Ingest an event to match
    payload = {
        "object": "mug",
        "action": "observed",
        "actor": "caregiver",
        "zone": "dining table",
        "timestamp": "2026-07-07T15:30:00",
        "confidence": 0.85,
        "source_frame": "mug_frame.jpg"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 201

    with patch.dict(os.environ, {}):
        if "FIREWORKS_API_KEY" in os.environ:
            del os.environ["FIREWORKS_API_KEY"]
            
        query_payload = {"question": "Who had the mug?"}
        response = client.post("/api/ask", json=query_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "mug" in data["answer"]
        assert data["mode"] == "mock"
        assert len(data["referenced_events"]) >= 1

def test_query_live_mode_with_mock_api(client):
    # Ingest an event to match
    payload = {
        "object": "glasses",
        "action": "placed",
        "actor": "patient",
        "zone": "dining table",
        "timestamp": "2026-07-07T14:15:00",
        "confidence": 0.88,
        "source_frame": "glasses_frame.jpg"
    }
    response = client.post("/api/ingest", json=payload)
    assert response.status_code == 201

    # Force API key to be set
    with patch.dict(os.environ, {"FIREWORKS_API_KEY": "fake-api-key"}):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "You placed your glasses on the dining table."
                    }
                }
            ]
        }

        # Mock the request inside llm.py
        with patch("backend.services.llm.httpx.post", return_value=mock_response) as mock_post:
            query_payload = {"question": "Where are my glasses?"}
            response = client.post("/api/query", json=query_payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "You placed your glasses on the dining table."
            assert data["mode"] == "live"
            assert len(data["referenced_events"]) >= 1
            mock_post.assert_called_once()

def test_multi_event_chronological_mock(client):
    # Ingest 3 events in reverse chronological order
    events_data = [
        {"object": "glasses", "action": "placed", "actor": "patient", "zone": "dining table", "timestamp": "2026-07-07T09:00:00", "confidence": 0.90},
        {"object": "glasses", "action": "picked_up", "actor": "patient", "zone": "dining table", "timestamp": "2026-07-07T10:00:00", "confidence": 0.90},
        {"object": "glasses", "action": "placed", "actor": "patient", "zone": "study table", "timestamp": "2026-07-07T11:00:00", "confidence": 0.90},
    ]
    for ev in events_data:
        client.post("/api/ingest", json=ev)
        
    query_payload = {"question": "Where are my glasses today?"}
    response = client.post("/api/query", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    
    # Check that mock answer contains details from all events and they are in chronological order
    answer = data["answer"]
    assert "dining table" in answer
    assert "study table" in answer
    # Chronological index check: 9:00 should come before 10:00 and 11:00 in text
    idx_9 = answer.find("09:00 AM")
    idx_10 = answer.find("10:00 AM")
    idx_11 = answer.find("11:00 AM")
    assert idx_9 < idx_10 < idx_11
    
    # Now ingest 3 more events (total 6 events) to test capping at 5
    extra_events = [
        {"object": "glasses", "action": "picked_up", "actor": "patient", "zone": "study table", "timestamp": "2026-07-07T12:00:00", "confidence": 0.90},
        {"object": "glasses", "action": "placed", "actor": "patient", "zone": "bedside shelf", "timestamp": "2026-07-07T13:00:00", "confidence": 0.90},
        {"object": "glasses", "action": "picked_up", "actor": "patient", "zone": "bedside shelf", "timestamp": "2026-07-07T14:00:00", "confidence": 0.90},
    ]
    for ev in extra_events:
        client.post("/api/ingest", json=ev)
        
    response = client.post("/api/query", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should cap at 5 and append "and a few earlier events."
    assert data["answer"].endswith("and a few earlier events.")
    assert len(data["referenced_events"]) == 5

def test_time_relative_query(client):
    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    events = [
        {"object": "watch", "action": "placed", "actor": "patient", "zone": "desk", "timestamp": f"{today_str}T08:00:00", "confidence": 0.90},
        {"object": "watch", "action": "picked_up", "actor": "patient", "zone": "desk", "timestamp": f"{today_str}T20:00:00", "confidence": 0.90},
        {"object": "watch", "action": "placed", "actor": "patient", "zone": "drawer", "timestamp": f"{yesterday_str}T14:00:00", "confidence": 0.90},
    ]
    for ev in events:
        client.post("/api/ingest", json=ev)
        
    # Query "today"
    resp = client.post("/api/query", json={"question": "Where is my watch today?"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["referenced_events"]) == 2
    assert "desk" in data["answer"]
    assert "drawer" not in data["answer"]
    
    # Query "yesterday"
    resp = client.post("/api/query", json={"question": "Where was my watch yesterday?"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["referenced_events"]) == 1
    assert "drawer" in data["answer"]
    assert "desk" not in data["answer"]
    
    # Query "this morning"
    resp = client.post("/api/query", json={"question": "Where was my watch this morning?"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["referenced_events"]) == 1
    assert "08:00 AM" in data["answer"]
    assert "08:00 PM" not in data["answer"]
    
    # Query future date / no match
    resp = client.post("/api/query", json={"question": "Where is my watch tomorrow?"})
    assert resp.status_code == 200
    assert resp.json()["answer"] == "I don't have a record of that yet"

def test_follow_up_conversational_context(client):
    events = [
        {"object": "keys", "action": "placed", "actor": "patient", "zone": "kitchen counter", "timestamp": "2026-07-07T09:00:00", "confidence": 0.90},
        {"object": "keys", "action": "picked_up", "actor": "patient", "zone": "kitchen counter", "timestamp": "2026-07-07T10:00:00", "confidence": 0.90},
        {"object": "keys", "action": "placed", "actor": "patient", "zone": "bedroom table", "timestamp": "2026-07-07T11:00:00", "confidence": 0.90},
    ]
    for ev in events:
        client.post("/api/ingest", json=ev)
        
    # Turn 1: Where are my keys? -> Should return bedroom table event (11:00)
    resp1 = client.post("/api/query", json={"question": "Where are my keys?"})
    data1 = resp1.json()
    assert "bedroom table" in data1["answer"]
    
    # Turn 2: And before that? -> Should return picked up event (10:00)
    history1 = [
        {"question": "Where are my keys?", "answer": data1["answer"]}
    ]
    resp2 = client.post("/api/query", json={"question": "And before that?", "conversation_history": history1})
    data2 = resp2.json()
    assert "picked up" in data2["answer"]
    assert "kitchen counter" in data2["answer"]
    assert "bedroom table" not in data2["answer"]
    
    # Turn 3: And before that? -> Should return placed event (09:00)
    history2 = history1 + [
        {"question": "And before that?", "answer": data2["answer"]}
    ]
    resp3 = client.post("/api/query", json={"question": "And before that?", "conversation_history": history2})
    data3 = resp3.json()
    assert "placed" in data3["answer"]
    assert "kitchen counter" in data3["answer"]
    assert "bedroom table" not in data3["answer"]

def test_confidence_hedging_mock(client, db_session):
    from backend.models.event import Event
    
    # 1. High confidence (>= 0.85) -> plain statement
    client.post("/api/ingest", json={"object": "mug", "action": "placed", "actor": "patient", "zone": "dining table", "timestamp": "2026-07-07T09:00:00", "confidence": 0.95})
    resp = client.post("/api/query", json={"question": "Where is my mug?"})
    assert resp.json()["answer"].startswith("Your mug was placed")
    
    # Cleanup
    db_session.query(Event).delete()
    db_session.commit()
    
    # 2. Medium confidence (0.6-0.84) -> gentle hedge
    client.post("/api/ingest", json={"object": "mug", "action": "placed", "actor": "patient", "zone": "dining table", "timestamp": "2026-07-07T09:00:00", "confidence": 0.75})
    resp = client.post("/api/query", json={"question": "Where is my mug?"})
    assert resp.json()["answer"].startswith("It looks like your mug was placed")
    
    # Cleanup
    db_session.query(Event).delete()
    db_session.commit()
    
    # 3. Low confidence (< 0.6) -> strong hedge + confirm suggestion
    client.post("/api/ingest", json={"object": "mug", "action": "placed", "actor": "patient", "zone": "dining table", "timestamp": "2026-07-07T09:00:00", "confidence": 0.45})
    resp = client.post("/api/query", json={"question": "Where is my mug?"})
    assert "I think I saw your mug" in resp.json()["answer"]
    assert "but I'm not fully sure — you may want to double check" in resp.json()["answer"]

def test_graceful_degradation_and_validation(client):
    # Ingest one event
    client.post("/api/ingest", json={"object": "wallet", "action": "placed", "actor": "patient", "zone": "sofa", "timestamp": "2026-07-07T12:00:00", "confidence": 0.90})
    
    # Force API key to run in live mode
    with patch.dict(os.environ, {"FIREWORKS_API_KEY": "fake-key"}):
        # 1. API Failure fallback
        # Mock httpx.post to raise an exception (RequestError)
        with patch("backend.services.llm.httpx.post", side_effect=httpx.RequestError("API timeout")):
            resp = client.post("/api/query", json={"question": "Where is my wallet?"})
            assert resp.status_code == 200
            data = resp.json()
            assert "Your wallet was placed" in data["answer"]
            assert data["mode"] == "mock_fallback"
            
        # 2. Grounding failure fallback
        # Mock LLM response to be completely unrelated (does not mention "wallet", "sofa", "placed")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "I recommend you drink at least eight glasses of water every single day to stay hydrated."
                    }
                }
            ]
        }
        with patch("backend.services.llm.httpx.post", return_value=mock_response):
            resp = client.post("/api/query", json={"question": "Where is my wallet?"})
            assert resp.status_code == 200
            data = resp.json()
            # It should discard the LLM output and return the mock response instead
            assert "Your wallet was placed" in data["answer"]
            assert data["mode"] == "mock_fallback"

