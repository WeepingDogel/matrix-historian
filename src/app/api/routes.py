from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud import message as crud
from app.schemas.message import Message, UserBase, RoomBase

router = APIRouter()

@router.get("/messages/", response_model=List[Message])
def read_messages(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    messages = crud.get_messages(db, room_id=room_id, user_id=user_id, skip=skip, limit=limit)
    return messages

@router.get("/messages/{event_id}", response_model=Message)
def read_message(event_id: str, db: Session = Depends(get_db)):
    message = crud.get_message(db, event_id=event_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/rooms/{room_id}/messages", response_model=List[Message])
def read_room_messages(room_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_room_messages(db, room_id=room_id, skip=skip, limit=limit)
    return messages

@router.get("/users/{user_id}/messages", response_model=List[Message])
def read_user_messages(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_user_messages(db, user_id=user_id, skip=skip, limit=limit)
    return messages

@router.get("/search/", response_model=List[Message])
def search_messages(
    query: str = Query(..., description="Search query string"),
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.search_messages(db, query, room_id, user_id, skip=skip, limit=limit)

@router.get("/users/", response_model=List[UserBase])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/rooms/", response_model=List[RoomBase])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms
