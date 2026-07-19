import sys

sys.path.insert(0, "/app/shared")

from datetime import datetime  # noqa: E402
from typing import Any, Dict, List  # noqa: E402

from base_app.crud import message as crud  # noqa: E402
from base_app.db.database import get_db  # noqa: E402
from base_app.schemas.message import (  # noqa: E402
    Message,
    MessageResponse,
    RoomBase,
    UserBase,
)
from cache import (  # noqa: E402
    cache_key,
    get_cached,
    invalidate_by_resource,
    set_cached,
)
from cache_headers import (  # noqa: E402
    CACHE_LONG,
    CACHE_MEDIUM,
    CACHE_SHORT,
    CACHE_VERY_LONG,
    cache_control,
)
from fastapi import APIRouter, Depends, HTTPException, Query  # noqa: E402
from fastapi.responses import JSONResponse, RedirectResponse  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

router = APIRouter()


@router.get("/messages/count")
def get_messages_count(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    query: str = Query(None, description="Search query string"),
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    db: Session = Depends(get_db),
):
    """获取消息总数，支持筛选条件"""
    key = cache_key(
        "count",
        "messages",
        room_id,
        user_id,
        query,
        str(after),
        str(before),
    )
    cached = get_cached("count", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_MEDIUM))

    if query:
        total = crud.count_search_messages(db, query, room_id, user_id, after, before)
    else:
        total = crud.count_messages(db, room_id, user_id, after, before)

    result = {"total": total}
    set_cached("count", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_MEDIUM))


@router.get("/messages/", response_model=MessageResponse)
def read_messages(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    sort: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
):
    query_params: Dict[str, Any] = {}
    if room_id:
        query_params["room_id"] = room_id
    if user_id:
        query_params["user_id"] = user_id
    if after:
        query_params["after"] = after
    if before:
        query_params["before"] = before

    total = crud.count_messages(db, **query_params)
    messages = crud.get_messages(db, skip=skip, limit=limit, sort=sort, **query_params)
    # 转换 ORM model 为 Pydantic schema
    messages_schema = [Message.model_validate(msg) for msg in messages]
    return MessageResponse(
        messages=messages_schema,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None,
    )


@router.get("/messages/{event_id}", response_model=Message)
def read_message(event_id: str, db: Session = Depends(get_db)):
    message = crud.get_message(db, event_id=event_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return Message.model_validate(message)


@router.get("/rooms/{room_id}/messages", response_model=List[Message])
def read_room_messages(
    room_id: str,
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    messages = crud.get_room_messages(
        db, room_id=room_id, after=after, before=before, skip=skip, limit=limit
    )
    return [Message.model_validate(msg) for msg in messages]


@router.get("/users/{user_id}/messages", response_model=List[Message])
def read_user_messages(
    user_id: str,
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    messages = crud.get_user_messages(
        db, user_id=user_id, after=after, before=before, skip=skip, limit=limit
    )
    return [Message.model_validate(msg) for msg in messages]


@router.get("/search/", response_model=MessageResponse)
def search_messages(
    query: str = Query(..., description="Search query string"),
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    sort: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db),
):
    total = crud.count_search_messages(db, query, room_id, user_id, after, before)
    messages = crud.search_messages(
        db, query, room_id, user_id, after, before, skip=skip, limit=limit, sort=sort
    )
    messages_schema = [Message.model_validate(msg) for msg in messages]
    return MessageResponse(
        messages=messages_schema,
        total=total,
        has_more=total > (skip + limit),
        next_skip=skip + limit if total > (skip + limit) else None,
    )


@router.get("/users/", response_model=List[UserBase])
def read_users(
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    """获取用户列表，带缓存"""
    key = cache_key("list", "users", str(skip), str(limit))
    cached = get_cached("list", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_SHORT))

    users = crud.get_users(db, skip=skip, limit=limit)
    result = [UserBase.model_validate(u) for u in users]
    set_cached("list", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_SHORT))


@router.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    """获取用户总数"""
    key = cache_key("count", "users")
    cached = get_cached("count", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_MEDIUM))

    total = crud.count_users(db)
    result = {"total": total}
    set_cached("count", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_MEDIUM))


@router.get("/users/search/", response_model=List[UserBase])
def search_users(
    query: str = Query(..., description="Search query string"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    """搜索用户API"""
    users = crud.search_users(db, query=query, skip=skip, limit=limit)
    return users


@router.get("/users/search/count")
def count_search_users(
    query: str = Query(..., description="Search query string"),
    db: Session = Depends(get_db),
):
    """获取搜索用户结果总数"""
    total = crud.count_search_users(db, query=query)
    return {"total": total}


@router.get("/rooms/", response_model=List[RoomBase])
def read_rooms(
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    """获取房间列表，带缓存"""
    key = cache_key("list", "rooms", str(skip), str(limit))
    cached = get_cached("list", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_SHORT))

    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    result = [RoomBase.model_validate(r) for r in rooms]
    set_cached("list", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_SHORT))


@router.get("/rooms/count")
def count_rooms(db: Session = Depends(get_db)):
    """获取房间总数"""
    key = cache_key("count", "rooms")
    cached = get_cached("count", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_MEDIUM))

    total = crud.count_rooms(db)
    result = {"total": total}
    set_cached("count", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_MEDIUM))


@router.get("/rooms/search/", response_model=List[RoomBase])
def search_rooms(
    query: str = Query(..., description="Search query string"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    """搜索房间API"""
    rooms = crud.search_rooms(db, query=query, skip=skip, limit=limit)
    return rooms


@router.get("/rooms/search/count")
def count_search_rooms(
    query: str = Query(..., description="Search query string"),
    db: Session = Depends(get_db),
):
    """获取搜索房间结果总数"""
    total = crud.count_search_rooms(db, query=query)
    return {"total": total}


@router.get("/health")
def health_check():
    """健康检查端点，浏览器短期缓存"""
    result = {"status": "healthy"}
    return JSONResponse(content=result, headers=cache_control(120))


@router.get("/analytics/message-stats")
def get_message_statistics(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """获取消息统计数据，带缓存"""
    key = cache_key("analytics", "message_stats", str(days))
    cached = get_cached("analytics", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_LONG))

    stats = crud.get_message_stats(db, days)
    result = {"stats": [{"date": str(row.date), "count": row.count} for row in stats]}
    set_cached("analytics", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_LONG))


@router.get("/analytics/user-activity")
def get_user_activity(
    limit: int = Query(10, description="Number of users to return"),
    db: Session = Depends(get_db),
):
    """获取用户活跃度统计，带缓存"""
    key = cache_key("analytics", "user_activity", str(limit))
    cached = get_cached("analytics", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_LONG))

    activity = crud.get_user_activity(db, limit)
    result = {
        "users": [
            {
                "user": user.user_id,
                "display_name": user.display_name,
                "message_count": count,
            }
            for user, count in activity
        ]
    }
    set_cached("analytics", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_LONG))


@router.get("/analytics/room-activity")
def get_room_activity(
    limit: int = Query(10, description="Number of rooms to return"),
    db: Session = Depends(get_db),
):
    """获取房间活跃度统计，带缓存"""
    key = cache_key("analytics", "room_activity", str(limit))
    cached = get_cached("analytics", key)
    if cached is not None:
        return JSONResponse(content=cached, headers=cache_control(CACHE_LONG))

    activity = crud.get_room_activity(db, limit)
    result = {
        "rooms": [
            {"room": room.room_id, "name": room.name, "message_count": count}
            for room, count in activity
        ]
    }
    set_cached("analytics", key, result)
    return JSONResponse(content=result, headers=cache_control(CACHE_LONG))


# ─── Cache Invalidation Endpoints ─────────────────────────────────────
# These endpoints are called by the bot service after write operations.

@router.post("/cache/invalidate")
def invalidate_cache(
    resource: str = Query(
        ...,
        description=(
            "Resource type to invalidate: "
            "message, room, user, media, analytics, all"
        ),
    )
):
    """Invalidate API cache for a given resource type. Called by bot after writes."""
    invalidate_by_resource(resource)
    return {"status": "ok", "invalidated": resource}


@router.get("/avatars/{avatar_type}/{entity_id}")
def get_avatar(
    avatar_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
):
    """Get avatar image for a user or room，长期浏览器缓存"""
    from base_app.storage.minio_client import MediaStorage

    if avatar_type not in ("users", "rooms"):
        raise HTTPException(status_code=400, detail="Invalid avatar type")

    # Check if entity has avatar
    if avatar_type == "users":
        entity = crud.get_user(db, entity_id)
    else:
        entity = crud.get_room(db, entity_id)

    if not entity or not entity.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar not found")

    try:
        storage = MediaStorage()
        url = storage.get_url(entity.avatar_url, expires=3600)

        # Avatars rarely change - long browser cache
        return RedirectResponse(url=url, headers=cache_control(CACHE_VERY_LONG))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching avatar: {str(e)}"
        ) from e
