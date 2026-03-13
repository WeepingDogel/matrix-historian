import asyncio
import logging
import sys

sys.path.insert(
    0, "/app/shared"
)  # Still correct, base_app is under shared  # Still correct, base_app is under shared

from base_app.db.database import init_db  # noqa: E402
from base_app.utils.logging_config import setup_logging  # noqa: E402
from bot import MatrixBot  # noqa: E402

logger = logging.getLogger(__name__)

# Setup logging
setup_logging()

# Initialize database tables
logger.info("Initializing database...")
init_db()
logger.info("Database initialized")


async def main():
    """Main entry point for the bot service"""
    bot = MatrixBot()
    await bot.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
