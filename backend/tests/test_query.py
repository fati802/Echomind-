import os
import pytest
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
