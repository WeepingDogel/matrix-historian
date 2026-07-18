import logging
import sys

sys.path.insert(
    0, "/app/shared"
)  # Still correct, base_app is under shared  # Still correct, base_app is under shared

from api import analytics, media  # noqa: E402
from api.routes import router  # noqa: E402
from base_app.db.database import init_db  # noqa: E402
from base_app.utils.logging_config import setup_logging  # noqa: E402
from cache_headers import CACHE_NONE  # noqa: E402
from db.routing import DatabaseRoutingMiddleware  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from starlette.middleware.base import BaseMiddleware  # noqa: E402
from starlette.responses import Response  # noqa: E402

logger = logging.getLogger(__name__)

# Setup logging
setup_logging()

# Initialize database tables
logger.info("Initializing database...")
init_db()
logger.info("Database initialized")

app = FastAPI(
    title="Matrix Historian API",
    description="A Matrix message archiver and analytics service",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database routing middleware — annotates requests for read/write splitting
app.add_middleware(DatabaseRoutingMiddleware)

# Cache-Control header middleware — adds browser-cache headers to all responses
# Endpoints can set request.state.cache_control to override the default (CACHE_NONE)
class CacheControlMiddleware(BaseMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        cache_setting = getattr(request.state, "cache_control", CACHE_NONE)
        if cache_setting:
            if callable(cache_setting):
                headers = cache_setting()
            else:
                headers = cache_setting
            for key, value in headers.items():
                response.headers[key] = value
        return response

app.add_middleware(CacheControlMiddleware)

# Include routers
app.include_router(router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api"}


if __name__ == "__main__":
    import os

    import uvicorn  # noqa: E402

    # Use environment variable for host, default to localhost for security
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(app, host=host, port=port)
