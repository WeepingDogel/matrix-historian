import logging
import sys

sys.path.insert(0, "/app/shared")

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from api import analytics, media  # noqa: E402
from api.routes import router  # noqa: E402
from app.db.database import init_db  # noqa: E402
from app.utils.logging_config import setup_logging  # noqa: E402

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

# Include routers
app.include_router(router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api"}


if __name__ == "__main__":
    import uvicorn  # noqa: E402

    uvicorn.run(app, host="0.0.0.0", port=8000)
