"""Simple in-process TTL cache for analytics endpoints."""
from cachetools import TTLCache

# Max 256 cached results, 15 minute TTL
_cache = TTLCache(maxsize=256, ttl=900)


def cache_key(*args):
    """Build a cache key from arguments."""
    return ":".join(str(a) for a in args)


def get_cached(key):
    """Get a cached value, or None if not found/expired."""
    return _cache.get(key)


def set_cached(key, data):
    """Store a value in cache."""
    _cache[key] = data
    return data
