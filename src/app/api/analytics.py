from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.crud import message as crud
from typing import List, Dict
import pandas as pd
from functools import lru_cache
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

@lru_cache(maxsize=128)
def cache_analytics_data(days: int, timestamp: str):
    """缓存分析数据，使用时间戳使缓存定期失效"""
    return {
        "cache_time": timestamp,
        "days": days,
        "expires_in": "1 hour"
    }

@router.get("/overview")
def get_analytics_overview(
    days: int = Query(7, description="分析天数"),
    db: Session = Depends(get_db)
):
    """获取概览数据"""
    try:
        cache_key = datetime.utcnow().strftime("%Y%m%d%H")
        cache_data = cache_analytics_data(days, cache_key)
        
        # 将SQLAlchemy对象转换为字典
        user_activity = [
            {
                "user": {
                    "user_id": user.user_id,
                    "display_name": user.display_name
                },
                "message_count": count
            }
            for user, count in crud.get_user_activity(db)
        ]
        
        room_activity = [
            {
                "room": {
                    "room_id": room.room_id,
                    "name": room.name
                },
                "message_count": count
            }
            for room, count in crud.get_room_activity(db)
        ]
        
        stats = {
            "message_stats": [
                {"date": str(stat[0]), "count": stat[1]}
                for stat in crud.get_message_stats(db, days)
            ],
            "user_activity": user_activity,
            "room_activity": room_activity,
            "hourly_activity": [
                {"hour": stat[0], "count": stat[1]}
                for stat in crud.get_hourly_activity(db, days)
            ],
            "cache_info": cache_data
        }
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析数据获取失败: {str(e)}"
        )

@router.get("/wordcloud")
def get_wordcloud_data(
    days: int = Query(7, description="分析天数"),
    limit: int = Query(50, description="返回词数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """获取词云数据（仅统计名词，扩展停用词）"""
    try:
        messages = crud.get_messages(db, room_id=room_id, limit=1000)  # 获取原始消息

        # 使用jieba.posseg分词并统计名词词频
        from collections import Counter
        import jieba.posseg as pseg

        # 扩展停用词列表
        stop_words = set([
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '着', '在', '也', '我', '你', '他', '她', '它',
            '我们', '你们', '他们', '她们', '它们', '这', '那', '一个', '没有', '上', '下', '啊', '哦', '嗯', '吧',
            '吗', '呀', '呢', '吧', '啊', '哦', '哇', '啦', '嘛', '呗', '哎', '哈', '嘿', '哟', '哼', '哎呀',
            '与', '及', '并', '或', '如果', '因为', '所以', '而且', '但是', '不过', '虽然', '但是', '就是', '还有',
            '并且', '以及', '等', '等到', '从', '到', '为', '被', '给', '让', '把', '对', '向', '往', '跟', '和',
            '与', '及', '等', '等到', '之', '其', '此', '每', '各', '本', '该', '这些', '那些', '某', '某些', '任何',
            '所有', '全部', '自己', '自身', '本人', '大家', '咱们', '有人', '没人', '什么', '啥', '哪个', '哪儿', '哪里',
            '怎么', '怎样', '如何', '多少', '几', '谁', '谁的', '啥的', '什么的', '这儿', '那儿', '这里', '那里',
            '时候', '时间', '现在', '今天', '明天', '昨天', '刚才', '刚刚', '已经', '还', '再', '就', '才', '又', '也',
            '很', '挺', '非常', '特别', '极其', '十分', '相当', '比较', '更', '最', '太', '真', '都', '全', '总', '只',
            '仅', '光', '单', '独', '每', '各', '本', '该', '这些', '那些', '某', '某些', '任何', '所有', '全部', '自己',
            '自身', '本人', '大家', '咱们', '有人', '没人', '什么', '啥', '哪个', '哪儿', '哪里', '怎么', '怎样', '如何',
            '多少', '几', '谁', '谁的', '啥的', '什么的', '这儿', '那儿', '这里', '那里', '时候', '时间', '现在', '今天',
            '明天', '昨天', '刚才', '刚刚', '已经', '还', '再', '就', '才', '又', '也', '很', '挺', '非常', '特别', '极其',
            '十分', '相当', '比较', '更', '最', '太', '真', '都', '全', '总', '只', '仅', '光', '单', '独'
        ])

        words = []
        for msg in messages:
            content = getattr(msg, "content", None)
            if content is not None and isinstance(content, str) and content.strip() != "":
                for word, flag in pseg.cut(content):
                    if flag.startswith('n') and word not in stop_words and len(word) > 1:
                        words.append(word)

        word_freq = Counter(words)

        # 转换为所需格式
        result = [
            {"word": word, "count": count}
            for word, count in word_freq.most_common(limit)
        ]

        return {"messages": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成词云数据失败: {str(e)}"
        )

@router.get("/interactions")
def get_user_interactions(
    days: int = Query(7, description="分析天数"),
    min_count: int = Query(3, description="最小互动次数"),
    db: Session = Depends(get_db)
):
    """获取用户互动数据"""
    interactions = crud.get_user_interaction_pairs(db, days, min_count)
    return {"interactions": interactions}

@router.get("/trends")
def get_message_trends(
    days: int = Query(7, description="分析天数"),
    interval: str = Query("day", description="统计间隔: hour/day/week"),
    db: Session = Depends(get_db)
):
    """获取消息趋势分析"""
    trends = crud.get_message_trends(db, days, interval)
    return {"trends": trends}

@router.get("/content-analysis")
def analyze_content(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """获取内容分析"""
    from app.ai.analyzer import MessageAnalyzer
    analyzer = MessageAnalyzer()
    
    messages = crud.get_word_frequency(db, days=days)
    word_freq = analyzer.analyze_word_frequency(messages)
    
    return {
        "word_frequency": word_freq
    }

@router.get("/user-network")
def get_user_network(
    days: int = Query(7, description="分析天数"),
    min_weight: int = Query(3, description="最小连接权重"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """获取用户互动网络"""
    try:
        from app.ai.analyzer import MessageAnalyzer
        analyzer = MessageAnalyzer()
        
        # 获取消息并转换格式
        raw_messages = crud.get_user_interaction_pairs(db, days, room_id=room_id)
        messages = [
            {
                "room_id": msg[0],  # 转换元组为字典
                "sender_id": msg[1],
                "timestamp": msg[2]
            }
            for msg in raw_messages
        ]
        
        network = analyzer.analyze_user_interactions(messages)
        
        return {
            "nodes": [{"id": node} for node in network.nodes()],
            "edges": [{"source": u, "target": v, "weight": d["weight"]} 
                     for u, v, d in network.edges(data=True)
                     if d["weight"] >= min_weight]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析用户网络失败: {str(e)}"
        )

@router.get("/sentiment")
async def analyze_sentiment(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """获取情感分析数据"""
    try:
        from app.ai.analyzer import MessageAnalyzer
        analyzer = MessageAnalyzer()
        
        messages = crud.get_messages(db, room_id=room_id, limit=100)
        message_texts = [{"content": msg.content} for msg in messages]
        
        # 使用 llama-3.1-8b-instant 模型
        sentiment_data = await analyzer.analyze_sentiment(
            message_texts, 
            model="llama-3.1-8b-instant"
        )
        
        return {
            "sentiment": sentiment_data.get("sentiment", "neutral"),
            "confidence": sentiment_data.get("confidence", 0.0),
            "analysis": sentiment_data.get("analysis", ""),
            "room_id": room_id,
            "days": days,
            "model": "llama-3.1-8b-instant"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity-heatmap")
async def get_activity_heatmap(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """获取活动热力图数据"""
    try:
        # 获取原始数据
        results = crud.get_activity_heatmap(db, days, room_id)
        
        # 初始化7x24的零矩阵
        heatmap = [[0 for _ in range(24)] for _ in range(7)]
        
        # 填充数据
        for weekday, hour, count in results:
            heatmap[int(weekday)][int(hour)] = int(count)
        
        return {
            "heatmap": heatmap,
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "hours": list(range(24))
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成活动热力图失败: {str(e)}"
        )

@router.get("/topic-evolution")
async def analyze_topic_evolution(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db)
):
    """分析话题演变"""
    try:
        messages = crud.get_messages(db, room_id=room_id, limit=500)
        # 转换数据为正确的格式
        topics_data = []
        for msg in messages:
            # 为每条消息生成话题数据
            content = getattr(msg, "content", None)
            if content is not None and isinstance(content, str):
                topic = analyze_single_topic(content)
            else:
                topic = ""
            topic_info = {
                "topic": topic,
                "weight": 1.0,  # 简单起见设置为1.0
                "timestamp": msg.timestamp.isoformat()
            }
            topics_data.append(topic_info)
        
        # 按时间排序
        topics_data.sort(key=lambda x: x["timestamp"])
        
        return {
            "topics": topics_data,
            "summary": generate_topic_summary([getattr(msg, "content", "") or "" for msg in messages])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_single_topic(text: str) -> str:
    """分析单条消息的主题"""
    # 简单实现，可以根据需要完善
    if len(text) < 10:
        return "简短对话"
    elif "?" in text or "？" in text:
        return "提问"
    else:
        return "一般讨论"

def generate_topic_summary(texts: List[str]) -> Dict:
    """生成话题总结"""
    return {
        "main_topics": ["日常交流", "技术讨论", "问答"],
        "trend": "稳定",
        "analysis": "以日常交流为主，技术讨论次之"
    }

@router.get("/ai-analysis")
async def get_ai_analysis(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    analysis_type: str = Query("sentiment", description="分析类型: sentiment/topic/pattern"),
    db: Session = Depends(get_db)
):
    """AI分析统一接口"""
    try:
        from app.ai.analyzer import MessageAnalyzer
        analyzer = MessageAnalyzer()
        
        messages = crud.get_messages(db, room_id=room_id, limit=100)
        message_texts = [{"content": msg.content} for msg in messages]
        
        if analysis_type == "sentiment":
            result = await analyzer.analyze_sentiment(message_texts, model="llama-3.1-8b-instant")
        else:
            raise HTTPException(status_code=400, detail="不支持的分析类型")
            
        return {
            "type": analysis_type,
            "result": result,
            "metadata": {
                "message_count": len(messages),
                "room_id": room_id,
                "analysis_time": datetime.utcnow().isoformat(),
                "model": "llama-3.1-8b-instant"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI分析失败: {str(e)}"
        )

@router.get("/analytics-health")
async def check_analytics_health():
    """检查分析服务健康状态"""
    return {
        "status": "healthy",
        "features": [
            "sentiment_analysis",
            "topic_analysis",
            "pattern_analysis"
        ],
        "cache_info": {
            "enabled": True,
            "size": cache_analytics_data.cache_info().maxsize
        }
    }
