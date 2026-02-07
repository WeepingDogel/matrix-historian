"""API routes for media"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
import sys
import io
import logging

sys.path.insert(0, '/app/shared')

from app.db.database import get_db
from app.crud import media as crud_media
from app.schemas.media import (
    MediaResponse,
    MediaWithUrl,
    MediaListResponse,
    MediaStatsResponse
)
from app.storage.minio_client import MediaStorage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MediaListResponse)
def list_media(
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(None, description="Filter by MIME type prefix (e.g., 'image/')"),
    db: Session = Depends(get_db)
):
    """List all media with pagination and optional MIME type filter"""
    total = crud_media.count_media(db, mime_type_filter=mime_type)
    media = crud_media.get_all_media(
        db,
        skip=skip,
        limit=limit,
        mime_type_filter=mime_type
    )
    
    media_responses = [MediaResponse.model_validate(m) for m in media]
    
    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )


@router.get("/stats", response_model=MediaStatsResponse)
def get_media_statistics(db: Session = Depends(get_db)):
    """Get media statistics (total count, total size, breakdown by type)"""
    stats = crud_media.get_media_stats(db)
    return MediaStatsResponse(**stats)


@router.get("/room/{room_id}", response_model=MediaListResponse)
def list_media_by_room(
    room_id: str,
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(None, description="Filter by MIME type prefix (e.g., 'image/')"),
    db: Session = Depends(get_db)
):
    """List media from a specific room"""
    total = crud_media.count_media(db, room_id=room_id, mime_type_filter=mime_type)
    media = crud_media.get_media_by_room(
        db,
        room_id=room_id,
        skip=skip,
        limit=limit,
        mime_type_filter=mime_type
    )
    
    media_responses = [MediaResponse.model_validate(m) for m in media]
    
    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )


@router.get("/user/{user_id}", response_model=MediaListResponse)
def list_media_by_user(
    user_id: str,
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(None, description="Filter by MIME type prefix (e.g., 'image/')"),
    db: Session = Depends(get_db)
):
    """List media sent by a specific user"""
    total = crud_media.count_media(db, user_id=user_id, mime_type_filter=mime_type)
    media = crud_media.get_media_by_user(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        mime_type_filter=mime_type
    )
    
    media_responses = [MediaResponse.model_validate(m) for m in media]
    
    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None
    )


@router.get("/{media_id}", response_model=MediaWithUrl)
def get_media_metadata(media_id: str, db: Session = Depends(get_db)):
    """Get media metadata with presigned download URL"""
    media = crud_media.get_media(db, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    # Generate presigned URL
    try:
        storage = MediaStorage()
        download_url = storage.get_url(media.minio_key, expires=3600)
        
        media_dict = MediaResponse.model_validate(media).model_dump()
        media_dict['download_url'] = download_url
        
        return MediaWithUrl(**media_dict)
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating download URL")


@router.get("/{media_id}/download")
def download_media(
    media_id: str,
    redirect: bool = Query(True, description="Redirect to presigned URL instead of streaming"),
    db: Session = Depends(get_db)
):
    """Download media file (redirect to presigned URL or stream directly)"""
    media = crud_media.get_media(db, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    try:
        storage = MediaStorage()
        
        if redirect:
            # Redirect to presigned URL (more efficient, offloads to MinIO)
            download_url = storage.get_url(media.minio_key, expires=3600)
            return RedirectResponse(url=download_url)
        else:
            # Stream file directly (useful if you need to go through API)
            data = storage.download(media.minio_key)
            return StreamingResponse(
                io.BytesIO(data),
                media_type=media.mime_type or "application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{media.original_filename}"'
                }
            )
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading media")
