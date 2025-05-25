from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class MessageStat(BaseModel):
    date: str
    count: int

class UserActivity(BaseModel):
    user: Dict[str, str]
    message_count: int

class RoomActivity(BaseModel):
    room: Dict[str, str]
    message_count: int

class HourlyActivity(BaseModel):
    hour: int
    count: int

class AnalyticsOverview(BaseModel):
    message_stats: List[MessageStat]
    user_activity: List[UserActivity]
    room_activity: List[RoomActivity]
    hourly_activity: List[HourlyActivity]
    cache_info: Dict[str, Any]
