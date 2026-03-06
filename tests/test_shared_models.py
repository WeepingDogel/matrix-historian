"""Tests for shared models and schemas."""

from datetime import datetime

import pytest

from shared.base_app.models.message import Message as MessageModel
from shared.base_app.schemas.message import (
    Message,
    MessageBase,
    MessageResponse,
    RoomBase,
    UserBase,
)


def test_message_base_schema():
    """Test MessageBase schema."""
    msg = MessageBase(content="Hello, world!")
    assert msg.content == "Hello, world!"  # nosec


def test_room_base_schema():
    """Test RoomBase schema."""
    room = RoomBase(room_id="!test:example.com", name="Test Room")
    assert room.room_id == "!test:example.com"  # nosec
    assert room.name == "Test Room"  # nosec


def test_user_base_schema():
    """Test UserBase schema."""
    user = UserBase(user_id="@user:example.com", display_name="Test User")
    assert user.user_id == "@user:example.com"  # nosec
    assert user.display_name == "Test User"  # nosec


def test_message_schema():
    """Test Message schema."""
    data = {
        "content": "Hello, world!",
        "event_id": "$test123",
        "room_id": "!test:example.com",
        "sender_id": "@user:example.com",
        "timestamp": datetime.now(),
        "room": {"room_id": "!test:example.com", "name": "Test Room"},
        "sender": {"user_id": "@user:example.com", "display_name": "Test User"},
    }

    message = Message(**data)
    assert message.event_id == "$test123"  # nosec
    assert message.room_id == "!test:example.com"  # nosec
    assert message.sender_id == "@user:example.com"  # nosec
    assert message.content == "Hello, world!"  # nosec


def test_message_response_schema():
    """Test MessageResponse schema."""
    data = {
        "messages": [],
        "total": 0,
        "has_more": False,
        "next_skip": None,
    }

    response = MessageResponse(**data)
    assert response.total == 0  # nosec
    assert response.has_more is False  # nosec
    assert response.messages == []  # nosec


def test_message_schema_validation():
    """Test schema validation with missing required fields."""
    with pytest.raises(Exception):
        Message(
            content="Test",
            # Missing required fields: event_id, room_id, sender_id, timestamp, room, sender
        )
