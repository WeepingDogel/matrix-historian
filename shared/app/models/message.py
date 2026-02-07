from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="sender")

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="room")

class Message(Base):
    __tablename__ = "messages"
    event_id = Column(String, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.room_id"))
    sender_id = Column(String, ForeignKey("users.user_id"))
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    room = relationship("Room", back_populates="messages")
    sender = relationship("User", back_populates="messages")

    __table_args__ = (
        Index('ix_messages_room_id', 'room_id'),
        Index('ix_messages_sender_id', 'sender_id'),
        Index('ix_messages_timestamp', 'timestamp')
    )

