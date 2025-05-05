import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
from datetime import timezone
import humanize
import locale
import os
import logging

# 尝试设置中文locale，如果失败则使用系统默认
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except locale.Error:
    logging.warning("Failed to set zh_CN.UTF-8 locale, falling back to system default")
    locale.setlocale(locale.LC_ALL, '')

humanize.i18n.activate("zh_CN")

# 设置页面配置
st.set_page_config(
    page_title="Matrix Historian",
    page_icon="📝",
    layout="wide"
)

# API 基础URL
API_URL = os.getenv("API_URL")

def fetch_data(endpoint, params=None):
    params = params or {}
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except requests.RequestException as e:
        st.error(f"无法连接到API: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"数据解析错误: {str(e)}")
        return None

def get_relative_time(timestamp):
    """将时间转换为相对时间（xxx前）"""
    now = datetime.now(timezone.utc)
    dt = pd.to_datetime(timestamp)
    if isinstance(dt, pd.Timestamp):
        dt = dt.to_pydatetime()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return humanize.naturaltime(now - dt)

def format_room_name(room):
    """格式化房间显示名称"""
    name = room.get('name')
    room_id = room.get('room_id')
    return f"{name} ({room_id})" if name else room_id

def format_user_name(user):
    """格式化用户显示名称"""
    display_name = user.get('display_name')
    user_id = user.get('user_id')
    return f"{display_name} ({user_id})" if display_name else user_id

def highlight_text(text: str, query: str) -> str:
    """高亮文本中的搜索关键词"""
    if not query:
        return text
    # 使用HTML和CSS来高亮文本，添加橙色文字颜色
    highlighted = text.replace(query, f'<span style="color: #ff6b6b; font-weight: bold;">{query}</span>')
    return highlighted

def main():
    st.title("Matrix Historian")
    
    # 初始化会话状态
    if 'page' not in st.session_state:
        st.session_state.page = 0
        st.session_state.all_messages = []
        st.session_state.filters = {
            'query': '',
            'room': '全部',
            'user': '全部'
        }
    
    # 侧边栏过滤器
    with st.sidebar:
        st.header("过滤器")
        search_query = st.text_input("搜索消息")
        
        try:
            # 获取房间列表并格式化显示
            rooms = fetch_data("rooms")
            room_display = {"全部": "全部"}
            room_display.update({format_room_name(room): room["room_id"] for room in rooms})
            selected_room_display = st.selectbox("选择房间", options=list(room_display.keys()))
            selected_room = room_display[selected_room_display]
            
            # 获取用户列表并格式化显示
            users = fetch_data("users")
            user_display = {"全部": "全部"}
            user_display.update({format_user_name(user): user["user_id"] for user in users})
            selected_user_display = st.selectbox("选择用户", options=list(user_display.keys()))
            selected_user = user_display[selected_user_display]
            
            # 检查过滤条件是否改变
            current_filters = {
                'query': search_query,
                'room': selected_room_display,
                'user': selected_user_display
            }
            
            if current_filters != st.session_state.filters:
                st.session_state.page = 0
                st.session_state.all_messages = []
                st.session_state.filters = current_filters
                
            # 添加基本统计信息
            st.header("统计信息")
            st.metric("总房间数", len(rooms) if rooms else 0)
            st.metric("总用户数", len(users) if users else 0)
        except Exception as e:
            st.error(f"加载数据时出错: {str(e)}")
            return
    
    # 构建查询参数
    params = {
        'skip': len(st.session_state.all_messages),
        'limit': 100  # 修改为100以匹配API默认值
    }
    if search_query:
        params["query"] = search_query
    if selected_room != "全部":
        params["room_id"] = selected_room
    if selected_user != "全部":
        params["user_id"] = selected_user

    # 获取消息
    endpoint = "search" if search_query else "messages"
    response = fetch_data(endpoint, params)
    
    if response:
        new_messages = response.get("messages", [])
        total = response.get("total", 0)
        has_more = response.get("has_more", False)
        
        # 追加新消息
        if new_messages:
            st.session_state.all_messages.extend(new_messages)
        
        # 显示所有消息
        if st.session_state.all_messages:
            df = pd.DataFrame(st.session_state.all_messages)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False)
            df = df.drop_duplicates(subset=['event_id'])
            
            for _, msg in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # 使用格式化的显示名称
                        sender_name = format_user_name(msg['sender'])
                        room_name = format_room_name(msg['room'])
                        st.markdown(f"**{sender_name}** in *{room_name}*")
                        # 使用高亮显示消息内容
                        highlighted_content = highlight_text(msg["content"], search_query)
                        st.markdown(highlighted_content, unsafe_allow_html=True)
                    with col2:
                        # 显示相对时间
                        st.text(get_relative_time(msg["timestamp"]))
                    st.divider()
            
            # 添加加载更多按钮
            loaded_count = len(st.session_state.all_messages)
            if has_more:
                if st.button(f"加载更多消息 ({loaded_count}/{total})"):
                    st.session_state.page += 1
                    st.rerun()
                    
        # 在侧边栏显示统计信息
        with st.sidebar:
            st.metric("消息总数", total)
    else:
        st.error("加载消息失败")

if __name__ == "__main__":
    main()
