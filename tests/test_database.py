"""Tests for database operations."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.app.db.database import Base
from shared.app.models.message import Message


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_database_connection(test_engine):
    """Test database connection."""
    with test_engine.connect() as conn:
        result = conn.execute("SELECT 1")
        assert result.scalar() == 1


def test_message_crud_operations(test_session):
    """Test CRUD operations for Message model."""
    from datetime import datetime

    # Create
    message = Message(
        room_id="!test:example.com",
        event_id="$test123",
        sender="@user:example.com",
        content="Test message",
        timestamp=datetime.now(),
        message_type="m.text",
    )

    test_session.add(message)
    test_session.commit()
    test_session.refresh(message)

    assert message.id is not None
    assert message.room_id == "!test:example.com"

    # Read
    retrieved = (
        test_session.query(Message).filter_by(room_id="!test:example.com").first()
    )
    assert retrieved is not None
    assert retrieved.content == "Test message"

    # Update
    retrieved.content = "Updated message"
    test_session.commit()
    test_session.refresh(retrieved)
    assert retrieved.content == "Updated message"

    # Delete
    test_session.delete(retrieved)
    test_session.commit()

    deleted = test_session.query(Message).filter_by(id=message.id).first()
    assert deleted is None


def test_database_constraints(test_session):
    """Test database constraints."""
    from datetime import datetime

    from sqlalchemy.exc import IntegrityError

    # Test required fields
    with pytest.raises(IntegrityError):
        message = Message(
            # Missing required fields
            room_id=None,
            event_id=None,
            sender=None,
            content="Test",
            timestamp=datetime.now(),
            message_type="m.text",
        )
        test_session.add(message)
        test_session.commit()
