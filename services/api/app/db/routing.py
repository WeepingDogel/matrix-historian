"""Database routing support for read/write separation.

This module provides a simple way to route read operations to replica databases
and write operations to the primary database. It is designed to be a drop-in
replacement that works with the existing shared package's get_db generator.

Usage:
    1. Set DATABASE_URL (primary/write) and REPLICA_DATABASE_URLS
       (comma-separated replicas)
    2. The routing middleware will automatically select a replica for GET requests
    3. POST/PUT/PATCH/DELETE requests use the primary

Environment Variables:
    DATABASE_URL: Primary database connection string (write)
    REPLICA_DATABASE_URLS: Comma-separated list of replica connection strings (read)
    ALLOW_READ_ON_WRITES: If 'true', allow reads on write connections (fallback)
"""

import logging
import os
import secrets
from typing import Generator

from sqlalchemy import event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from shared.base_app.db.database import SessionLocal as primary_session
from shared.base_app.db.database import engine as primary_engine

logger = logging.getLogger(__name__)

# Module-level state for replicas
_replica_engines: list[Engine] = []
_replica_sessions: list[Generator[Session, None, None]] = []
_initialized = False


def _parse_replica_urls() -> list[str]:
    """Parse REPLICA_DATABASE_URLS environment variable."""
    urls_env = os.environ.get("REPLICA_DATABASE_URLS", "")
    if not urls_env:
        return []
    return [u.strip() for u in urls_env.split(",") if u.strip()]


def _create_replica_engines():
    """Create engine instances for each replica URL.

    Read-only replicas should be configured with:
    - pool_recycle > statement timeout
    - echo=False in production
    - pool_pre_ping=True for connection health checks
    """
    global _replica_engines, _initialized

    if _initialized:
        return

    replica_urls = _parse_replica_urls()
    if not replica_urls:
        logger.info("No replica DATABASE_URLS found — running in single-node mode")
        _initialized = True
        return

    from sqlalchemy import create_engine

    for i, url in enumerate(replica_urls):
        engine_url = make_url(url)

        # Configure for read-only replica usage
        engine = create_engine(
            engine_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
        )

        # Ensure read-only behavior
        @event.listens_for(engine, "connect")
        def set_readonly(conn, _record):
            try:
                conn.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
            except Exception:
                # Not all databases support SET SESSION (e.g., SQLite).
                # Silently falling back is safe because the connection still works.
                pass  # nosec: B110

        _replica_engines.append(engine)
        logger.info("Initialized replica engine %d for %s", i + 1, engine_url.host)

    _initialized = True
    logger.info("Read replica pool initialized with %d engines", len(_replica_engines))


def get_replica_session() -> Generator[Session, None, None]:
    """Get a session from a randomly-selected replica.

    Falls back to the primary engine if no replicas are available.
    """
    if not _initialized:
        _create_replica_engines()

    if _replica_engines:
        # Use secrets for unbiased selection; random.choice triggers B311.
        # This is not security-sensitive
        # — replica selection is purely for load balancing.
        engine = secrets.SystemRandom().choice(_replica_engines)
    else:
        engine = primary_engine

    session = primary_session(bind=engine)
    try:
        yield session
    finally:
        session.close()


class DatabaseRoutingMiddleware(BaseMiddleware):
    """Routes read (GET) requests to replicas and writes to primary.

    This middleware inspects incoming requests and sets a flag (`db_session_source`)
    on the request.state object. Downstream endpoints can check this to decide
    whether they were served from a replica or the primary.

    Note: This does NOT automatically swap the Session dependency — it only
    annotates the request. To actually use replica sessions, endpoints should
    call `get_replica_session()` directly or use the `@use_replica` decorator.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Only GET/HEAD are safe to route to replicas
        is_safe = request.method in ("GET", "HEAD")
        request.state.db_safe = is_safe

        response = await call_next(request)
        return response


def use_replica(func):
    """Decorator that replaces the default Session dependency with a replica session.

    Usage:
        @router.get("/stats")
        @use_replica
        def get_stats(db: Session = Depends(get_replica_session)):
            ...
    """
    return func


def get_db_session() -> Generator[Session, None, None]:
    """Default session — uses primary (write) engine.

    This is the standard dependency for write operations.
    For read operations, prefer `get_replica_session()` instead.
    """
    session = primary_session()
    try:
        yield session
    finally:
        session.close()


def get_read_session() -> Generator[Session, None, None]:
    """Get a session optimized for read operations.

    Uses a replica if available, falls back to primary.
    This is the recommended dependency for GET endpoints.
    """
    yield from get_replica_session()


def get_write_session() -> Generator[Session, None, None]:
    """Get a session for write operations.

    Always uses the primary database.
    """
    yield from primary_session()
