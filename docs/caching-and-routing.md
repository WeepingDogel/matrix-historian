# Caching & Read/Write Separation

This document describes the caching layer and read/write separation architecture added to Matrix Historian.

## Overview

Matrix Historian now uses a multi-tier caching strategy:

1. **In-memory API cache** — per-service LRU caches with configurable TTLs
2. **Browser/HTTP cache headers** — `Cache-Control` headers on all API responses
3. **SvelteKit `ttl` revalidation** — frontend-side caching with automatic refresh
4. **Read/Write separation** — optional replica routing for read-heavy workloads

No Redis or external cache infrastructure is required.

---

## API In-Memory Cache

### Architecture

The cache system (`services/api/app/cache.py`) uses three independent LRU pools:

| Pool | Purpose | Default Max Size |
|------|---------|-----------------|
| `short` | Ephemeral data (messages, recent activity) | 256 entries |
| `medium` | Semi-stable data (room lists, user lists, counts) | 512 entries |
| `long` | Aggregated data (analytics, stats, room metadata) | 1024 entries |

Each pool has its own eviction policy, so hot short-lived data won't evict long-lived analytics data.

### Cache Keys

Keys are namespaced by pool and resource type:

```python
# Short-term
cache_key("message", "list", room_id="abc123")
cache_key("message", "count")

# Medium-term
cache_key("room", "list")
cache_key("room", "count")
cache_key("user", "list")
cache_key("media", "stats")

# Long-term
cache_key("analytics", "overview", days=7)
cache_key("analytics", "hourly", interval="day", days=7)
cache_key("analytics", "top-rooms", limit=20, days=7)
cache_key("media", "metadata", media_id="xyz789")
```

### Cache Invalidation

When a write operation occurs (new message archived, room created, etc.), the relevant cache keys are automatically invalidated through an HTTP callback from the Bot service to the API service.

#### How It Works

```
Bot writes to PostgreSQL  ──►  Bot calls API cache invalidation endpoint  ──►  API clears relevant cache pools
```

1. **Bot** processes a Matrix event and writes to PostgreSQL
2. **Bot** immediately calls `GET /api/v1/cache/invalidate?resource=<type>` on the API service
3. **API** clears the relevant cache pools (count, list, media, etc.)
4. Next read request will miss the cache and fetch fresh data from the database

#### Invalidated Resources

| Bot Write Event | Cache Resource Invalidated |
|----------------|---------------------------|
| New user created/updated | `user` (count + list pools) |
| New room created/updated | `room` (count + list pools) |
| New text message archived | `message` (count + list pools) |
| New media message archived | `media` (media pool) |

#### Configuration

Set `API_CACHE_INVALIDATE_URL` in the bot environment:

```bash
API_CACHE_INVALIDATE_URL=http://api:8500/api/v1/cache/invalidate
```

The invalidation request uses a 2-second timeout and is fire-and-forget — if the API is temporarily unavailable, the next TTL expiration will handle cache refresh.

#### Programmatic Invalidation

You can also invalidate caches directly in Python:

```python
from cache import invalidate_by_resource

# Invalidate all message-related caches
invalidate_by_resource("message")

# Invalidate all caches
invalidate_by_resource("all")
```

Or via the API endpoint:

```bash
curl -X POST "http://localhost:8500/api/v1/cache/invalidate?resource=message"
```

---

## HTTP Cache Headers

### Cache-Control Levels

The `cache_headers.py` module defines three standard levels:

| Level | Header Value | Use Case |
|-------|-------------|----------|
| `CACHE_NONE` | `no-store, no-cache, must-revalidate, max-age=0` | Highly dynamic data (message list, search) |
| `CACHE_SHORT` | `public, max-age=60, s-maxage=60, stale-while-revalidate=30` | Metadata, presigned URLs (1 min) |
| `CACHE_MEDIUM` | `public, max-age=300, s-maxage=300, stale-while-revalidate=120` | Counts, stats, room/user lists (5 min) |
| `CACHE_LONG` | `public, max-age=900, s-maxage=900, stale-while-revalidate=300` | Analytics, aggregated data (15 min) |

### Endpoint Behavior

| Endpoint Group | Default Cache | Notes |
|---------------|--------------|-------|
| `/api/v1/messages/` | `CACHE_NONE` | Real-time message list |
| `/api/v1/messages/count` | `CACHE_MEDIUM` | Count changes infrequently |
| `/api/v1/rooms/` | `CACHE_MEDIUM` | Room list is semi-stable |
| `/api/v1/rooms/count` | `CACHE_MEDIUM` | Room count rarely changes |
| `/api/v1/users/` | `CACHE_MEDIUM` | User list is semi-stable |
| `/api/v1/users/count` | `CACHE_MEDIUM` | User count rarely changes |
| `/api/v1/search/` | `CACHE_NONE` | Search results are dynamic |
| `/api/v1/analytics/*` | `CACHE_LONG` | Aggregated data changes slowly |
| `/api/v1/media/stats` | `CACHE_MEDIUM` | Media stats are stable |
| `/api/v1/media/{id}` | `CACHE_SHORT` | Presigned URLs expire quickly |

### Custom Cache Control

Endpoints can override the default by setting `request.state.cache_control`:

```python
from cache_headers import CACHE_LONG

@app.get("/custom-endpoint")
def custom_endpoint(request: Request):
    request.state.cache_control = CACHE_LONG
    return {"data": "..."}
```

---

## SvelteKit Frontend Caching

### `next: { ttl }` Option

SvelteKit's server-side `fetch` supports a `ttl` (time-to-live) option that controls how long the rendered page is cached before revalidation:

```javascript
// Cache for 5 minutes (300000 ms)
const res = await fetch('/api/v1/rooms/count', { next: { ttl: 300000 } });
```

### Page-Level Cache Strategy

| Page | Data | TTL | Rationale |
|------|------|-----|-----------|
| Home (`/`) | Counts | 5 min | Stable counters |
| Home (`/`) | Recent messages | 1 min | Recent data is somewhat dynamic |
| Home (`/`) | Rooms/Users list | 3 min | Semi-stable |
| Home (`/`) | Analytics overview | 15 min | Aggregated data changes slowly |
| Rooms (`/rooms`) | List | 3 min | Room list is stable |
| Rooms (`/rooms`) | Count | 5 min | Rarely changes |
| Users (`/users`) | List | 3 min | User list is stable |
| Users (`/users`) | Count | 5 min | Rarely changes |
| Messages (`/messages`) | List | No cache | Highly dynamic |
| Messages (`/messages`) | Search | No cache | Real-time search |
| Analytics (`/analytics`) | All | 10-15 min | Aggregated data |

### Search Pages

Search endpoints intentionally do not use SvelteKit caching because search results depend on the query string and should reflect the latest data:

```javascript
// Search results — always fresh
const res = await fetch(`/api/v1/search/?query=${q}`);
```

---

## Read/Write Separation

### Architecture

The `db/routing.py` module provides optional read/write splitting:

```
                    ┌──────────────┐
        Writes ────►│  Primary DB   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
        Reads ──────┤  Replica DB   │◄── Optional (comma-separated)
                    └──────────────┘
```

### Configuration

Set the following environment variables:

```bash
# Primary database (required, used for writes)
DATABASE_URL=postgresql://user:pass@primary:5432/historian  # pragma: allowlist secret

# Read replicas (optional, comma-separated)
REPLICA_DATABASE_URLS=postgresql://user:pass@replica1:5432/historian,postgresql://user:pass@replica2:5432/historian  # pragma: allowlist secret
```

If `REPLICA_DATABASE_URLS` is not set, all requests use the primary database (single-node mode).

### How It Works

1. **`DatabaseRoutingMiddleware`** annotates each request with `request.state.db_safe` based on HTTP method.
2. **`get_read_session()`** selects a random replica engine if available, falling back to primary.
3. **`get_write_session()`** always uses the primary engine.
4. Each replica connection sets `SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY` on connect.

### Using Read Sessions in Endpoints

Replace the default `Depends(get_db)` with `Depends(get_read_session)` for read-only endpoints:

```python
from db.routing import get_read_session

@router.get("/stats")
def get_stats(db: Session = Depends(get_read_session)):
    ...
```

For write endpoints, keep using the default `Depends(get_db)`:

```python
from base_app.db.database import get_db

@router.post("/rooms")
def create_room(db: Session = Depends(get_db)):
    ...
```

### When to Enable Read/Write Separation

Enable this when:
- You have multiple PostgreSQL replicas configured
- Read traffic significantly exceeds write traffic
- Analytics queries are heavy and compete with user-facing reads

Do NOT enable this when:
- You run a single-node deployment
- Write traffic is high and would benefit from direct primary access
- Replication lag is unacceptable for your use case

---

## Performance Considerations

### Memory Usage

Each API service instance maintains its own in-memory cache. For a horizontally-scaled deployment:

- Each pod/container will have independent cache state
- This is fine for self-hosted deployments with 1-3 API instances
- For larger deployments, consider moving to a shared cache (Redis/Memcached)

### Cache Hit Ratio

Typical cache hit ratios expected:

| Data Type | Expected Hit Ratio | Reason |
|-----------|-------------------|---------|
| Counts | 80-95% | Change infrequently |
| Room/User lists | 60-80% | Stable unless rooms/users are added frequently |
| Analytics | 70-90% | Aggregated over time windows |
| Message lists | 10-30% | Highly dynamic |
| Search | <5% | Unique queries |

### Eviction Strategy

LRU (Least Recently Used) eviction means:
- Hot data stays cached
- Cold data is automatically removed
- Each pool has independent limits to prevent one data type from starving another

---

## Monitoring

### Cache Statistics

You can inspect cache statistics at runtime:

```python
from cache import get_cache_stats

stats = get_cache_stats()
# {
#     "short": {"size": 42, "max_size": 256, "hits": 100, "misses": 50},
#     "medium": {"size": 128, "max_size": 512, "hits": 500, "misses": 100},
#     "long": {"size": 256, "max_size": 1024, "hits": 2000, "misses": 300}
# }
```

### Logging

The cache module logs hits and misses at DEBUG level. Enable debug logging to track cache performance:

```yaml
# docker-compose.yml
services:
  api:
    environment:
      LOG_LEVEL: debug
```

### Health Check

Add a `/cache/stats` endpoint to expose cache metrics:

```python
@router.get("/cache/stats")
def cache_stats():
    return get_cache_stats()
```

---

## Future Enhancements

1. **Cache invalidation webhook** — Bot service notifies API when new events are archived
2. **Distributed cache** — Move to Redis/Memcached for multi-instance deployments
3. **Query result caching** — Auto-cache SQL query results with TTL
4. **CDN integration** — Put CloudFlare/Nginx in front for additional caching
5. **Stale-while-revalidate UI** — Show stale data while refreshing in the background
6. **Cache warming** — Pre-populate caches on startup for critical endpoints