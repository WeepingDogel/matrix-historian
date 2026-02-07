"""Pydantic schemas for media"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MediaBase(BaseModel):
    """Base media schema"""
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class MediaCreate(MediaBase):
    """Schema for creating media"""
    event_id: Optional[str] = None
    room_id: str
    sender_id: str
    minio_key: str
    minio_bucket: str = "matrix-media"


class MediaResponse(MediaBase):
    """Schema for media response"""
    media_id: str
    event_id: Optional[str] = None
    room_id: str
    sender_id: str
    minio_key: str
    minio_bucket: str
    timestamp: datetime
    
    model_config = {"from_attributes": True}


class MediaWithUrl(MediaResponse):
    """Media response with presigned download URL"""
    download_url: str


class MediaListResponse(BaseModel):
    """Response for media list endpoints"""
    media: List[MediaResponse]
    total: int
    has_more: bool
    next_skip: Optional[int] = None


class MediaStatsResponse(BaseModel):
    """Response for media statistics"""
    total_count: int
    total_size: int
    by_type: dict
