# message.py
# This module defines Pydantic models for messages in a chat application.


from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str


class UserBase(BaseModel):
    user_id: str
    display_name: Optional[str] = None

    model_config = {"from_attributes": True}


class RoomBase(BaseModel):
    room_id: str
    name: Optional[str] = None

    model_config = {"from_attributes": True}


class MediaAttachment(BaseModel):
    media_id: str
    mime_type: Optional[str] = None
    original_filename: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

    model_config = {"from_attributes": True}


class Message(MessageBase):
    event_id: str
    room_id: str
    sender_id: str
    timestamp: datetime
    room: RoomBase
    sender: UserBase
    media: List[MediaAttachment] = []

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    messages: List[Message]
    total: int
    has_more: bool
    next_skip: Optional[int] = None
