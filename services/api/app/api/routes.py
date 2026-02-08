from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import sys
sys.path.insert(0, '/app/shared')

from app.db.database import get_db
from app.crud import message as crud
from app.schemas.message import Message, UserBase, RoomBase, MessageResponse

router = APIRouter()

@router.get("/messages/count")
def get_messages_count(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    query: str = Query(None, description="Search query string"),
    db: Session = Depends(get_db)
):
    """获取消息总数，支持筛选条件"""
    if query:
        total = crud.count_search_messages(db, query, room_id, user_id)
    else:
        total = crud.count_messages(db, room_id, user_id)
    return {"total": total}

@router.get("/messages/", response_model=MessageResponse)
def read_messages(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    after: datetime = Query(None, description="Filter messages after this time"),
    skip: int = Query(0, description="Skip N records"), 
    limit: int = Query(100, description="Limit the number of records"), 
    db: Session = Depends(get_db)
):
    query_params = {}
    if room_id:
        query_params["room_id"] = room_id
    if user_id:
        query_params["user_id"] = user_id
    if after:
        query_params["after"] = after
        
    total = crud.count_messages(db, **query_params)
    messages = crud.get_messages(db, skip=skip, limit=limit, **query_params)
    # 转换 ORM model 为 Pydantic schema
    messages_schema = [Message.model_validate(msg) for msg in messages]
    return MessageResponse(
        messages=messages_schema,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )

@router.get("/messages/{event_id}", response_model=Message)
def read_message(event_id: str, db: Session = Depends(get_db)):
    message = crud.get_message(db, event_id=event_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return Message.model_validate(message)

@router.get("/rooms/{room_id}/messages", response_model=List[Message])
def read_room_messages(room_id: str, skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    messages = crud.get_room_messages(db, room_id=room_id, skip=skip, limit=limit)
    return [Message.model_validate(msg) for msg in messages]

@router.get("/users/{user_id}/messages", response_model=List[Message])
def read_user_messages(user_id: str, skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    messages = crud.get_user_messages(db, user_id=user_id, skip=skip, limit=limit)
    return [Message.model_validate(msg) for msg in messages]

@router.get("/search/", response_model=MessageResponse)
def search_messages(
    query: str = Query(..., description="Search query string"),
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db)
):
    total = crud.count_search_messages(db, query, room_id, user_id)
    messages = crud.search_messages(db, query, room_id, user_id, skip=skip, limit=limit)
    messages_schema = [Message.model_validate(msg) for msg in messages]
    return MessageResponse(
        messages=messages_schema,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )

@router.get("/users/", response_model=List[UserBase])
def read_users(skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/search/", response_model=List[UserBase])
def search_users(
    query: str = Query(..., description="Search query string"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db)
):
    """搜索用户API"""
    users = crud.search_users(db, query=query, skip=skip, limit=limit)
    return users

@router.get("/rooms/", response_model=List[RoomBase])
def read_rooms(skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.get("/analytics/message-stats")
def get_message_statistics(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """获取消息统计数据"""
    stats = crud.get_message_stats(db, days)
    return {
        "stats": [
            {"date": str(row.date), "count": row.count}
            for row in stats
        ]
    }

@router.get("/analytics/user-activity")
def get_user_activity(
    limit: int = Query(10, description="Number of users to return"),
    db: Session = Depends(get_db)
):
    """获取用户活跃度统计"""
    activity = crud.get_user_activity(db, limit)
    return {
        "users": [{
            "user": user.user_id,
            "display_name": user.display_name,
            "message_count": count
        } for user, count in activity]
    }

@router.get("/analytics/room-activity")
def get_room_activity(
    limit: int = Query(10, description="Number of rooms to return"),
    db: Session = Depends(get_db)
):
    """获取房间活跃度统计"""
    activity = crud.get_room_activity(db, limit)
    return {
        "rooms": [{
            "room": room.room_id,
            "name": room.name,
            "message_count": count
        } for room, count in activity]
    }
