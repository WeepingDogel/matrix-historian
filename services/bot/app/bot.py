import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(
    0, "/app/shared"
)  # Still correct, base_app is under shared  # Still correct, base_app is under shared

import backoff  # noqa: E402
import simplematrixbotlib as botlib  # noqa: E402
from base_app.crud import media as crud_media  # noqa: E402
from base_app.crud import message as crud  # noqa: E402
from base_app.db.database import SessionLocal  # noqa: E402
from base_app.storage.minio_client import MediaStorage  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from nio import (  # noqa: E402
    DownloadResponse,
    InviteEvent,
    RoomMessageAudio,
    RoomMessageFile,
    RoomMessageImage,
    RoomMessageVideo,
)

HEALTHCHECK_FILE = Path(os.getenv("HEALTHCHECK_FILE", "/app/data/healthcheck"))

logger = logging.getLogger(__name__)
load_dotenv()


class MatrixBot:
    """
    Matrix Bot for archiving messages to PostgreSQL database.
    Consolidated bot initialization - single source of truth.
    Supports optional end-to-end encryption (E2EE).
    """

    def __init__(self):
        self.homeserver = os.getenv("MATRIX_HOMESERVER")
        self.username = os.getenv("MATRIX_USER")
        if self.username and not self.username.startswith("@"):
            self.username = f"@{self.username}:matrix.org"
        self.password = os.getenv("MATRIX_PASSWORD")
        self.encryption_enabled = (
            os.getenv("MATRIX_ENCRYPTION_ENABLED", "false").lower() == "true"
        )
        self.device_name = os.getenv("MATRIX_DEVICE_NAME", "matrix-historian")

        if not all([self.homeserver, self.username, self.password]):
            raise ValueError("Missing Matrix credentials in environment variables")

        logger.info(f"Initializing bot with user {self.username}")
        if self.encryption_enabled:
            logger.info("E2EE encryption is ENABLED")
        else:
            logger.info("E2EE encryption is DISABLED")
        self.initialize_bot()
        logger.info("Bot initialized successfully")

    def initialize_bot(self):
        """Initialize or reinitialize bot"""
        self.creds = botlib.Creds(
            homeserver=self.homeserver,
            username=self.username,
            password=self.password,
            session_stored_file="/app/data/bot_session.txt",
        )
        self.config = botlib.Config()
        self.config.encryption_enabled = self.encryption_enabled
        # Increase timeout for initial sync (default 65536ms may not be enough
        # when the bot is in many rooms)
        self.config.timeout = int(
            os.getenv("MATRIX_SYNC_TIMEOUT", "300000")
        )  # 5 minutes
        # Persist sync state so restarts only fetch incremental updates
        self.config.store_path = os.getenv("MATRIX_STORE_PATH", "/app/data/nio_store")
        # Set device name for E2EE identification
        if self.encryption_enabled and self.device_name:
            self.config.device_name = self.device_name
        self.bot = botlib.Bot(self.creds, self.config)
        self.setup_handlers()

    def _auto_verify_devices(self) -> None:
        """Auto-trust all known devices for E2EE (Trust On First Use).

        This is called after each sync to ensure the bot can decrypt messages
        from any device its users are on. For session-verified accounts, this
        allows the bot to trust new devices without manual interaction.
        """
        if not self.encryption_enabled:
            return

        client = self.bot.async_client
        if not hasattr(client, "device_store") or not client.device_store:
            logger.debug("No device store available for auto-verify")
            return

        try:
            for user_id, device_dict in client.device_store.items():
                for device_id, device in device_dict.items():
                    if not device.trusted:
                        logger.info(
                            f"Auto-verifying device {device_id} for user {user_id}"
                        )
                        client.verify_device(device)
                        logger.info(
                            f"Device {device_id} for user {user_id} is now trusted"
                        )
            logger.debug("Device auto-verify pass complete")
        except Exception as e:
            logger.warning(f"Error during device auto-verify: {str(e)}", exc_info=True)

    def _setup_encryption_handlers(self) -> None:
        """
        Register callbacks for E2EE-related events:
        - Device verification after each sync
        - Room invitation auto-accept
        """
        if not self.encryption_enabled:
            return

        client = self.bot.async_client

        # Auto-verify devices on each successful sync
        client.add_response_callback(self._auto_verify_devices, "SyncResponse")

        # Register invite handler
        client.add_event_callback(self._handle_invite, InviteEvent)

    async def _handle_invite(self, event: InviteEvent) -> None:
        """Auto-accept room invites so the bot can join encrypted rooms.

        For encrypted rooms, the bot must explicitly join to receive the
        room encryption state and start receiving key shares from other members.
        """
        try:
            room_id = event.source.get("room_id")
            if not room_id:
                logger.warning("Received invite without room_id")
                return

            logger.info(f"Auto-accepting invite to room {room_id}")
            result = await self.bot.async_client.join(room_id)
            if hasattr(result, "room_id") and result.room_id:
                logger.info(f"Successfully joined room {room_id}")
            else:
                logger.warning(
                    f"Failed to join room {room_id}: "
                    f"{getattr(result, 'message', 'unknown error')}"
                )
        except Exception as e:
            logger.error(f"Error handling invite: {str(e)}", exc_info=True)

    async def process_avatar(self, mxc_url: str, entity_type: str, entity_id: str):
        """Download avatar, create thumbnail, upload to MinIO."""
        try:
            media_data = await self.download_matrix_media(mxc_url)
            if not media_data:
                return None

            # Create thumbnail with Pillow
            from io import BytesIO  # noqa: E402

            from PIL import Image  # noqa: E402

            img = Image.open(BytesIO(media_data))
            img.thumbnail((128, 128), Image.LANCZOS)

            # Convert to RGB if necessary (e.g. RGBA PNGs)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            buf = BytesIO()
            img.save(buf, format="JPEG", quality=60, optimize=True)
            thumb_data = buf.getvalue()

            # Upload to MinIO avatars bucket
            import hashlib  # noqa: E402

            id_hash = hashlib.md5(entity_id.encode(), usedforsecurity=False).hexdigest()
            minio_key = f"avatars/{entity_type}/{id_hash}.jpg"

            storage = MediaStorage()
            # bucket is auto-created in MediaStorage.__init__
            storage.client.put_object(
                "matrix-media",
                minio_key,
                BytesIO(thumb_data),
                len(thumb_data),
                content_type="image/jpeg",
            )

            logger.info(
                f"Saved {entity_type} avatar for {entity_id} "
                f"({len(thumb_data)} bytes)"
            )
            return minio_key
        except Exception as e:
            logger.error(f"Error processing avatar: {str(e)}", exc_info=True)
            return None

    async def download_matrix_media(self, mxc_url: str) -> bytes:
        """Download media from Matrix server.

        In encrypted rooms, nio will automatically decrypt the media
        content before returning it in the DownloadResponse.
        """
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

        async def handle_message(room, event):
            logger.debug(f"Received message in room {room.room_id}")

            # Ignore bot's own messages
            if event.sender == self.creds.username:
                return

            # Skip text handler for events already handled as media
            if getattr(event, "_is_media_event", False):
                return

            try:
                with SessionLocal() as db:
                    # Create or update user
                    crud.create_user(
                        db,
                        event.sender,
                        event.sender.split(":")[0][
                            1:
                        ],  # Extract username from @user:domain.org
                    )

                    # Create or update room
                    crud.create_room(
                        db,
                        room.room_id,
                        getattr(room, "name", room.room_id),  # Use room ID if no name
                    )

                    # Check and update user avatar
                    try:
                        user_profile = await self.bot.async_client.get_profile(
                            event.sender
                        )
                        if (
                            hasattr(user_profile, "avatar_url")
                            and user_profile.avatar_url
                        ):
                            db_user = crud.get_user(db, event.sender)
                            if db_user and not db_user.avatar_url:
                                minio_key = await self.process_avatar(
                                    user_profile.avatar_url, "users", event.sender
                                )
                                if minio_key:
                                    crud.update_user_avatar(db, event.sender, minio_key)
                    except Exception as e:
                        logger.debug(f"Could not fetch avatar for {event.sender}: {e}")

                    # Determine if this is a media event
                    is_media = False
                    if hasattr(event, "source"):
                        content = event.source.get("content", {})
                        msgtype = content.get("msgtype")
                        if msgtype in ("m.image", "m.file", "m.audio", "m.video"):
                            is_media = True

                    if is_media:
                        # Handle media messages (image, file, audio, video)
                        mxc_url = content.get("url")
                        if mxc_url:
                            logger.info(f"Processing {msgtype} from {event.sender}")

                            # Extract metadata
                            filename = content.get("body", "unknown")
                            info = content.get("info", {})
                            mime_type = info.get("mimetype", "application/octet-stream")
                            size = info.get("size")
                            width = info.get("w")
                            height = info.get("h")

                            # Save message record (with type prefix)
                            message_body = f"[{msgtype}] {filename}"
                            crud.create_message(
                                db,
                                event.event_id,
                                room.room_id,
                                event.sender,
                                message_body,
                            )

                            # Download media from Matrix
                            media_data = await self.download_matrix_media(mxc_url)

                            if media_data:
                                try:
                                    storage = MediaStorage()
                                    minio_key = storage.upload(
                                        media_data, filename, mime_type
                                    )

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
                                        height=height,
                                    )
                                    logger.info(
                                        f"Saved media {filename} "
                                        f"({mime_type}, {size} bytes) to MinIO"
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Error saving media to MinIO: {str(e)}",
                                        exc_info=True,
                                    )
                            else:
                                logger.warning(
                                    f"Failed to download media from {mxc_url}"
                                )
                    elif hasattr(event, "body") and event.body:
                        # Save text message (only for non-media events)
                        crud.create_message(
                            db,
                            event.event_id,
                            room.room_id,
                            event.sender,
                            event.body,
                        )
                        logger.info(
                            f"Saved text message from {event.sender} in "
                            f"{room.room_id}"
                        )

            except Exception as e:
                logger.error(f"Error handling message: {str(e)}", exc_info=True)

        # Register handle_message for text events (call explicitly instead of
        # using @decorator syntax, because on_message_event returns None which
        # would shadow the function name and break media proxy references).
        self.bot.listener.on_message_event(handle_message)

        # Register listeners for media event types.
        # simplematrixbotlib's on_message_event only captures RoomMessageText,
        # so we use on_custom_event to route media events into the same handler.
        # Use a factory function to avoid Python's closure-over-loop-variable gotcha.
        def _register_media_handler(et):
            @self.bot.listener.on_custom_event(et)
            async def _media_proxy(room, event):
                # Mark the event as already handled so the text handler doesn't
                # fall through and double-save it as text
                event._is_media_event = True
                await handle_message(room, event)

        for event_type in [
            RoomMessageImage,
            RoomMessageFile,
            RoomMessageAudio,
            RoomMessageVideo,
        ]:
            _register_media_handler(event_type)

        # Register E2EE-specific handlers (invites, device auto-verify)
        self._setup_encryption_handlers()

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
        max_time=600,
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
            if hasattr(self.bot, "async_client"):
                await self.bot.async_client.close()
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
