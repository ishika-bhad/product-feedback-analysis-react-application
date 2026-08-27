import os
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force testing environment settings
os.environ["DATABASE_URL"] = "sqlite:///./test_sentiment.db"
os.environ["API_BEARER_TOKEN"] = "testtoken123"

from backend.app.main import app
from backend.app.database.connection import get_db
from backend.app.models.base import Base
from backend.app.config.settings import settings

# Test Database Engine
TEST_DB_URL = "sqlite:///./test_sentiment.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override FastAPI get_db dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Setup: Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: Drop tables and remove file
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_sentiment.db"):
        os.remove("test_sentiment.db")

def test_health_probe():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "sentiment-analysis-backend"}

def test_auth_header_missing():
    payload = {
        "request_id": str(uuid.uuid4()),
        "product_name": "Test Gizmo",
        "product_feedback": "Perfect widget!"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 401
    resp_body = response.json()
    assert resp_body["success"] is False
    assert "token is missing" in resp_body["error_message"].lower()

def test_auth_header_invalid():
    payload = {
        "request_id": str(uuid.uuid4()),
        "product_name": "Test Gizmo",
        "product_feedback": "Perfect widget!"
    }
    response = client.post(
        "/api/feedback",
        json=payload,
        headers={"Authorization": "Bearer invalid_token_123"}
    )
    assert response.status_code == 401
    resp_body = response.json()
    assert resp_body["success"] is False
    assert "invalid" in resp_body["error_message"].lower()

def test_feedback_submission_success():
    req_id = str(uuid.uuid4())
    payload = {
        "request_id": req_id,
        "product_name": "Widget X",
        "product_feedback": "This is an amazing and awesome product! So easy and helpful."
    }
    response = client.post(
        "/api/feedback",
        json=payload,
        headers={"Authorization": "Bearer testtoken123"}
    )
    assert response.status_code == 201
    resp_body = response.json()
    assert resp_body["success"] is True
    assert resp_body["data"]["request_id"] == req_id
    assert resp_body["data"]["product_name"] == "Widget X"
    assert resp_body["data"]["sentiment"] == "positive"
    assert resp_body["data"]["confidence"] > 0.5

def test_feedback_submission_validation():
    # Empty product name
    payload = {
        "request_id": str(uuid.uuid4()),
        "product_name": "  ",
        "product_feedback": "Good design."
    }
    response = client.post(
        "/api/feedback",
        json=payload,
        headers={"Authorization": "Bearer testtoken123"}
    )
    assert response.status_code == 422
    resp_body = response.json()
    assert resp_body["success"] is False
    assert "validation failed" in resp_body["error_message"].lower()

def test_get_historical_sentiment_success():
    headers = {"Authorization": "Bearer testtoken123"}
    prod_name = "Super Gadget"
    
    # Submit first feedback
    r1 = str(uuid.uuid4())
    client.post("/api/feedback", json={
        "request_id": r1,
        "product_name": prod_name,
        "product_feedback": "Love this gadget, it is excellent and beautiful!"
    }, headers=headers)

    # Submit second feedback
    r2 = str(uuid.uuid4())
    res = client.post("/api/feedback", json={
        "request_id": r2,
        "product_name": prod_name,
        "product_feedback": "Terrible. It is broken and slow."
    }, headers=headers)
    
    product_id = res.json()["data"]["product_id"]

    # Retrieve history
    retrieval_id = str(uuid.uuid4())
    history_headers = {
        "Authorization": "Bearer testtoken123",
        "x-request-id": retrieval_id
    }
    response = client.get(f"/api/feedback/historical/{product_id}", headers=history_headers)
    assert response.status_code == 200
    
    resp_body = response.json()
    assert resp_body["success"] is True
    assert resp_body["data"]["request_id"] == retrieval_id
    assert resp_body["data"]["product_name"] == prod_name
    assert len(resp_body["data"]["feedbacks"]) == 2

def test_get_historical_sentiment_not_found():
    retrieval_id = str(uuid.uuid4())
    history_headers = {
        "Authorization": "Bearer testtoken123",
        "x-request-id": retrieval_id
    }
    # Non-existent ID
    response = client.get("/api/feedback/historical/999", headers=history_headers)
    assert response.status_code == 404
    resp_body = response.json()
    assert resp_body["success"] is False
    assert "does not exist" in resp_body["error_message"]
