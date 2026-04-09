import re
import sys

sys.path.insert(0, "/app/shared")  # Still correct, base_app is under shared
from datetime import datetime  # noqa: E402
from typing import Dict, List  # noqa: E402

from base_app.crud import message as crud  # noqa: E402
from base_app.db.database import get_db  # noqa: E402
from cache import cache_key, get_cached, set_cached  # noqa: E402
from fastapi import APIRouter, Depends, HTTPException, Query  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def get_analytics_overview(
    days: int = Query(7, description="分析天数"), db: Session = Depends(get_db)
):
    """获取概览数据"""
    try:
        key = cache_key("overview", days)
        cached = get_cached(key)
        if cached is not None:
            return cached

        # 将SQLAlchemy对象转换为字典
        user_activity = [
            {
                "user": {"user_id": user.user_id, "display_name": user.display_name},
                "message_count": count,
            }
            for user, count in crud.get_user_activity(db)
        ]

        room_activity = [
            {
                "room": {"room_id": room.room_id, "name": room.name},
                "message_count": count,
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
        }
        return set_cached(key, stats)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"分析数据获取失败: {str(e)}"
        ) from e


@router.get("/wordcloud")
def get_wordcloud_data(
    days: int = Query(7, description="分析天数"),
    limit: int = Query(50, description="返回词数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """获取词云数据（仅统计名词，扩展停用词）"""
    try:
        key = cache_key("wordcloud", days, limit, room_id)
        cached = get_cached(key)
        if cached is not None:
            return cached

        messages = crud.get_messages(db, room_id=room_id, limit=1000)  # 获取原始消息

        # 使用jieba.posseg分词并统计名词词频
        from collections import Counter  # noqa: E402

        import jieba.posseg as pseg  # noqa: E402

        # Pre-compile URL/mxc pattern for stripping links before segmentation
        url_pattern = re.compile(r"https?://\S+|mxc://\S+")

        # 扩展停用词列表
        stop_words = set(
            [
                "一个",
                "上",
                "下",
                "不过",
                "与",
                "为",
                "之",
                "也",
                "了",
                "什么",
                "什么的",
                "仅",
                "今天",
                "从",
                "他",
                "他们",
                "以及",
                "任何",
                "但是",
                "你",
                "你们",
                "光",
                "全",
                "全部",
                "其",
                "再",
                "几",
                "刚刚",
                "刚才",
                "到",
                "十分",
                "单",
                "又",
                "及",
                "只",
                "各",
                "向",
                "吗",
                "吧",
                "呀",
                "呗",
                "呢",
                "和",
                "咱们",
                "哇",
                "哈",
                "哎",
                "哎呀",
                "哟",
                "哦",
                "哪个",
                "哪儿",
                "哪里",
                "哼",
                "啊",
                "啥",
                "啥的",
                "啦",
                "嗯",
                "嘛",
                "嘿",
                "因为",
                "在",
                "多少",
                "大家",
                "太",
                "她",
                "她们",
                "如何",
                "如果",
                "它",
                "它们",
                "对",
                "就",
                "就是",
                "已经",
                "并",
                "并且",
                "往",
                "很",
                "怎么",
                "怎样",
                "总",
                "我",
                "我们",
                "或",
                "所以",
                "所有",
                "才",
                "把",
                "挺",
                "时候",
                "时间",
                "明天",
                "昨天",
                "是",
                "更",
                "最",
                "有人",
                "本",
                "本人",
                "极其",
                "某",
                "某些",
                "此",
                "每",
                "比较",
                "没人",
                "没有",
                "特别",
                "独",
                "现在",
                "的",
                "相当",
                "真",
                "着",
                "等",
                "等到",
                "给",
                "而",
                "而且",
                "自己",
                "自身",
                "虽然",
                "被",
                "让",
                "该",
                "谁",
                "谁的",
                "跟",
                "还",
                "还有",
                "这",
                "这些",
                "这儿",
                "这里",
                "那",
                "那些",
                "那儿",
                "那里",
                "都",
                "非常",
            ]
        )
        # URL and media related
        stop_words.update(
            [
                "https",
                "http",
                "www",
                "com",
                "org",
                "net",
                "cn",
                "image",
                "jpeg",
                "jpg",
                "png",
                "gif",
                "webp",
                "mp4",
                "mp3",
                "wav",
                "ogg",
                "mxc",
                "matrix",
                "svg",
                "pdf",
                "zip",
                "rar",
                # Common web/tech noise
                "html",
                "css",
                "json",
                "xml",
                "api",
                "url",
                "file",
                # Short meaningless fragments
                "de",
                "le",
                "la",
                "el",
                "en",
                "id",
                "re",
            ]
        )

        words = []
        for msg in messages:
            content = getattr(msg, "content", None)
            if (
                content is not None
                and isinstance(content, str)
                and content.strip() != ""
            ):
                content = url_pattern.sub("", content)  # Strip URLs before segmentation
                for word, flag in pseg.cut(content):
                    if (
                        flag.startswith("n")
                        and word not in stop_words
                        and len(word) > 1
                    ):
                        words.append(word)

        word_freq = Counter(words)

        # 转换为所需格式
        result = [
            {"word": word, "count": count}
            for word, count in word_freq.most_common(limit)
        ]

        return set_cached(key, {"messages": result})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"生成词云数据失败: {str(e)}"
        ) from e


@router.get("/interactions")
def get_user_interactions(
    days: int = Query(7, description="分析天数"),
    min_count: int = Query(3, description="最小互动次数"),
    db: Session = Depends(get_db),
):
    """获取用户互动数据"""
    key = cache_key("interactions", days, min_count)
    cached = get_cached(key)
    if cached is not None:
        return cached

    interactions = crud.get_user_interaction_pairs(db, days, min_count)
    result = {
        "interactions": [
            {
                "room_id": row[0],
                "sender_id": row[1],
                "timestamp": (
                    row[2].isoformat() if hasattr(row[2], "isoformat") else str(row[2])
                ),
            }
            for row in interactions
        ]
    }
    return set_cached(key, result)


@router.get("/trends")
def get_message_trends(
    days: int = Query(7, description="分析天数"),
    interval: str = Query("day", description="统计间隔: hour/day/week"),
    db: Session = Depends(get_db),
):
    """获取消息趋势分析"""
    try:
        key = cache_key("trends", days, interval)
        cached = get_cached(key)
        if cached is not None:
            return cached

        trends = crud.get_message_trends(db, days, interval)
        result = {
            "trends": [{"period": str(trend[0]), "count": trend[1]} for trend in trends]
        }
        return set_cached(key, result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"获取消息趋势失败: {str(e)}"
        ) from e


@router.get("/content-analysis")
def analyze_content(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """获取内容分析"""
    from ai.analyzer import MessageAnalyzer  # noqa: E402

    analyzer = MessageAnalyzer()

    messages = crud.get_word_frequency(db, days=days)
    word_freq = analyzer.analyze_word_frequency(messages)

    return {"word_frequency": word_freq}


@router.get("/user-network")
def get_user_network(
    days: int = Query(7, description="分析天数"),
    min_weight: int = Query(3, description="最小连接权重"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """获取用户互动网络"""
    try:
        from ai.analyzer import MessageAnalyzer  # noqa: E402

        analyzer = MessageAnalyzer()

        # 获取消息并转换格式
        raw_messages = crud.get_user_interaction_pairs(db, days, room_id=room_id)
        messages = [
            {
                "room_id": msg[0],  # 转换元组为字典
                "sender_id": msg[1],
                "timestamp": msg[2],
            }
            for msg in raw_messages
        ]

        network = analyzer.analyze_user_interactions(messages)

        return {
            "nodes": [{"id": node} for node in network.nodes()],
            "edges": [
                {"source": u, "target": v, "weight": d["weight"]}
                for u, v, d in network.edges(data=True)
                if d["weight"] >= min_weight
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"分析用户网络失败: {str(e)}"
        ) from e


@router.get("/sentiment")
async def analyze_sentiment(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """获取情感分析数据"""
    try:
        key = cache_key("sentiment", days, room_id)
        cached = get_cached(key)
        if cached is not None:
            return cached

        from ai.analyzer import MessageAnalyzer  # noqa: E402

        analyzer = MessageAnalyzer()

        messages = crud.get_messages(db, room_id=room_id, limit=100)
        message_texts = [{"content": msg.content} for msg in messages]

        # 使用 llama-3.1-8b-instant 模型
        sentiment_data = await analyzer.analyze_sentiment(
            message_texts, model="llama-3.1-8b-instant"
        )

        result = {
            "sentiment": sentiment_data.get("sentiment", "neutral"),
            "confidence": sentiment_data.get("confidence", 0.0),
            "analysis": sentiment_data.get("analysis", ""),
            "room_id": room_id,
            "days": days,
            "model": "llama-3.1-8b-instant",
        }
        return set_cached(key, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/activity-heatmap")
async def get_activity_heatmap(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """获取活动热力图数据"""
    try:
        key = cache_key("activity_heatmap", days, room_id)
        cached = get_cached(key)
        if cached is not None:
            return cached

        # 获取原始数据
        results = crud.get_activity_heatmap(db, days, room_id)

        # 初始化7x24的零矩阵
        heatmap = [[0 for _ in range(24)] for _ in range(7)]

        # 填充数据
        for weekday, hour, count in results:
            heatmap[int(weekday)][int(hour)] = int(count)

        result = {
            "heatmap": heatmap,
            "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "hours": list(range(24)),
        }
        return set_cached(key, result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"生成活动热力图失败: {str(e)}"
        ) from e


@router.get("/topic-evolution")
async def analyze_topic_evolution(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    db: Session = Depends(get_db),
):
    """分析话题演变"""
    try:
        key = cache_key("topic_evolution", days, room_id)
        cached = get_cached(key)
        if cached is not None:
            return cached

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
                "timestamp": msg.timestamp.isoformat(),
            }
            topics_data.append(topic_info)

        # 按时间排序
        topics_data.sort(key=lambda x: x["timestamp"])

        result = {
            "topics": topics_data,
            "summary": generate_topic_summary(
                [getattr(msg, "content", "") or "" for msg in messages]
            ),
        }
        return set_cached(key, result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


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
        "analysis": "以日常交流为主，技术讨论次之",
    }


@router.get("/ai-analysis")
async def get_ai_analysis(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    analysis_type: str = Query(
        "sentiment", description="分析类型: sentiment/topic/pattern"
    ),
    db: Session = Depends(get_db),
):
    """AI分析统一接口"""
    try:
        from ai.analyzer import MessageAnalyzer  # noqa: E402

        analyzer = MessageAnalyzer()

        messages = crud.get_messages(db, room_id=room_id, limit=100)
        message_texts = [{"content": msg.content} for msg in messages]

        if analysis_type == "sentiment":
            result = await analyzer.analyze_sentiment(
                message_texts, model="llama-3.1-8b-instant"
            )
            model_used = "llama-3.1-8b-instant"
        elif analysis_type == "summary":
            message_dicts = [
                {
                    "sender": {
                        "display_name": (
                            msg.sender.display_name if msg.sender else msg.sender_id
                        )
                    },
                    "content": msg.content,
                }
                for msg in messages
            ]
            result = await analyzer.generate_summary(message_dicts)
            model_used = "llama-3.1-8b-instant"
        else:
            raise HTTPException(status_code=400, detail="不支持的分析类型")

        return {
            "type": analysis_type,
            "result": result,
            "metadata": {
                "message_count": len(messages),
                "room_id": room_id,
                "analysis_time": datetime.utcnow().isoformat(),
                "model": model_used,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI分析失败: {str(e)}"
        ) from e


@router.get("/user-hourly-activity")
async def get_user_hourly_activity(
    days: int = Query(7, description="分析天数"),
    room_id: str = Query(None, description="房间ID"),
    limit: int = Query(50, description="返回用户数量限制"),
    db: Session = Depends(get_db),
):
    """获取基于用户的每小时活动数据"""
    try:
        key = cache_key("user_hourly_activity", days, room_id, limit)
        cached = get_cached(key)
        if cached is not None:
            return cached

        # 获取原始数据
        results = crud.get_user_hourly_activity(db, days, room_id, limit)

        # 组织数据格式
        user_data = {}
        for user_id, hour, count in results:
            if user_id not in user_data:
                user_data[user_id] = {"user_id": user_id, "hourly_activity": [0] * 24}
            user_data[user_id]["hourly_activity"][int(hour)] = int(count)

        # 获取用户显示名称
        users = []
        for user_id, data in user_data.items():
            user = crud.get_user(db, user_id)
            display_name = user.display_name if user else user_id
            users.append(
                {
                    "user_id": user_id,
                    "display_name": display_name,
                    "hourly_activity": data["hourly_activity"],
                }
            )

        # 按总消息数排序
        users.sort(key=lambda x: sum(x["hourly_activity"]), reverse=True)

        result = {
            "users": users,
            "hours": list(range(24)),
            "days": days,
            "room_id": room_id,
            "user_count": len(users),
        }
        return set_cached(key, result)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"获取用户每小时活动数据失败: {str(e)}"
        ) from e


@router.get("/analytics-health")
async def check_analytics_health():
    """检查分析服务健康状态"""
    return {
        "status": "healthy",
        "features": [
            "sentiment_analysis",
            "topic_analysis",
            "pattern_analysis",
            "user_hourly_activity",
        ],
        "cache_info": {
            "enabled": True,
            "type": "cachetools.TTLCache",
            "ttl_seconds": 900,
        },
    }
