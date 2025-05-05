import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.database import Base, engine, get_db

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_read_messages(client):
    response = client.get("/messages/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_message_not_found(client):
    response = client.get("/messages/nonexistent")
    assert response.status_code == 404
