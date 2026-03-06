"""Tests for database operations."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from shared.base_app.db.database import Base
from shared.base_app.models.message import Message, Room, User


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_database_connection(test_engine):
    """Test database connection."""
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1  # nosec


def test_message_crud_operations(test_session):
    """Test CRUD operations for Message model."""
    # Create required Room and User first
    room = Room(room_id="!test:example.com", name="Test Room")
    user = User(user_id="@user:example.com", display_name="Test User")
    test_session.add_all([room, user])
    test_session.commit()

    # Create message
    message = Message(
        event_id="$test123",
        room_id="!test:example.com",
        sender_id="@user:example.com",
        content="Test message",
    )
    test_session.add(message)
    test_session.commit()

    assert message.event_id == "$test123"  # nosec
    assert message.room_id == "!test:example.com"  # nosec

    # Read
    retrieved = (
        test_session.query(Message)
        .filter_by(room_id="!test:example.com")
        .first()
    )
    assert retrieved is not None  # nosec
    assert retrieved.content == "Test message"  # nosec

    # Update
    retrieved.content = "Updated message"
    test_session.commit()
    test_session.refresh(retrieved)
    assert retrieved.content == "Updated message"  # nosec

    # Delete
    test_session.delete(retrieved)
    test_session.commit()

    deleted = (
        test_session.query(Message)
        .filter_by(event_id="$test123")
        .first()
    )
    assert deleted is None  # nosec


def test_database_relationships(test_session):
    """Test model relationships."""
    room = Room(room_id="!test:example.com", name="Test Room")
    user = User(user_id="@user:example.com", display_name="Test User")
    test_session.add_all([room, user])
    test_session.commit()

    message = Message(
        event_id="$test456",
        room_id="!test:example.com",
        sender_id="@user:example.com",
        content="Relationship test",
    )
    test_session.add(message)
    test_session.commit()

    assert message.room.name == "Test Room"  # nosec
    assert message.sender.display_name == "Test User"  # nosec
