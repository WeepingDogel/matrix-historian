"""Multi-pool in-process TTL cache for API endpoints."""

from cachetools import TTLCache

# ─── Cache pools with different TTL strategies ───────────────────────
# Each pool is optimized for a specific data category.

_cache = {
    # Count/metadata: changes infrequently, high reuse
    "count":      TTLCache(maxsize=64,  ttl=300),     # 5 minutes
    # Lists (rooms, users): moderate churn
    "list":       TTLCache(maxsize=128, ttl=180),     # 3 minutes
    # Analytics: aggregation results, slow-changing
    "analytics":  TTLCache(maxsize=256, ttl=900),     # 15 minutes
    # Media metadata: stable after ingest
    "media":      TTLCache(maxsize=64,  ttl=300),     # 5 minutes
    # Avatars: rarely change, long-lived
    "avatar":     TTLCache(maxsize=256, ttl=86400),   # 24 hours
}


def cache_key(*args):
    """Build a cache key from arguments."""
    return ":".join(str(a) for a in args)


def get_cached(pool_name: str, key: str):
    """Get a cached value from the specified pool, or None if not found/expired."""
    pool = _cache.get(pool_name)
    if pool is None:
        return None
    return pool.get(key)


def set_cached(pool_name: str, key: str, data):
    """Store a value in the specified cache pool."""
    pool = _cache.get(pool_name)
    if pool is None:
        return data
    pool[key] = data
    return data


def invalidate_pool(pool_name: str):
    """Clear all cached entries in a pool (e.g., after write operations)."""
    pool = _cache.get(pool_name)
    if pool is not None:
        pool.clear()


def cache_info():
    """Return statistics about all cache pools."""
    info = {}
    for name, pool in _cache.items():
        info[name] = {
            "size": len(pool),
            "maxsize": pool.maxsize,
            "ttl_seconds": pool.ttl,
        }
    return info