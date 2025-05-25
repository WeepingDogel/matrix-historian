import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
import os
from datetime import datetime
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx

def render_analysis_page():
    st.title("消息分析")
    
    api_url = os.getenv("API_URL", "http://app:8000/api/v1")
    
    # 添加侧边栏房间选择
    with st.sidebar:
        days = st.slider("分析时间范围", 1, 30, 7)
        
        # 获取房间列表
        rooms = fetch_api_data(f"{api_url}/rooms")
        room_options = {"全部": None}
        if rooms:
            for room in rooms:
                display_name = f"{room.get('name', '')} ({room['room_id']})"
                room_options[display_name] = room['room_id']
        
        # 添加 on_change 回调来触发重新运行
        if 'previous_room' not in st.session_state:
            st.session_state.previous_room = "全部"
            
        selected_room = st.selectbox(
            "选择房间",
            options=list(room_options.keys()),
            key="analysis_room",
            on_change=lambda: st.rerun()
        )
        
        # 更新前一个选择
        if selected_room != st.session_state.previous_room:
            st.session_state.previous_room = selected_room
            st.rerun()
            
        room_id = room_options[selected_room]

    # 更新所有渲染函数调用，传入room_id参数
    st.header("活动概览")
    render_activity_overview(api_url, days, room_id)
    
    st.markdown("---")  # 分隔线
    
    st.header("词云分析")
    render_wordcloud_analysis(api_url, days, room_id)
    
    st.markdown("---")
    
    st.header("用户互动")
    render_user_interactions(api_url, days, room_id)
    
    st.markdown("---")
    
    st.header("话题分析")
    render_topic_analysis(api_url, days, room_id)
    
    st.markdown("---")
    
    st.header("情感分析")
    render_sentiment_analysis(api_url, days, room_id)
    
    st.markdown("---")
    
    st.header("活跃度分析")
    render_activity_patterns(api_url, days, room_id)

def render_activity_overview(api_url: str, days: int, room_id: str = None):
    try:
        # 获取概览数据
        overview = fetch_api_data(f"{api_url}/analytics/overview", {"days": days, "room_id": room_id})
        if overview:
            col1, col2 = st.columns(2)
            with col1:
                # 消息趋势
                if "message_stats" in overview:
                    df = pd.DataFrame(overview["message_stats"])
                    fig = px.line(df, x="date", y="count", title="消息趋势")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 用户活跃度
                if "user_activity" in overview:
                    user_df = pd.DataFrame([
                        {"user": item["user"]["display_name"] or item["user"]["user_id"],
                         "count": item["message_count"]}
                        for item in overview["user_activity"]
                    ])
                    fig = px.pie(user_df, values="count", names="user", title="用户活跃度")
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"加载活动概览失败: {str(e)}")

def render_wordcloud_analysis(api_url: str, days: int, room_id: str = None):
    """渲染词云分析"""
    
    try:
        params = {"days": days, "room_id": room_id}
        response = requests.get(f"{api_url}/analytics/wordcloud", params=params)
        data = response.json()
        
        if data and "messages" in data:
            # 转换为DataFrame
            df = pd.DataFrame(data["messages"])
            
            if not df.empty:
                # 显示词频统计
                st.subheader("高频词统计")
                fig = px.bar(df.head(20), 
                           x="word", 
                           y="count",
                           title="词频统计 (Top 20)")
                st.plotly_chart(fig, use_container_width=True)
                
                # 生成词云
                word_dict = {row['word']: row['count'] for _, row in df.iterrows()}
                
                # 使用默认字体，不指定具体路径
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    font_path='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'  # 更新字体路径
                ).generate_from_frequencies(word_dict)
                
                fig, ax = plt.subplots()
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
    except FileNotFoundError as e:
        st.error("字体文件未找到，尝试使用备用字体")
        # 尝试使用备用字体
        try:
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white'
            ).generate_from_frequencies(word_dict)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"生成词云失败: {str(e)}")
    except Exception as e:
        st.error(f"加载词云数据失败: {str(e)}")
        if st.checkbox("显示详细错误信息"):
            st.exception(e)

def render_user_interactions(api_url: str, days: int, room_id: str = None):
    try:
        params = {"days": days, "room_id": room_id}
        data = fetch_api_data(f"{api_url}/analytics/user-network", params)
        if data and "nodes" in data and "edges" in data:
            # 创建网络图
            G = nx.Graph()
            for node in data["nodes"]:
                G.add_node(node["id"])
            for edge in data["edges"]:
                G.add_edge(edge["source"], edge["target"], weight=edge["weight"])
            
            # 绘制网络图
            pos = nx.spring_layout(G)
            fig, ax = plt.subplots(figsize=(10, 10))
            nx.draw(G, pos, with_labels=True, node_color='lightblue',
                   node_size=1000, font_size=8, 
                   width=[d['weight'] for (_,_,d) in G.edges(data=True)])
            st.pyplot(fig)
            
            # 互动强度热力图
            st.subheader("互动强度分析")
            edges_df = pd.DataFrame(data["edges"])
            if not edges_df.empty:
                fig = px.density_heatmap(
                    edges_df, 
                    x="source", 
                    y="target",
                    z="weight",
                    title="用户互动热力图"
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"加载用户互动分析失败: {str(e)}")

def render_topic_analysis(api_url: str, days: int, room_id: str = None):
    try:
        params = {"days": days, "room_id": room_id}
        data = fetch_api_data(f"{api_url}/analytics/topic-evolution", params)
        if data and "topics" in data:
            # 话题趋势图
            df = pd.DataFrame(data["topics"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            fig = px.line(df, x="timestamp", y="weight", 
                         color="topic", title="话题演变趋势")
            st.plotly_chart(fig, use_container_width=True)
            
            # 话题分布
            if "summary" in data:
                st.subheader("主要话题")
                for topic in data["summary"]["main_topics"]:
                    st.markdown(f"- {topic}")
                st.info(data["summary"]["analysis"])
    except Exception as e:
        st.error(f"加载话题分析失败: {str(e)}")

def render_sentiment_analysis(api_url: str, days: int, room_id: str = None):
    try:
        params = {"days": days, "room_id": room_id}
        data = fetch_api_data(f"{api_url}/analytics/sentiment", params)
        if data:
            col1, col2 = st.columns([2, 1])
            with col1:
                # 情感仪表盘
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = data["confidence"],
                    title = {'text': f"情感倾向: {data['sentiment']}"},
                    gauge = {
                        'axis': {'range': [0, 1]},
                        'bar': {'color': "darkblue"},
                        'steps' : [
                            {'range': [0, 0.3], 'color': "lightgray"},
                            {'range': [0.3, 0.7], 'color': "gray"},
                            {'range': [0.7, 1], 'color': "darkgray"}
                        ],
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.info(data["analysis"])
    except Exception as e:
        st.error(f"加载情感分析失败: {str(e)}")

def render_activity_patterns(api_url: str, days: int, room_id: str = None):
    try:
        params = {"days": days, "room_id": room_id}
        data = fetch_api_data(f"{api_url}/analytics/activity-heatmap", params)
        if data and "heatmap" in data:
            # 转换热力图数据
            heatmap_df = pd.DataFrame(data["heatmap"])
            total_messages = heatmap_df.values.sum()
            
            # 显示总体活跃度统计
            col_metric, _, _ = st.columns([1, 1, 1])
            with col_metric:
                st.metric("总消息数", total_messages)

            # 居中显示热力图
            st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_df.values,
                x=data["hours"],
                y=data["weekdays"],
                colorscale="Viridis",
                hoverongaps=False
            ))
            fig.update_layout(
                title="活动时间分布",
                xaxis_title="小时",
                yaxis_title="星期",
                height=400,
                width=800
            )
            st.plotly_chart(fig, use_container_width=False)
            
            # 居中显示小时统计
            hourly_sums = heatmap_df.sum().values
            hours = list(range(len(hourly_sums)))
            
            hourly_df = pd.DataFrame({
                'hour': hours,
                'count': hourly_sums
            })
            
            fig_hourly = px.bar(
                hourly_df,
                x='hour',
                y='count',
                title="每小时活跃度"
            )
            fig_hourly.update_layout(
                xaxis_title="小时",
                yaxis_title="消息数量",
                width=800,
                height=400
            )
            st.plotly_chart(fig_hourly, use_container_width=False)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 活跃时段分析
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.subheader("活跃时段分析")
                peak_hour = int(hourly_df.loc[hourly_df['count'].idxmax(), 'hour'])
                peak_day_idx = int(heatmap_df.sum(axis=1).idxmax())
                weekdays = data["weekdays"]
                peak_day = weekdays[peak_day_idx] if 0 <= peak_day_idx < len(weekdays) else "未知"
                
                st.info(f"""
                - 最活跃时段: {peak_hour}:00
                - 最活跃日期: {peak_day}
                - 平均每小时消息: {total_messages/(24*7):.1f}条
                """)
            
    except Exception as e:
        st.error(f"加载活动模式分析失败: {str(e)}")
        if st.checkbox("显示详细错误信息"):
            st.exception(e)

def fetch_api_data(url: str, params: dict = None) -> dict:
    """统一的API数据获取函数"""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API请求失败: {str(e)}")
        return None
