import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, get_db

@pytest.fixture(scope="session")
def db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    """Create test client"""
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_read_messages(client):
    """Test reading all messages"""
    response = client.get("/api/v1/messages/")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "messages" in response.json()
    assert "total" in response.json()

def test_read_message_not_found(client):
    """Test reading non-existent message"""
    response = client.get("/api/v1/messages/nonexistent")
    assert response.status_code == 404

def test_read_users(client):
    """Test reading users list"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_rooms(client):
    """Test reading rooms list"""
    response = client.get("/api/v1/rooms/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
