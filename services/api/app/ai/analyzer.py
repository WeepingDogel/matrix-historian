import os
from typing import List, Dict, Tuple
import groq
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import logging
import jieba
from collections import Counter
import networkx as nx

logger = logging.getLogger(__name__)

class MessageAnalyzer:
    def __init__(self):
        self.client = groq.Groq()
        self.client.api_key = os.getenv("GROQ_API_KEY")
        self.stop_words = set(['的', '了', '和', '是', '就', '都', '而', '及', '与', '着'])
        
    async def analyze_sentiment(self, messages: List[Dict], **kwargs) -> dict:
        """分析消息情感倾向"""
        try:
            # 准备消息文本
            texts = [msg["content"] for msg in messages]
            combined_text = "\n".join(texts)
            
            system_prompt = """你是一个专门进行数据分析的AI助手。请按照以下格式返回JSON：
{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "analysis": "分析总结"
}"""
            user_prompt = f"""分析以下消息的整体情感倾向：\n{combined_text}"""
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=kwargs.get('model', 'llama-3.1-8b-instant'),
                temperature=0,
                max_tokens=500,
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # 规范化返回结果
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": float(result.get("confidence", 0.5)),
                "analysis": result.get("analysis", "无法分析情感倾向")
            }
            
        except json.JSONDecodeError:
            logger.error("AI返回的不是有效的JSON格式")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "analysis": "分析失败：返回格式错误"
            }
        except Exception as e:
            logger.error(f"情感分析失败: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "analysis": f"分析失败：{str(e)}"
            }

    async def generate_summary(self, messages: List[Dict]) -> dict:
        """生成对话摘要"""
        try:
            texts = [f"{msg['sender']['display_name']}: {msg['content']}" 
                    for msg in messages]
            combined_text = "\n".join(texts)
            
            system_prompt = "你是一个专门总结对话的AI助手。只返回JSON格式的结果，包含summary和key_points字段。"
            user_prompt = f"""为这段对话生成摘要：\n{combined_text}"""
            
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=1000,
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
            
        except json.JSONDecodeError:
            logger.error("AI返回的不是有效的JSON格式")
            return {"error": "invalid_json", "message": "AI返回格式错误"}
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            return {"error": "summary_failed", "message": str(e)}

    def generate_activity_chart(self, messages: List[Dict]) -> go.Figure:
        """生成活动趋势图表"""
        # 转换消息时间戳为pandas时间序列
        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 按小时统计消息数量
        hourly_counts = df.groupby(pd.Grouper(key='timestamp', freq='H')).size()
        
        # 创建图表
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_counts.index,
            y=hourly_counts.values,
            mode='lines',
            name='消息数量'
        ))
        
        fig.update_layout(
            title='消息活动趋势',
            xaxis_title='时间',
            yaxis_title='消息数量',
            template='plotly_dark'
        )
        
        return fig

    def generate_user_interaction_chart(self, messages: List[Dict]) -> go.Figure:
        """生成用户互动图表"""
        df = pd.DataFrame(messages)
        
        # 统计用户发言次数
        user_counts = df['sender'].apply(lambda x: x['display_name']).value_counts()
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=user_counts.index,
            values=user_counts.values,
            hole=.3
        )])
        
        fig.update_layout(
            title='用户参与度分布',
            template='plotly_dark'
        )
        
        return fig
    
    def analyze_word_frequency(self, messages: List[str]) -> List[Tuple[str, int]]:
        """分析词频"""
        words = []
        for message in messages:
            words.extend(
                w for w in jieba.cut(message)
                if len(w) > 1 and w not in self.stop_words
            )
        return Counter(words).most_common(50)
    
    def analyze_user_interactions(self, messages: List[Dict]) -> nx.Graph:
        """分析用户互动网络"""
        G = nx.Graph()
        
        # 构建用户互动图
        for i in range(len(messages) - 1):
            current = messages[i]
            next_msg = messages[i + 1]
            
            # 检查消息是否在同一房间
            if (current['room_id'] == next_msg['room_id'] and 
                current['sender_id'] != next_msg['sender_id']):
                # 添加或更新边的权重
                weight = G.get_edge_data(
                    current['sender_id'],
                    next_msg['sender_id'],
                    {"weight": 0}
                )["weight"]
                
                G.add_edge(
                    current['sender_id'],
                    next_msg['sender_id'],
                    weight=weight + 1
                )
        
        return G
    
    def generate_activity_heatmap(self, messages: List[Dict]) -> pd.DataFrame:
        """生成活动热力图数据"""
        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['weekday'] = df['timestamp'].dt.weekday
        
        heatmap_data = df.groupby(['weekday', 'hour']).size().unstack(fill_value=0)
        return heatmap_data
