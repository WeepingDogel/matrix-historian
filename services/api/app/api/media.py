"""API routes for media"""

import io
import logging
import sys

sys.path.insert(
    0, "/app/shared"
)  # Still correct, base_app is under shared  # Still correct, base_app is under shared

from base_app.crud import media as crud_media  # noqa: E402
from base_app.db.database import get_db  # noqa: E402
from base_app.schemas.media import (  # noqa: E402
    MediaListResponse,
    MediaResponse,
    MediaStatsResponse,
    MediaWithUrl,
)
from base_app.storage.minio_client import MediaStorage  # noqa: E402
from cache import cache_key, get_cached, set_cached  # noqa: E402
from cache_headers import CACHE_MEDIUM, CACHE_SHORT, cache_control  # noqa: E402
from fastapi import APIRouter, Depends, HTTPException, Query  # noqa: E402
from fastapi.responses import (  # noqa: E402
    JSONResponse,
    RedirectResponse,
    StreamingResponse,
)
from sqlalchemy.orm import Session  # noqa: E402

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=MediaListResponse)
def list_media(
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(
        None, description="Filter by MIME type prefix (e.g., 'image/')"
    ),
    db: Session = Depends(get_db),
):
    """List all media with pagination and optional MIME type filter"""
    total = crud_media.count_media(db, mime_type_filter=mime_type)
    media = crud_media.get_all_media(
        db, skip=skip, limit=limit, mime_type_filter=mime_type
    )

    media_responses = [MediaResponse.model_validate(m) for m in media]

    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None,
    )


@router.get("/stats", response_model=MediaStatsResponse)
def get_media_statistics(db: Session = Depends(get_db)):
    """Get media statistics (total count, total size,
    breakdown by type)，带缓存"""
    key = cache_key("media", "stats")
    cached = get_cached("media", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_MEDIUM))

    stats = crud_media.get_media_stats(db)
    result = MediaStatsResponse(**stats).model_dump()
    set_cached("media", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_MEDIUM))


@router.get("/room/{room_id}", response_model=MediaListResponse)
def list_media_by_room(
    room_id: str,
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(
        None, description="Filter by MIME type prefix (e.g., 'image/')"
    ),
    db: Session = Depends(get_db),
):
    """List media from a specific room"""
    total = crud_media.count_media(db, room_id=room_id, mime_type_filter=mime_type)
    media = crud_media.get_media_by_room(
        db, room_id=room_id, skip=skip, limit=limit, mime_type_filter=mime_type
    )

    media_responses = [MediaResponse.model_validate(m) for m in media]

    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None,
    )


@router.get("/user/{user_id}", response_model=MediaListResponse)
def list_media_by_user(
    user_id: str,
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    mime_type: str = Query(
        None, description="Filter by MIME type prefix (e.g., 'image/')"
    ),
    db: Session = Depends(get_db),
):
    """List media sent by a specific user"""
    total = crud_media.count_media(db, user_id=user_id, mime_type_filter=mime_type)
    media = crud_media.get_media_by_user(
        db, user_id=user_id, skip=skip, limit=limit, mime_type_filter=mime_type
    )

    media_responses = [MediaResponse.model_validate(m) for m in media]

    return MediaListResponse(
        media=media_responses,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None,
    )


@router.get("/{media_id}", response_model=MediaWithUrl)
def get_media_metadata(media_id: str, db: Session = Depends(get_db)):
    """Get media metadata with presigned download URL，短期缓存"""
    key = cache_key("media", "metadata", media_id)
    cached = get_cached("media", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_SHORT))

    media = crud_media.get_media(db, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    # Generate presigned URL
    try:
        storage = MediaStorage()
        download_url = storage.get_url(media.minio_key, expires=3600)

        media_dict = MediaResponse.model_validate(media).model_dump()
        media_dict["download_url"] = download_url

        result = MediaWithUrl(**media_dict).model_dump()
        set_cached("media", key, result)
        return JSONResponse(content=result, headers=cache_control(CACHE_SHORT))
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error generating download URL"
        ) from e


@router.get("/{media_id}/download")
def download_media(
    media_id: str,
    redirect: bool = Query(
        True, description="Redirect to presigned URL instead of streaming"
    ),
    db: Session = Depends(get_db),
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
                    "Content-Disposition": (
                        f'attachment; filename="{media.original_filename}"'
                    )
                },
            )
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading media") from e

