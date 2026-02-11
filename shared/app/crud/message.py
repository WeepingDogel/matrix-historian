from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.message import Message, User, Room
from sqlalchemy import extract
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Tuple, Optional

def get_messages(db: Session, room_id: Optional[str] = None, user_id: Optional[str] = None, 
                after: Optional[datetime] = None, before: Optional[datetime] = None, 
                skip: int = 0, limit: int = 100):
    query = db.query(Message)
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    if user_id:
        query = query.filter(Message.sender_id == user_id)
    if after:
        query = query.filter(Message.timestamp >= after)
    if before:
        query = query.filter(Message.timestamp <= before)
        
    return query.order_by(Message.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_message(db: Session, event_id: str):
    return db.query(Message).filter(Message.event_id == event_id).first()

def get_room_messages(db: Session, room_id: str, after: Optional[datetime] = None, 
                     before: Optional[datetime] = None, skip: int = 0, limit: int = 100):
    query = db.query(Message).filter(Message.room_id == room_id)
    
    if after:
        query = query.filter(Message.timestamp >= after)
    if before:
        query = query.filter(Message.timestamp <= before)
        
    return query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

def get_user_messages(db: Session, user_id: str, after: Optional[datetime] = None, 
                     before: Optional[datetime] = None, skip: int = 0, limit: int = 100):
    query = db.query(Message).filter(Message.sender_id == user_id)
    
    if after:
        query = query.filter(Message.timestamp >= after)
    if before:
        query = query.filter(Message.timestamp <= before)
        
    return query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

def search_messages(db: Session, query: str, room_id: Optional[str] = None, user_id: Optional[str] = None, 
                   after: Optional[datetime] = None, before: Optional[datetime] = None, 
                   skip: int = 0, limit: int = 100):
    search_query = db.query(Message)\
        .filter(Message.content.like(f"%{query}%"))
    
    if room_id:
        search_query = search_query.filter(Message.room_id == room_id)
    if user_id:
        search_query = search_query.filter(Message.sender_id == user_id)
    if after:
        search_query = search_query.filter(Message.timestamp >= after)
    if before:
        search_query = search_query.filter(Message.timestamp <= before)
        
    return search_query.order_by(Message.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def count_messages(db: Session, room_id: Optional[str] = None, user_id: Optional[str] = None, 
                  after: Optional[datetime] = None, before: Optional[datetime] = None):
    query = db.query(func.count(Message.event_id))
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    if user_id:
        query = query.filter(Message.sender_id == user_id)
    if after:
        query = query.filter(Message.timestamp >= after)
    if before:
        query = query.filter(Message.timestamp <= before)
        
    return query.scalar()

def count_search_messages(db: Session, search_query: str, room_id: Optional[str] = None, user_id: Optional[str] = None, 
                         after: Optional[datetime] = None, before: Optional[datetime] = None):
    """计算搜索结果的消息总数"""
    query = db.query(func.count(Message.event_id)).filter(
        Message.content.ilike(f"%{search_query}%")
    )
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    if user_id:
        query = query.filter(Message.sender_id == user_id)
    if after:
        query = query.filter(Message.timestamp >= after)
    if before:
        query = query.filter(Message.timestamp <= before)
        
    return query.scalar()

def count_users(db: Session):
    """计算用户总数"""
    return db.query(func.count(User.user_id)).scalar()

def count_search_users(db: Session, query: str):
    """计算搜索用户结果总数"""
    return db.query(func.count(User.user_id)).filter(
        User.display_name.ilike(f"%{query}%") | 
        User.user_id.ilike(f"%{query}%")
    ).scalar()

def create_user(db: Session, user_id: str, display_name: Optional[str] = None):
    db_user = get_user(db, user_id)
    if not db_user:
        db_user = User(user_id=user_id, display_name=display_name)
        db.add(db_user)
        db.commit()
    return db_user

def create_room(db: Session, room_id: str, name: Optional[str] = None):
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

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Room).offset(skip).limit(limit).all()

def search_users(db: Session, query: str, skip: int = 0, limit: int = 100):
    """搜索用户"""
    return db.query(User).filter(
        User.display_name.ilike(f"%{query}%") | 
        User.user_id.ilike(f"%{query}%")
    ).offset(skip).limit(limit).all()

def get_message_stats(db: Session, days: int = 7):
    """获取消息统计数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    daily_stats = db.query(
        func.date_trunc('day', Message.timestamp).label('date'),
        func.count(Message.event_id).label('count')
    ).filter(
        Message.timestamp >= start_date
    ).group_by(
        func.date_trunc('day', Message.timestamp)
    ).order_by(
        func.date_trunc('day', Message.timestamp)
    ).all()
    
    return daily_stats

def get_user_activity(db: Session, limit: int = 10):
    """获取最活跃用户统计"""
    return db.query(
        User,
        func.count(Message.event_id).label('message_count')
    ).join(Message).group_by(User).order_by(
        func.count(Message.event_id).desc()
    ).limit(limit).all()

def get_room_activity(db: Session, limit: int = 10):
    """获取最活跃房间统计"""
    return db.query(
        Room,
        func.count(Message.event_id).label('message_count')
    ).join(Message).group_by(Room).order_by(
        func.count(Message.event_id).desc()
    ).limit(limit).all()

def get_hourly_activity(db: Session, days: int = 7):
    """获取每小时活跃度统计"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return db.query(
        extract('hour', Message.timestamp).label('hour'),
        func.count(Message.event_id).label('count')
    ).filter(
        Message.timestamp >= start_date
    ).group_by(
        extract('hour', Message.timestamp)
    ).order_by(
        extract('hour', Message.timestamp)
    ).all()

def get_word_frequency(db: Session, limit: int = 50, days: int = 7):
    """获取高频词统计"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    messages = db.query(Message.content).filter(
        Message.timestamp >= start_date
    ).all()
    
    # 返回原始消息内容供后续处理
    return [msg[0] for msg in messages]

def get_user_interaction_pairs(db: Session, days: int = 7, min_count: int = 3, room_id: Optional[str] = None) -> List[Tuple]:
    """
    获取用户互动对，支持按房间筛选
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(
        Message.room_id,
        Message.sender_id,
        Message.timestamp
    ).filter(
        Message.timestamp.between(start_date, end_date)
    )
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    
    # 转换为 tuple 列表
    return [tuple(row) for row in query.order_by(Message.timestamp).all()]

def get_message_trends(db: Session, days: int = 7, interval: str = "day"):
    """获取消息趋势数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    if interval == "hour":
        group_by = func.date_trunc('hour', Message.timestamp)
    elif interval == "week":
        group_by = func.date_trunc('week', Message.timestamp)
    else:  # default: day
        group_by = func.date_trunc('day', Message.timestamp)
    
    return db.query(
        group_by.label('period'),
        func.count(Message.event_id).label('count')
    ).filter(
        Message.timestamp >= start_date
    ).group_by('period').order_by('period').all()

def get_conversation_patterns(db: Session, days: int = 7):
    """分析对话模式"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取消息序列
    messages = db.query(
        Message.room_id,
        Message.sender_id,
        Message.timestamp,
        Message.content
    ).filter(
        Message.timestamp >= start_date
    ).order_by(
        Message.room_id,
        Message.timestamp
    ).all()
    
    # 计算回复时间间隔
    intervals = []
    prev_msg = None
    for msg in messages:
        if prev_msg and prev_msg.room_id == msg.room_id:
            interval = (msg.timestamp - prev_msg.timestamp).total_seconds()
            intervals.append(interval)
        prev_msg = msg
    
    return {
        "avg_response_time": sum(intervals) / len(intervals) if intervals else 0,
        "peak_hours": _calculate_peak_hours(messages),
        "common_patterns": _analyze_conversation_flow(messages)
    }

def _calculate_peak_hours(messages):
    """Calculate peak activity hours"""
    hours = [msg.timestamp.hour for msg in messages]
    hour_counts = Counter(hours)
    return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)

def _analyze_conversation_flow(messages):
    """分析对话流模式"""
    patterns = []
    current_pattern = []
    prev_sender = None
    
    for msg in messages:
        if prev_sender and msg.sender_id != prev_sender:
            if len(current_pattern) >= 2:
                patterns.append(current_pattern.copy())
            current_pattern = [msg.sender_id]
        else:
            current_pattern.append(msg.sender_id)
        prev_sender = msg.sender_id
    
    return patterns

def get_activity_heatmap(db: Session, days: int = 7, room_id: Optional[str] = None) -> List[Tuple]:
    """
    获取活动热力图数据
    
    参数:
        db: 数据库会话
        days: 分析天数
        room_id: 可选的房间ID过滤
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(
        func.extract('dow', Message.timestamp).label('weekday'),
        func.extract('hour', Message.timestamp).label('hour'),
        func.count('*').label('count')
    ).filter(
        Message.timestamp.between(start_date, end_date)
    )
    
    if room_id:
        query = query.filter(Message.room_id == room_id)
    
    # 转换为 tuple 列表
    return [tuple(row) for row in query.group_by(
        'weekday',
        'hour'
    ).order_by('weekday', 'hour').all()]
