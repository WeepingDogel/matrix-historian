from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
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
    skip: int = Query(0, description="Skip N records"), 
    limit: int = Query(100, description="Limit the number of records"), 
    db: Session = Depends(get_db)
):
    total = crud.count_messages(db, room_id=room_id, user_id=user_id)
    messages = crud.get_messages(db, room_id=room_id, user_id=user_id, skip=skip, limit=limit)
    return MessageResponse(
        messages=messages,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )

@router.get("/messages/{event_id}", response_model=Message)
def read_message(event_id: str, db: Session = Depends(get_db)):
    message = crud.get_message(db, event_id=event_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/rooms/{room_id}/messages", response_model=List[Message])
def read_room_messages(room_id: str, skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    messages = crud.get_room_messages(db, room_id=room_id, skip=skip, limit=limit)
    return messages

@router.get("/users/{user_id}/messages", response_model=List[Message])
def read_user_messages(user_id: str, skip: int = Query(0, description="Skip N records"), limit: int = Query(100, description="Limit the number of records"), db: Session = Depends(get_db)):
    messages = crud.get_user_messages(db, user_id=user_id, skip=skip, limit=limit)
    return messages

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
    return MessageResponse(
        messages=messages,
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
