from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageBase(BaseModel):
    content: str
    
class UserBase(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    room_id: str
    name: Optional[str] = None
    
    class Config:
        from_attributes = True

class Message(MessageBase):
    event_id: str
    room_id: str
    sender_id: str
    timestamp: datetime
    room: RoomBase
    sender: UserBase
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    messages: List[Message]
    total: int
    has_more: bool
    next_skip: Optional[int] = None
