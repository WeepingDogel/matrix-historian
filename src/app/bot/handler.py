import simplematrixbotlib as botlib
import asyncio
from app.db.database import SessionLocal
from app.crud import message as crud
import json
import logging
import os
from dotenv import load_dotenv
import backoff  # 需要添加到requirements.txt

logger = logging.getLogger(__name__)
load_dotenv()

class MatrixBot:
    def __init__(self):
        self.homeserver = os.getenv("MATRIX_HOMESERVER")
        self.username = os.getenv("MATRIX_USER")
        if self.username and not self.username.startswith("@"):
            self.username = f"@{self.username}:matrix.org"
        self.password = os.getenv("MATRIX_PASSWORD")

        if not all([self.homeserver, self.username, self.password]):
            raise ValueError("Missing Matrix credentials in .env")
            
        logger.info(f"Initializing bot with user {self.username}")
        self.initialize_bot()
        logger.info("Bot initialized successfully")

    def initialize_bot(self):
        """初始化或重新初始化bot"""
        self.creds = botlib.Creds(
            homeserver=self.homeserver,
            username=self.username,
            password=self.password,
            session_stored_file="bot_session.txt"
        )
        self.config = botlib.Config()
        self.config.encryption_enabled = False
        self.bot = botlib.Bot(self.creds, self.config)
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.listener.on_message_event
        async def handle_message(room, event):
            logger.debug(f"Received message in room {room.room_id}")
            # 忽略机器人自己的消息
            if event.sender == self.creds.username:
                return
                
            try:
                # 只检查消息是否有body属性
                if hasattr(event, 'body') and event.body:
                    with SessionLocal() as db:
                        # 创建或更新用户 - 简单使用用户 ID
                        crud.create_user(
                            db, 
                            event.sender,
                            event.sender.split(':')[0][1:]  # 从 @user:domain.org 提取用户名
                        )
                        
                        # 创建或更新房间
                        crud.create_room(
                            db, 
                            room.room_id,
                            getattr(room, 'name', room.room_id)  # 如果没有名称，使用房间ID
                        )
                        
                        # 保存文本消息
                        crud.create_message(
                            db,
                            event.event_id,
                            room.room_id,
                            event.sender,
                            event.body
                        )
                        logger.info(f"Saved text message from {event.sender} in {room.room_id}")
                    
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}", exc_info=True)

    @backoff.on_exception(
        backoff.expo,
        (asyncio.TimeoutError, ConnectionError),
        max_tries=5,
        max_time=300
    )
    async def try_connect(self):
        """尝试连接到Matrix服务器，带有重试机制"""
        try:
            await self.bot.main()
        except Exception as e:
            logger.error(f"Connection attempt failed: {str(e)}")
            raise

    async def reconnect(self):
        """重新连接到Matrix服务器"""
        logger.info("Attempting to reconnect...")
        try:
            # 重新初始化bot
            self.initialize_bot()
            # 尝试重新连接
            await self.try_connect()
            logger.info("Successfully reconnected")
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {str(e)}")
            return False

    async def start(self):
        """启动bot，包含重试和重连逻辑"""
        while True:
            try:
                logger.info("Starting Matrix bot...")
                await self.try_connect()
                return True
            except (asyncio.TimeoutError, ConnectionError) as e:
                logger.error(f"Connection error: {str(e)}")
                logger.info("Waiting 60 seconds before reconnecting...")
                await asyncio.sleep(60)
                await self.reconnect()
            except Exception as e:
                logger.error(f"Fatal error: {str(e)}", exc_info=True)
                return False

    async def stop(self):
        """停止bot"""
        try:
            if hasattr(self.bot, 'async_client'):
                await self.bot.async_client.close()
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
