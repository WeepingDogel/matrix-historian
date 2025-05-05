import simplematrixbotlib as botlib
import os
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_homeserver_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def init_bot():
    load_dotenv()
    
    homeserver = os.getenv("MATRIX_HOMESERVER")
    user = os.getenv("MATRIX_USER")
    password = os.getenv("MATRIX_PASSWORD")
    
    if not all([homeserver, user, password]):
        raise ValueError("Missing required Matrix configuration in .env file")
    
    if not validate_homeserver_url(homeserver):
        raise ValueError(f"Invalid Matrix homeserver URL: {homeserver}")
    
    creds = botlib.Creds(homeserver, user, password)
    config = botlib.Config()
    return botlib.Bot(creds, config)

bot = None
historian = None

async def start_bot():
    try:
        global bot, historian
        bot = init_bot()
        
        from .handler import MatrixHistorian
        historian = MatrixHistorian(bot)
        
        @bot.listener.on_message_event
        async def handle_message(room, event):
            await historian.handle_message(room, event)
            
        logger.info("Starting Matrix bot...")
        await bot.run()  # 直接使用 bot.run() 处理登录和同步
    except Exception as e:
        logger.error(f"Failed to start Matrix bot: {str(e)}")
        return False
    return True

async def stop_bot():
    # simplematrixbotlib 会自动处理清理工作
    pass
