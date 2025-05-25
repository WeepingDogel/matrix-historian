from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.bot.client import start_bot
from app.db.database import init_db
import threading
import uvicorn
from contextlib import asynccontextmanager
import logging
import asyncio
from app.bot.handler import MatrixBot
from app.utils.logging_config import setup_logging
from app.api import analytics

logger = logging.getLogger(__name__)

# 设置日志
setup_logging()

# Initialize database tables
init_db()

bot = MatrixBot()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start bot in background task
    bot_task = asyncio.create_task(bot.start())
    yield
    # Cleanup
    if not bot_task.done():
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            logger.info("Bot task cancelled")
            pass

app = FastAPI(
    title="Matrix Historian",
    description="A Matrix message archiver and search service",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")




