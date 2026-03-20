import sys

sys.path.insert(
    0, "/app/shared"
)  # Still correct, base_app is under shared  # Still correct, base_app is under shared

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
from fastapi import APIRouter, Depends, HTTPException, Query  # noqa: E402
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
    if query:
        total = crud.count_search_messages(db, query, room_id, user_id, after, before)
    else:
        total = crud.count_messages(db, room_id, user_id, after, before)
    return {"total": total}


@router.get("/messages/", response_model=MessageResponse)
def read_messages(
    room_id: str = Query(None, description="Filter by room ID"),
    user_id: str = Query(None, description="Filter by user ID"),
    after: datetime = Query(None, description="Filter messages after this time"),
    before: datetime = Query(None, description="Filter messages before this time"),
    skip: int = Query(0, description="Skip N records"),
    limit: int = Query(100, description="Limit the number of records"),
    db: Session = Depends(get_db),
):
    query_params: Dict[str, Any] = {}
    if room_id:
        query_params["room_id"] = room_id
    if user_id:
        query_params["user_id"] = user_id
    if after:
        query_params["after"] = after.isoformat() if after else None
    if before:
        query_params["before"] = before.isoformat() if before else None

    total = crud.count_messages(db, **query_params)
    messages = crud.get_messages(db, skip=skip, limit=limit, **query_params)
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
    db: Session = Depends(get_db),
):
    total = crud.count_search_messages(db, query, room_id, user_id, after, before)
    messages = crud.search_messages(
        db, query, room_id, user_id, after, before, skip=skip, limit=limit
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
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/count")
def count_users(db: Session = Depends(get_db)):
    """获取用户总数"""
    total = crud.count_users(db)
    return {"total": total}


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
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms


@router.get("/rooms/count")
def count_rooms(db: Session = Depends(get_db)):
    """获取房间总数"""
    total = crud.count_rooms(db)
    return {"total": total}


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
    return {"status": "healthy"}


@router.get("/analytics/message-stats")
def get_message_statistics(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db),
):
    """获取消息统计数据"""
    stats = crud.get_message_stats(db, days)
    return {"stats": [{"date": str(row.date), "count": row.count} for row in stats]}


@router.get("/analytics/user-activity")
def get_user_activity(
    limit: int = Query(10, description="Number of users to return"),
    db: Session = Depends(get_db),
):
    """获取用户活跃度统计"""
    activity = crud.get_user_activity(db, limit)
    return {
        "users": [
            {
                "user": user.user_id,
                "display_name": user.display_name,
                "message_count": count,
            }
            for user, count in activity
        ]
    }


@router.get("/analytics/room-activity")
def get_room_activity(
    limit: int = Query(10, description="Number of rooms to return"),
    db: Session = Depends(get_db),
):
    """获取房间活跃度统计"""
    activity = crud.get_room_activity(db, limit)
    return {
        "rooms": [
            {"room": room.room_id, "name": room.name, "message_count": count}
            for room, count in activity
        ]
    }


@router.get("/avatars/{avatar_type}/{entity_id}")
def get_avatar(
    avatar_type: str,
    entity_id: str,
    db: Session = Depends(get_db),
):
    """Get avatar image for a user or room"""

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
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching avatar: {str(e)}")
