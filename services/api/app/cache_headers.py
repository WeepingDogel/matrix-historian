"""HTTP cache header helpers for browser-side caching."""

from datetime import datetime, timezone
from hashlib import md5
from typing import Any, Dict


def cache_control(max_age: int, public: bool = True) -> Dict[str, str]:
    """Generate Cache-Control header dict."""
    if public:
        directive = f"public, max-age={max_age}"
    else:
        directive = f"no-cache, max-age={max_age}"
    return {"Cache-Control": directive}


def etag_header(data: Any) -> str:
    """Generate an ETag from response data."""
    content = str(data).encode("utf-8")
    return md5(content, usedforsecurity=False).hexdigest()  # noqa: DUO131


def conditional_headers(max_age: int = 300, etag_value: str = "") -> Dict[str, str]:
    """Generate headers for conditional requests."""
    headers = cache_control(max_age)
    if etag_value:
        headers["ETag"] = f'"{etag_value}"'
    headers["Last-Modified"] = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    return headers


# ─── Standard cache durations (seconds) ──────────────────────────────
CACHE_NONE = 0  # No caching
CACHE_IMMEDIATE = 0  # No caching
CACHE_SHORT = 120  # 2 minutes - dynamic lists
CACHE_MEDIUM = 300  # 5 minutes - counts, stats
CACHE_LONG = 900  # 15 minutes - analytics
CACHE_VERY_LONG = 86400  # 24 hours - avatars, static assets
