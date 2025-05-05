from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.crud import message as crud
from app.schemas.message import Message

router = APIRouter()

@router.get("/messages/", response_model=List[Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
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

@router.get("/search/")
def search_messages(
    query: str = Query(..., description="Search query string"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.search_messages(db, query, skip=skip, limit=limit)
