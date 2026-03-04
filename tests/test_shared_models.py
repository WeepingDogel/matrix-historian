"""Tests for shared models and schemas."""

from datetime import datetime

import pytest

from shared.app.models.message import Message
from shared.app.schemas.message import MessageCreate, MessageResponse


def test_message_model():
    """Test Message model creation."""
    message = Message(
        id=1,
        room_id="!test:example.com",
        event_id="$test123",
        sender="@user:example.com",
        content="Hello, world!",
        timestamp=datetime.now(),
        message_type="m.text",
        media_url="https://example.com/image.jpg",
        media_type="image/jpeg",
        media_size=1024,
        media_width=800,
        media_height=600,
    )

    assert message.room_id == "!test:example.com"  # nosec
    assert message.sender == "@user:example.com"  # nosec
    assert message.content == "Hello, world!"  # nosec
    assert message.message_type == "m.text"  # nosec


def test_message_create_schema():
    """Test MessageCreate schema validation."""
    data = {
        "room_id": "!test:example.com",
        "event_id": "$test123",
        "sender": "@user:example.com",
        "content": "Hello, world!",
        "timestamp": "2024-01-01T12:00:00Z",
        "message_type": "m.text",
    }

    message_create = MessageCreate(**data)
    assert message_create.room_id == data["room_id"]  # nosec
    assert message_create.sender == data["sender"]  # nosec


def test_message_response_schema():
    """Test MessageResponse schema."""
    data = {
        "id": 1,
        "room_id": "!test:example.com",
        "event_id": "$test123",
        "sender": "@user:example.com",
        "content": "Hello, world!",
        "timestamp": datetime.now(),
        "message_type": "m.text",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    message_response = MessageResponse(**data)
    assert message_response.id == 1  # nosec
    assert message_response.room_id == "!test:example.com"  # nosec


def test_message_schema_validation():
    """Test schema validation with invalid data."""
    with pytest.raises(ValueError):
        MessageCreate(
            room_id="",  # Empty room_id should fail
            event_id="$test123",
            sender="@user:example.com",
            content="Test",
            timestamp="2024-01-01T12:00:00Z",
            message_type="m.text",
        )
