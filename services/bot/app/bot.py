import simplematrixbotlib as botlib
import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import backoff
from nio import (
    DownloadResponse,
    RoomMessageImage,
    RoomMessageFile,
    RoomMessageAudio,
    RoomMessageVideo,
)

HEALTHCHECK_FILE = Path(os.getenv("HEALTHCHECK_FILE", "/app/healthcheck"))

# Import from shared package
import sys
sys.path.insert(0, '/app/shared')
from app.db.database import SessionLocal
from app.crud import message as crud
from app.crud import media as crud_media
from app.storage.minio_client import MediaStorage

logger = logging.getLogger(__name__)
load_dotenv()


class MatrixBot:
    """
    Matrix Bot for archiving messages to PostgreSQL database.
    Consolidated bot initialization - single source of truth.
    """
    
    def __init__(self):
        self.homeserver = os.getenv("MATRIX_HOMESERVER")
        self.username = os.getenv("MATRIX_USER")
        if self.username and not self.username.startswith("@"):
            self.username = f"@{self.username}:matrix.org"
        self.password = os.getenv("MATRIX_PASSWORD")

        if not all([self.homeserver, self.username, self.password]):
            raise ValueError("Missing Matrix credentials in environment variables")
            
        logger.info(f"Initializing bot with user {self.username}")
        self.initialize_bot()
        logger.info("Bot initialized successfully")

    def initialize_bot(self):
        """Initialize or reinitialize bot"""
        self.creds = botlib.Creds(
            homeserver=self.homeserver,
            username=self.username,
            password=self.password,
            session_stored_file="bot_session.txt"
        )
        self.config = botlib.Config()
        self.config.encryption_enabled = False
        # Increase timeout for initial sync (default 65536ms may not be enough
        # when the bot is in many rooms)
        self.config.timeout = int(os.getenv("MATRIX_SYNC_TIMEOUT", "300000"))  # 5 minutes
        # Persist sync state so restarts only fetch incremental updates
        self.config.store_path = os.getenv("MATRIX_STORE_PATH", "/app/nio_store")
        self.bot = botlib.Bot(self.creds, self.config)
        self.setup_handlers()

    async def download_matrix_media(self, mxc_url: str) -> bytes:
        """Download media from Matrix server"""
        try:
            logger.debug(f"Downloading media from {mxc_url}")
            response = await self.bot.async_client.download(mxc_url)
            if isinstance(response, DownloadResponse):
                logger.debug(f"Downloaded {len(response.body)} bytes")
                return response.body
            else:
                logger.error(f"Failed to download media: {response}")
                return None
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}", exc_info=True)
            return None

    def setup_handlers(self):
        """Setup message event handlers"""
        @self.bot.listener.on_message_event
        async def handle_message(room, event):
            logger.debug(f"Received message in room {room.room_id}")
            
            # Ignore bot's own messages
            if event.sender == self.creds.username:
                return
                
            try:
                with SessionLocal() as db:
                    # Create or update user
                    crud.create_user(
                        db, 
                        event.sender,
                        event.sender.split(':')[0][1:]  # Extract username from @user:domain.org
                    )
                    
                    # Create or update room
                    crud.create_room(
                        db, 
                        room.room_id,
                        getattr(room, 'name', room.room_id)  # Use room ID if no name
                    )
                    
                    # Determine if this is a media event
                    is_media = False
                    if hasattr(event, 'source'):
                        content = event.source.get('content', {})
                        msgtype = content.get('msgtype')
                        if msgtype in ('m.image', 'm.file', 'm.audio', 'm.video'):
                            is_media = True
                    
                    if is_media:
                        # Handle media messages (image, file, audio, video)
                        mxc_url = content.get('url')
                        if mxc_url:
                            logger.info(f"Processing {msgtype} from {event.sender}")
                            
                            # Extract metadata
                            filename = content.get('body', 'unknown')
                            info = content.get('info', {})
                            mime_type = info.get('mimetype', 'application/octet-stream')
                            size = info.get('size')
                            width = info.get('w')
                            height = info.get('h')
                            
                            # Save message record (with type prefix)
                            message_body = f'[{msgtype}] {filename}'
                            crud.create_message(
                                db,
                                event.event_id,
                                room.room_id,
                                event.sender,
                                message_body
                            )
                            
                            # Download media from Matrix
                            media_data = await self.download_matrix_media(mxc_url)
                            
                            if media_data:
                                try:
                                    storage = MediaStorage()
                                    minio_key = storage.upload(media_data, filename, mime_type)
                                    
                                    # Save media metadata
                                    crud_media.create_media(
                                        db,
                                        event_id=event.event_id,
                                        room_id=room.room_id,
                                        sender_id=event.sender,
                                        minio_key=minio_key,
                                        original_filename=filename,
                                        mime_type=mime_type,
                                        size=size,
                                        width=width,
                                        height=height
                                    )
                                    logger.info(f"Saved media {filename} ({mime_type}, {size} bytes) to MinIO")
                                except Exception as e:
                                    logger.error(f"Error saving media to MinIO: {str(e)}", exc_info=True)
                            else:
                                logger.warning(f"Failed to download media from {mxc_url}")
                    elif hasattr(event, 'body') and event.body:
                        # Save text message (only for non-media events)
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

        # Register listeners for media event types.
        # simplematrixbotlib's on_message_event only captures RoomMessageText,
        # so we use on_custom_event to route media events into the same handler.
        for event_type in [RoomMessageImage, RoomMessageFile,
                           RoomMessageAudio, RoomMessageVideo]:
            @self.bot.listener.on_custom_event(event_type)
            async def _media_proxy(room, event):
                await handle_message(room, event)

    async def _heartbeat_loop(self):
        """Periodically touch healthcheck file to signal the bot is alive.
        
        Docker healthcheck verifies this file was modified recently.
        If the bot hangs (e.g. event loop blocked), the file goes stale
        and Docker marks the container as unhealthy.
        """
        logger.info(f"Heartbeat loop started (file: {HEALTHCHECK_FILE})")
        while True:
            try:
                HEALTHCHECK_FILE.touch()
            except Exception as e:
                logger.warning(f"Failed to touch healthcheck file: {e}")
            await asyncio.sleep(30)

    @backoff.on_exception(
        backoff.expo,
        (asyncio.TimeoutError, ConnectionError, OSError),
        max_tries=10,
        max_time=600
    )
    async def try_connect(self):
        """Attempt to connect to Matrix server with retry mechanism"""
        try:
            await self.bot.main()
        except Exception as e:
            logger.error(f"Connection attempt failed: {str(e)}")
            raise

    async def reconnect(self):
        """Reconnect to Matrix server"""
        logger.info("Attempting to reconnect...")
        try:
            # Close old client session to avoid 'Unclosed client session' warning
            await self.stop()
            self.initialize_bot()
            await self.try_connect()
            logger.info("Successfully reconnected")
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {str(e)}")
            return False

    async def start(self):
        """Start bot with retry, reconnection logic, and heartbeat."""
        # Start heartbeat in background
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        while True:
            try:
                logger.info("Starting Matrix bot...")
                await self.try_connect()
                heartbeat_task.cancel()
                return True
            except (asyncio.TimeoutError, ConnectionError) as e:
                logger.error(f"Connection error: {str(e)}")
                logger.info("Waiting 60 seconds before reconnecting...")
                await asyncio.sleep(60)
                await self.reconnect()
            except Exception as e:
                logger.error(f"Fatal error: {str(e)}", exc_info=True)
                heartbeat_task.cancel()
                return False

    async def stop(self):
        """Stop bot"""
        try:
            if hasattr(self.bot, 'async_client'):
                await self.bot.async_client.close()
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
