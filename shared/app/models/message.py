from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="sender")
    media = relationship("Media", back_populates="sender")

class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    messages = relationship("Message", back_populates="room")
    media = relationship("Media", back_populates="room")

class Message(Base):
    __tablename__ = "messages"
    event_id = Column(String, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("rooms.room_id"))
    sender_id = Column(String, ForeignKey("users.user_id"))
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    room = relationship("Room", back_populates="messages")
    sender = relationship("User", back_populates="messages")
    media = relationship("Media", back_populates="message")

    __table_args__ = (
        Index('ix_messages_room_id', 'room_id'),
        Index('ix_messages_sender_id', 'sender_id'),
        Index('ix_messages_timestamp', 'timestamp')
    )

class Media(Base):
    __tablename__ = "media"
    media_id = Column(String, primary_key=True, index=True)  # UUID
    event_id = Column(String, ForeignKey("messages.event_id"), nullable=True)
    room_id = Column(String, ForeignKey("rooms.room_id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    minio_key = Column(String, nullable=False)  # Object key in MinIO
    minio_bucket = Column(String, default="matrix-media")
    original_filename = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    size = Column(Integer, nullable=True)  # bytes
    width = Column(Integer, nullable=True)  # for images
    height = Column(Integer, nullable=True)  # for images
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    room = relationship("Room", back_populates="media")
    sender = relationship("User", back_populates="media")
    message = relationship("Message", back_populates="media")

    __table_args__ = (
        Index('ix_media_room_id', 'room_id'),
        Index('ix_media_sender_id', 'sender_id'),
        Index('ix_media_timestamp', 'timestamp'),
        Index('ix_media_event_id', 'event_id'),
        Index('ix_media_mime_type', 'mime_type')
    )

