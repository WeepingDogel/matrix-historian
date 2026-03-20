"""
One-time script to backfill avatars for existing users.
Run inside the bot container:
  docker cp scripts/backfill_avatars.py matrix-historian-bot-production:/tmp/
  docker exec -it matrix-historian-bot-production python /tmp/backfill_avatars.py
"""

import asyncio
import hashlib
import logging
import os
import sys
from io import BytesIO

sys.path.insert(0, "/app/shared")

from base_app.crud.message import update_user_avatar  # noqa: E402
from base_app.db.database import SessionLocal  # noqa: E402
from base_app.models.message import User  # noqa: E402
from base_app.storage.minio_client import MediaStorage  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backfill_avatars")


async def main():
    from nio import AsyncClient

    homeserver = os.getenv("MATRIX_HOMESERVER")
    username = os.getenv("MATRIX_USER")
    password = os.getenv("MATRIX_PASSWORD")

    if not all([homeserver, username, password]):
        logger.error("Missing MATRIX_HOMESERVER, MATRIX_USER, or MATRIX_PASSWORD")
        return

    if username and not username.startswith("@"):
        username = f"@{username}:matrix.org"

    client = AsyncClient(homeserver, username)
    login_resp = await client.login(password)
    logger.info(f"Logged in: {login_resp}")

    storage = MediaStorage()

    with SessionLocal() as db:
        users = db.query(User).filter(User.avatar_url.is_(None)).all()
        logger.info(f"Found {len(users)} users without avatars")

        success = 0
        for user in users:
            try:
                profile = await client.get_profile(user.user_id)
                if not hasattr(profile, "avatar_url") or not profile.avatar_url:
                    continue

                # Download avatar
                from nio import DownloadResponse

                resp = await client.download(profile.avatar_url)
                if not isinstance(resp, DownloadResponse):
                    continue

                # Thumbnail with Pillow
                from PIL import Image

                img = Image.open(BytesIO(resp.body))
                img.thumbnail((128, 128), Image.LANCZOS)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                buf = BytesIO()
                img.save(buf, format="JPEG", quality=60, optimize=True)
                thumb_data = buf.getvalue()

                # Upload to MinIO
                id_hash = hashlib.md5(
                    user.user_id.encode(), usedforsecurity=False
                ).hexdigest()
                minio_key = f"avatars/users/{id_hash}.jpg"
                # bucket is auto-created in MediaStorage.__init__
                storage.client.put_object(
                    "matrix-media",
                    minio_key,
                    BytesIO(thumb_data),
                    len(thumb_data),
                    content_type="image/jpeg",
                )

                update_user_avatar(db, user.user_id, minio_key)
                success += 1
                logger.info(f"[{success}] {user.user_id} -> {minio_key}")

            except Exception as e:
                logger.warning(f"Failed for {user.user_id}: {e}")

    await client.close()
    logger.info(f"Done! {success}/{len(users)} avatars backfilled")


if __name__ == "__main__":
    asyncio.run(main())
