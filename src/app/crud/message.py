from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.message import Message, User, Room

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Message).order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

def get_message(db: Session, event_id: str):
    return db.query(Message).filter(Message.event_id == event_id).first()

def get_room_messages(db: Session, room_id: str, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(Message.room_id == room_id)\
        .order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

def get_user_messages(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(Message).filter(Message.sender_id == user_id)\
        .order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

def search_messages(db: Session, query: str, skip: int = 0, limit: int = 100):
    return db.query(Message)\
        .filter(Message.content.like(f"%{query}%"))\
        .order_by(Message.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_user(db: Session, user_id: str, display_name: str = None):
    db_user = get_user(db, user_id)
    if not db_user:
        db_user = User(user_id=user_id, display_name=display_name)
        db.add(db_user)
        db.commit()
    return db_user

def create_room(db: Session, room_id: str, name: str = None):
    db_room = get_room(db, room_id)
    if not db_room:
        db_room = Room(room_id=room_id, name=name)
        db.add(db_room)
        db.commit()
    return db_room

def create_message(db: Session, event_id: str, room_id: str, sender_id: str, content: str):
    db_message = Message(
        event_id=event_id,
        room_id=room_id,
        sender_id=sender_id,
        content=content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

def get_room(db: Session, room_id: str):
    return db.query(Room).filter(Room.room_id == room_id).first()
