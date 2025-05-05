import simplematrixbotlib as botlib
import asyncio
from app.db.database import SessionLocal
from app.crud import message as crud
import json
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class MatrixBot:
    def __init__(self):
        homeserver = os.getenv("MATRIX_HOMESERVER")
        username = os.getenv("MATRIX_USER")
        if username and not username.startswith("@"):
            username = f"@{username}:matrix.org"
        password = os.getenv("MATRIX_PASSWORD")

        if not all([homeserver, username, password]):
            raise ValueError("Missing Matrix credentials in .env")
            
        logger.info(f"Initializing bot with user {username}")
        self.creds = botlib.Creds(
            homeserver=homeserver,
            username=username,
            password=password,
            session_stored_file="bot_session.txt"
        )
        self.config = botlib.Config()
        self.config.encryption_enabled = False  # 禁用加密以简化测试
        self.bot = botlib.Bot(self.creds, self.config)
        self.setup_handlers()
        logger.info("Bot initialized successfully")

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
                        # 创建或更新用户
                        crud.create_user(
                            db, 
                            event.sender,
                            None
                        )
                        
                        # 创建或更新房间
                        crud.create_room(
                            db, 
                            room.room_id,
                            None
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

    async def start(self):
        try:
            logger.info("Starting Matrix bot...")
            logger.info(f"Using credentials for user: {self.creds.username}")
            await self.bot.main()
            return True
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}", exc_info=True)
            return False

    async def stop(self):
        pass  # simplematrixbotlib handles cleanup automatically
