"""CRUD operations for media"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.message import Media
from typing import Optional, List
from datetime import datetime
import uuid


def create_media(
    db: Session,
    event_id: Optional[str],
    room_id: str,
    sender_id: str,
    minio_key: str,
    original_filename: Optional[str] = None,
    mime_type: Optional[str] = None,
    size: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    minio_bucket: str = "matrix-media"
) -> Media:
    """
    Create a new media record
    
    Args:
        db: Database session
        event_id: Matrix event ID (nullable for standalone media)
        room_id: Room ID where media was sent
        sender_id: User ID who sent the media
        minio_key: Object key in MinIO
        original_filename: Original filename
        mime_type: MIME type
        size: File size in bytes
        width: Image width (for images)
        height: Image height (for images)
        minio_bucket: MinIO bucket name
        
    Returns:
        Created Media object
    """
    media_id = str(uuid.uuid4())
    
    db_media = Media(
        media_id=media_id,
        event_id=event_id,
        room_id=room_id,
        sender_id=sender_id,
        minio_key=minio_key,
        minio_bucket=minio_bucket,
        original_filename=original_filename,
        mime_type=mime_type,
        size=size,
        width=width,
        height=height,
        timestamp=datetime.utcnow()
    )
    
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def get_media(db: Session, media_id: str) -> Optional[Media]:
    """Get a media record by ID"""
    return db.query(Media).filter(Media.media_id == media_id).first()


def get_media_by_event(db: Session, event_id: str) -> List[Media]:
    """Get all media associated with an event"""
    return db.query(Media).filter(Media.event_id == event_id).all()


def get_media_by_room(
    db: Session,
    room_id: str,
    skip: int = 0,
    limit: int = 100,
    mime_type_filter: Optional[str] = None
) -> List[Media]:
    """
    Get media from a specific room
    
    Args:
        db: Database session
        room_id: Room ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        mime_type_filter: Filter by MIME type prefix (e.g., "image/")
        
    Returns:
        List of Media objects
    """
    query = db.query(Media).filter(Media.room_id == room_id)
    
    if mime_type_filter:
        query = query.filter(Media.mime_type.like(f"{mime_type_filter}%"))
    
    return query.order_by(Media.timestamp.desc()).offset(skip).limit(limit).all()


def get_media_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    mime_type_filter: Optional[str] = None
) -> List[Media]:
    """
    Get media sent by a specific user
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        mime_type_filter: Filter by MIME type prefix (e.g., "image/")
        
    Returns:
        List of Media objects
    """
    query = db.query(Media).filter(Media.sender_id == user_id)
    
    if mime_type_filter:
        query = query.filter(Media.mime_type.like(f"{mime_type_filter}%"))
    
    return query.order_by(Media.timestamp.desc()).offset(skip).limit(limit).all()


def get_all_media(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    mime_type_filter: Optional[str] = None,
    after: Optional[datetime] = None
) -> List[Media]:
    """
    Get all media with optional filters
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        mime_type_filter: Filter by MIME type prefix (e.g., "image/")
        after: Filter media after this timestamp
        
    Returns:
        List of Media objects
    """
    query = db.query(Media)
    
    if mime_type_filter:
        query = query.filter(Media.mime_type.like(f"{mime_type_filter}%"))
    
    if after:
        query = query.filter(Media.timestamp >= after)
    
    return query.order_by(Media.timestamp.desc()).offset(skip).limit(limit).all()


def count_media(
    db: Session,
    room_id: Optional[str] = None,
    user_id: Optional[str] = None,
    mime_type_filter: Optional[str] = None,
    after: Optional[datetime] = None
) -> int:
    """
    Count media with optional filters
    
    Args:
        db: Database session
        room_id: Filter by room
        user_id: Filter by user
        mime_type_filter: Filter by MIME type prefix
        after: Filter media after this timestamp
        
    Returns:
        Total count of media matching filters
    """
    query = db.query(func.count(Media.media_id))
    
    if room_id:
        query = query.filter(Media.room_id == room_id)
    
    if user_id:
        query = query.filter(Media.sender_id == user_id)
    
    if mime_type_filter:
        query = query.filter(Media.mime_type.like(f"{mime_type_filter}%"))
    
    if after:
        query = query.filter(Media.timestamp >= after)
    
    return query.scalar()


def get_media_stats(db: Session) -> dict:
    """
    Get media statistics
    
    Returns:
        Dictionary with statistics:
        - total_count: Total number of media files
        - total_size: Total size in bytes
        - by_type: Count and size by MIME type prefix
    """
    total_count = db.query(func.count(Media.media_id)).scalar()
    total_size = db.query(func.sum(Media.size)).scalar() or 0
    
    # Get stats by type (image, video, audio, file)
    type_stats = db.query(
        Media.mime_type,
        func.count(Media.media_id).label('count'),
        func.sum(Media.size).label('total_size')
    ).group_by(Media.mime_type).all()
    
    # Group by prefix (image/, video/, audio/, etc.)
    by_type = {}
    for mime_type, count, size in type_stats:
        if mime_type:
            prefix = mime_type.split('/')[0]
            if prefix not in by_type:
                by_type[prefix] = {'count': 0, 'total_size': 0}
            by_type[prefix]['count'] += count
            by_type[prefix]['total_size'] += (size or 0)
    
    return {
        'total_count': total_count,
        'total_size': total_size,
        'by_type': by_type
    }


def delete_media(db: Session, media_id: str) -> bool:
    """
    Delete a media record
    
    Args:
        db: Database session
        media_id: Media ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_media = get_media(db, media_id)
    if db_media:
        db.delete(db_media)
        db.commit()
        return True
    return False
