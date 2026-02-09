# API Reference

## Base URL
All endpoints are prefixed with `/api/v1`.

## Endpoints

### GET /messages/
- Description: Retrieve a list of messages.
- Parameters:
  - room_id (optional): Filter by room ID. Example: `!roomid:matrix.org`
  - user_id (optional): Filter by user ID. Example: `@user:matrix.org`
  - after (optional): ISO datetime to filter messages after. Example: `2024-01-01T00:00:00Z`
  - skip (optional): Offset for pagination (default is 0). Example: `0`
  - limit (optional): Maximum number of records (default is 100). Example: `50`
- Request Example:
  ```
  /api/v1/messages/?room_id=!roomid:matrix.org&user_id=@user:matrix.org&skip=0&limit=50
  ```
- Response Example:
  ```json
  {
    "messages": [
      {
        "event_id": "$eventid",
        "room_id": "!roomid:matrix.org",
        "sender_id": "@user:matrix.org",
        "content": "Hello, world!",
        "timestamp": "2024-01-01T00:00:00Z",
        "room": {"room_id": "!roomid:matrix.org", "name": "Room Name"},
        "sender": {"user_id": "@user:matrix.org", "display_name": "User Display Name"}
      }
    ],
    "total": 100,
    "has_more": true,
    "next_skip": 50
  }
  ```

### GET /messages/{event_id}
- Description: Retrieve a specific message by its event ID.
- Parameter:
  - event_id: Unique identifier of the message. Example: `$eventid`
- Request Example:
  ```
  /api/v1/messages/$eventid
  ```
- Response Example:
  ```json
  {
    "event_id": "$eventid",
    "room_id": "!roomid:matrix.org",
    "sender_id": "@user:matrix.org",
    "content": "Hello, world!",
    "timestamp": "2024-01-01T00:00:00Z",
    "room": {"room_id": "!roomid:matrix.org", "name": "Room Name"},
    "sender": {"user_id": "@user:matrix.org", "display_name": "User Display Name"}
  }
  ```

### GET /messages/count
- Description: Get the total count of messages, supports filters.
- Parameters:
  - room_id (optional): Example: `!roomid:matrix.org`
  - user_id (optional): Example: `@user:matrix.org`
  - query (optional): Search string. Example: `hello`
- Request Example:
  ```
  /api/v1/messages/count?room_id=!roomid:matrix.org&user_id=@user:matrix.org&query=hello
  ```
- Response Example:
  ```json
  {
    "total": 10
  }
  ```

### GET /rooms/{room_id}/messages
- Description: Retrieve messages from a specific room.
- Parameter:
  - room_id: Room identifier. Example: `!roomid:matrix.org`
- Request Example:
  ```
  /api/v1/rooms/!roomid:matrix.org/messages
  ```
- Response Example:
  ```json
  [
    {
      "event_id": "$eventid",
      "room_id": "!roomid:matrix.org",
      "sender_id": "@user:matrix.org",
      "content": "Hello, world!",
      "timestamp": "2024-01-01T00:00:00Z",
      "room": {"room_id": "!roomid:matrix.org", "name": "Room Name"},
      "sender": {"user_id": "@user:matrix.org", "display_name": "User Display Name"}
    }
  ]
  ```

### GET /users/{user_id}/messages
- Description: Retrieve messages sent by a specific user.
- Parameter:
  - user_id: User identifier. Example: `@user:matrix.org`
- Request Example:
  ```
  /api/v1/users/@user:matrix.org/messages
  ```
- Response Example:
  ```json
  [
    {
      "event_id": "$eventid",
      "room_id": "!roomid:matrix.org",
      "sender_id": "@user:matrix.org",
      "content": "Hello, world!",
      "timestamp": "2024-01-01T00:00:00Z",
      "room": {"room_id": "!roomid:matrix.org", "name": "Room Name"},
      "sender": {"user_id": "@user:matrix.org", "display_name": "User Display Name"}
    }
  ]
  ```

### GET /search/
- Description: Search messages by content.
- Parameters:
  - query (required): Search keyword. Example: `hello`
  - room_id (optional): Example: `!roomid:matrix.org`
  - user_id (optional): Example: `@user:matrix.org`
  - skip (optional): Example: `0`
  - limit (optional): Example: `50`
- Request Example:
  ```
  /api/v1/search/?query=hello&room_id=!roomid:matrix.org&user_id=@user:matrix.org&skip=0&limit=50
  ```
- Response Example:
  ```json
  {
    "messages": [
      {
        "event_id": "$eventid",
        "room_id": "!roomid:matrix.org",
        "sender_id": "@user:matrix.org",
        "content": "Hello, world!",
        "timestamp": "2024-01-01T00:00:00Z",
        "room": {"room_id": "!roomid:matrix.org", "name": "Room Name"},
        "sender": {"user_id": "@user:matrix.org", "display_name": "User Display Name"}
      }
    ],
    "total": 10,
    "has_more": false,
    "next_skip": null
  }
  ```

### GET /users/
- Description: Retrieve the list of users.
- Request Example:
  ```
  /api/v1/users/
  ```
- Response Example:
  ```json
  [
    {"user_id": "@user1:matrix.org", "display_name": "User 1"},
    {"user_id": "@user2:matrix.org", "display_name": "User 2"}
  ]
  ```

### GET /users/search/
- Description: Search users by keyword.
- Parameters:
  - query (required): Search keyword. Example: `alice`
  - skip (optional): Example: `0`
  - limit (optional): Example: `50`
- Request Example:
  ```
  /api/v1/users/search/?query=alice&skip=0&limit=50
  ```
- Response Example:
  ```json
  [
    {"user_id": "@alice:matrix.org", "display_name": "Alice"}
  ]
  ```

### GET /rooms/
- Description: Retrieve the list of rooms.
- Request Example:
  ```
  /api/v1/rooms/
  ```
- Response Example:
  ```json
  [
    {"room_id": "!room1:matrix.org", "name": "Room 1"},
    {"room_id": "!room2:matrix.org", "name": "Room 2"}
  ]
  ```

### GET /health
- Description: Health check endpoint.
- Request Example:
  ```
  /api/v1/health
  ```
- Response Example:
  ```json
  {"status": "healthy"}
  ```

## Analytics API Endpoints

### GET /api/v1/analytics/overview
- Description: Get analytics overview including message stats and user activity.
- Parameters:
  - days (optional): Number of days to analyze. Default: 7
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "message_stats": [
      {"date": "2024-01-01", "count": 150}
    ],
    "user_activity": [
      {
        "user": {
          "user_id": "@user:matrix.org",
          "display_name": "User Name"
        },
        "message_count": 42
      }
    ],
    "cache_info": {
      "cache_time": "20240101",
      "expires_in": "1 hour"
    }
  }
  ```

### GET /api/v1/analytics/message-stats
- Description: Get daily message counts for the given period.
- Parameters:
  - days (optional): Number of days to analyze. Default: 7
- Response Example:
  ```json
  {"stats": [{"date": "2024-01-01", "count": 150}]}
  ```

### GET /api/v1/analytics/user-activity
- Description: Top user activity by message count.
- Parameters:
  - limit (optional): Number of users to return. Default: 10
- Response Example:
  ```json
  {"users": [{"user": "@user:matrix.org", "display_name": "User Name", "message_count": 42}]}
  ```

### GET /api/v1/analytics/room-activity
- Description: Top room activity by message count.
- Parameters:
  - limit (optional): Number of rooms to return. Default: 10
- Response Example:
  ```json
  {"rooms": [{"room": "!room:matrix.org", "name": "Room Name", "message_count": 120}]}
  ```

### GET /api/v1/analytics/wordcloud
- Description: Generate word frequency data for word cloud visualization.
- Parameters:
  - days (optional): Number of days. Default: 7
  - limit (optional): Maximum number of words. Default: 50
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "messages": [
      {"word": "hello", "count": 42},
      {"word": "matrix", "count": 28}
    ]
  }
  ```

### GET /api/v1/analytics/user-network
- Description: Get user interaction network data.
- Parameters:
  - days (optional): Number of days. Default: 7
  - min_weight (optional): Minimum interaction weight. Default: 3
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "nodes": [
      {"id": "@user1:matrix.org"},
      {"id": "@user2:matrix.org"}
    ],
    "edges": [
      {
        "source": "@user1:matrix.org",
        "target": "@user2:matrix.org",
        "weight": 5
      }
    ]
  }
  ```

### GET /api/v1/analytics/interactions
- Description: Get user interaction pairs with counts.
- Parameters:
  - days (optional): Number of days. Default: 7
  - min_count (optional): Minimum interaction count. Default: 3
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {"interactions": [["@user1:matrix.org", "@user2:matrix.org", 5]]}
  ```

### GET /api/v1/analytics/sentiment
- Description: Analyze sentiment of messages using AI.
- Parameters:
  - days (optional): Number of days. Default: 7
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "sentiment": "positive",
    "confidence": 0.85,
    "analysis": "Generally positive discussions",
    "model": "llama-3.1-8b-instant"
  }
  ```

### GET /api/v1/analytics/trends
- Description: Message trends aggregated by interval.
- Parameters:
  - days (optional): Number of days. Default: 7
  - interval (optional): Aggregation interval. One of: hour/day/week. Default: day
- Response Example:
  ```json
  {"trends": [["2024-01-01", 100]]}
  ```

### GET /api/v1/analytics/activity-heatmap
- Description: Get activity heatmap data by hour and weekday. The heatmap is a 7x24 matrix where rows represent weekdays (0=Monday, 6=Sunday) and columns represent hours (0-23).
- Parameters:
  - days (optional): Number of days to analyze. Default: 7
  - room_id (optional): Filter by room ID
- Request Example:
  ```
  /api/v1/analytics/activity-heatmap?days=7&room_id=!roomid:matrix.org
  ```
- Response Example:
  ```json
  {
    "heatmap": [
      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
      [0, 0, 0, 0, 0, 0, 1, 5, 10, 15, 20, 25, 30, 25, 20, 15, 10, 5, 3, 2, 1, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 2, 8, 15, 20, 25, 30, 35, 30, 25, 20, 15, 8, 5, 3, 2, 1, 0, 0],
      [0, 0, 0, 0, 0, 0, 1, 6, 12, 18, 22, 28, 32, 28, 22, 18, 12, 6, 4, 2, 1, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 3, 10, 18, 25, 30, 35, 40, 35, 30, 25, 18, 10, 6, 4, 2, 1, 0, 0],
      [0, 0, 0, 0, 0, 0, 5, 15, 25, 35, 40, 45, 50, 45, 40, 35, 25, 15, 10, 5, 3, 2, 0, 0],
      [0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 45, 50, 55, 50, 45, 40, 30, 20, 15, 10, 5, 3, 0, 0]
    ],
    "weekdays": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
    "hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
  }
  ```
- Notes:
  - The heatmap matrix has 7 rows (one for each weekday) and 24 columns (one for each hour)
  - Values represent message counts for that weekday-hour combination
  - Weekdays are in Chinese by default: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

### GET /api/v1/analytics/topic-evolution
- Description: Analyze topic evolution over time. This endpoint identifies main topics in conversations and tracks how they change over the specified period.
- Parameters:
  - days (optional): Number of days to analyze. Default: 7
  - room_id (optional): Filter by room ID
- Request Example:
  ```
  /api/v1/analytics/topic-evolution?days=7&room_id=!roomid:matrix.org
  ```
- Response Example:
  ```json
  {
    "topics": [
      {
        "topic": "Technical Discussion",
        "weight": 0.85,
        "timestamp": "2024-01-01T12:00:00Z",
        "keywords": ["python", "api", "database", "docker"]
      },
      {
        "topic": "Daily Chat",
        "weight": 0.65,
        "timestamp": "2024-01-01T14:30:00Z",
        "keywords": ["hello", "how", "weekend", "plans"]
      },
      {
        "topic": "Tech Support",
        "weight": 0.45,
        "timestamp": "2024-01-02T10:15:00Z",
        "keywords": ["help", "error", "fix", "issue"]
      }
    ],
    "summary": {
      "main_topics": ["Technical Discussion", "Daily Chat", "Tech Support"],
      "trend": "increasing",
      "analysis": "Technical discussions dominate, with increasing activity in tech support topics",
      "topic_distribution": {
        "Technical Discussion": 0.45,
        "Daily Chat": 0.35,
        "Tech Support": 0.20
      }
    }
  }
  ```
- Notes:
  - Weight represents the relative importance of the topic (0.0 to 1.0)
  - Topics are identified using AI analysis of message content
  - The summary provides an overview of topic trends and distribution

### GET /api/v1/analytics/content-analysis
- Description: Content analysis utilities including word frequency, message length statistics, and content patterns.
- Parameters:
  - days (optional): Number of days to analyze. Default: 7
  - room_id (optional): Filter by room ID
- Request Example:
  ```
  /api/v1/analytics/content-analysis?days=7&room_id=!roomid:matrix.org
  ```
- Response Example:
  ```json
  {
    "word_frequency": [
      {"word": "hello", "count": 42, "percentage": 0.05},
      {"word": "matrix", "count": 28, "percentage": 0.03},
      {"word": "python", "count": 25, "percentage": 0.03},
      {"word": "docker", "count": 18, "percentage": 0.02},
      {"word": "api", "count": 15, "percentage": 0.02}
    ],
    "message_stats": {
      "total_messages": 850,
      "avg_message_length": 45.2,
      "max_message_length": 280,
      "min_message_length": 1,
      "messages_with_links": 120,
      "messages_with_images": 65,
      "messages_with_code": 42
    },
    "content_patterns": {
      "questions": 85,
      "exclamations": 42,
      "code_blocks": 28,
      "mentions": 56
    }
  }
  ```
- Notes:
  - Word frequency excludes common stop words (the, and, is, etc.)
  - Percentage represents the word's frequency relative to total words analyzed
  - Content patterns identify specific types of messages for deeper analysis

### GET /api/v1/analytics/ai-analysis
- Description: Unified AI analysis endpoint.
- Parameters:
  - days (optional): Number of days. Default: 7
  - room_id (optional): Filter by room ID
  - analysis_type (optional): Supported: `sentiment`. Default: `sentiment`
- Response Example:
  ```json
  {
    "type": "sentiment",
    "result": {"sentiment": "positive", "confidence": 0.85},
    "metadata": {"message_count": 100, "room_id": null, "analysis_time": "2024-01-01T00:00:00Z", "model": "llama-3.1-8b-instant"}
  }
  ```

### GET /api/v1/analytics/analytics-health
- Description: Health check for analytics features and cache info.
- Response Example:
  ```json
  {
    "status": "healthy",
    "features": ["sentiment_analysis", "topic_analysis", "pattern_analysis"],
    "cache_info": {"enabled": true, "size": 128}
  }
  ```

## Media API Endpoints

### GET /api/v1/media/
- Description: List all media files with pagination and optional MIME type filtering.
- Parameters:
  - skip (optional): Pagination offset. Default: 0
  - limit (optional): Maximum number of records to return. Default: 100
  - mime_type (optional): Filter by MIME type prefix (e.g., 'image/' for images only)
- Request Example:
  ```
  /api/v1/media/?skip=0&limit=50&mime_type=image/
  ```
- Response Example:
  ```json
  {
    "media": [
      {
        "media_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_id": "$eventid",
        "room_id": "!roomid:matrix.org",
        "user_id": "@user:matrix.org",
        "original_filename": "photo.jpg",
        "mime_type": "image/jpeg",
        "file_size": 102400,
        "width": 800,
        "height": 600,
        "timestamp": "2024-01-01T00:00:00Z",
        "minio_key": "550e8400-e29b-41d4-a716-446655440000/photo.jpg"
      }
    ],
    "total": 150,
    "has_more": true,
    "next_skip": 50
  }
  ```

### GET /api/v1/media/stats
- Description: Get media statistics including total count, total size, and breakdown by media type.
- Request Example:
  ```
  /api/v1/media/stats
  ```
- Response Example:
  ```json
  {
    "total_count": 150,
    "total_size": 157286400,
    "by_type": [
      {"mime_type": "image/jpeg", "count": 80, "total_size": 83886080},
      {"mime_type": "image/png", "count": 40, "total_size": 41943040},
      {"mime_type": "video/mp4", "count": 20, "total_size": 25165824},
      {"mime_type": "audio/mpeg", "count": 10, "total_size": 6291456}
    ]
  }
  ```

### GET /api/v1/media/room/{room_id}
- Description: List media files from a specific room.
- Parameters:
  - room_id (required): Room identifier. Example: `!roomid:matrix.org`
  - skip (optional): Pagination offset. Default: 0
  - limit (optional): Maximum number of records to return. Default: 100
  - mime_type (optional): Filter by MIME type prefix (e.g., 'image/' for images only)
- Request Example:
  ```
  /api/v1/media/room/!roomid:matrix.org?skip=0&limit=50&mime_type=image/
  ```
- Response Example:
  ```json
  {
    "media": [
      {
        "media_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_id": "$eventid",
        "room_id": "!roomid:matrix.org",
        "user_id": "@user:matrix.org",
        "original_filename": "photo.jpg",
        "mime_type": "image/jpeg",
        "file_size": 102400,
        "width": 800,
        "height": 600,
        "timestamp": "2024-01-01T00:00:00Z",
        "minio_key": "550e8400-e29b-41d4-a716-446655440000/photo.jpg"
      }
    ],
    "total": 75,
    "has_more": true,
    "next_skip": 50
  }
  ```

### GET /api/v1/media/user/{user_id}
- Description: List media files sent by a specific user.
- Parameters:
  - user_id (required): User identifier. Example: `@user:matrix.org`
  - skip (optional): Pagination offset. Default: 0
  - limit (optional): Maximum number of records to return. Default: 100
  - mime_type (optional): Filter by MIME type prefix (e.g., 'image/' for images only)
- Request Example:
  ```
  /api/v1/media/user/@user:matrix.org?skip=0&limit=50&mime_type=image/
  ```
- Response Example:
  ```json
  {
    "media": [
      {
        "media_id": "550e8400-e29b-41d4-a716-446655440000",
        "event_id": "$eventid",
        "room_id": "!roomid:matrix.org",
        "user_id": "@user:matrix.org",
        "original_filename": "photo.jpg",
        "mime_type": "image/jpeg",
        "file_size": 102400,
        "width": 800,
        "height": 600,
        "timestamp": "2024-01-01T00:00:00Z",
        "minio_key": "550e8400-e29b-41d4-a716-446655440000/photo.jpg"
      }
    ],
    "total": 30,
    "has_more": false,
    "next_skip": null
  }
  ```

### GET /api/v1/media/{media_id}
- Description: Get media metadata with a presigned download URL.
- Parameters:
  - media_id (required): Unique identifier of the media file. Example: `550e8400-e29b-41d4-a716-446655440000`
- Request Example:
  ```
  /api/v1/media/550e8400-e29b-41d4-a716-446655440000
  ```
- Response Example:
  ```json
  {
    "media_id": "550e8400-e29b-41d4-a716-446655440000",
    "event_id": "$eventid",
    "room_id": "!roomid:matrix.org",
    "user_id": "@user:matrix.org",
    "original_filename": "photo.jpg",
    "mime_type": "image/jpeg",
    "file_size": 102400,
    "width": 800,
    "height": 600,
    "timestamp": "2024-01-01T00:00:00Z",
    "minio_key": "550e8400-e29b-41d4-a716-446655440000/photo.jpg",
    "download_url": "https://minio.example.com/matrix-media/550e8400-e29b-41d4-a716-446655440000/photo.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&..."
  }
  ```
- Notes:
  - The download URL is a presigned URL that expires after 1 hour
  - This endpoint returns metadata only; use the download endpoint to get the actual file

### GET /api/v1/media/{media_id}/download
- Description: Download media file directly or redirect to presigned URL.
- Parameters:
  - media_id (required): Unique identifier of the media file. Example: `550e8400-e29b-41d4-a716-446655440000`
  - redirect (optional): Redirect to presigned URL instead of streaming. Default: `true`
- Request Example:
  ```
  /api/v1/media/550e8400-e29b-41d4-a716-446655440000/download?redirect=false
  ```
- Response:
  - When `redirect=true` (default): HTTP 307 redirect to presigned download URL
  - When `redirect=false`: Direct file stream with appropriate Content-Type and Content-Disposition headers
- Notes:
  - Redirect mode is more efficient as it offloads file serving to MinIO
  - Direct streaming mode is useful when you need to go through the API for authentication or logging
  - Presigned URLs expire after 1 hour for security

## Error Codes

### Common HTTP Status Codes
- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters or malformed request
- `404 Not Found`: Resource not found (e.g., message, user, room, media)
- `500 Internal Server Error`: Server-side error

### Media API Specific Errors
- `404 Not Found`: Media file not found in database or MinIO storage
- `500 Internal Server Error`: MinIO connection error or storage failure
- `503 Service Unavailable`: Media storage service unavailable

### Analytics API Specific Errors
- `400 Bad Request`: Invalid analysis parameters (e.g., unsupported analysis_type)
- `500 Internal Server Error`: AI analysis service unavailable or analysis failure
- `503 Service Unavailable`: Cache service or external AI service unavailable

## Rate Limiting
- Default rate limit: 100 requests per minute per IP address
- Analytics endpoints may have lower limits due to computational complexity
- Media download endpoints are not rate limited for performance

## Authentication
Currently, the API does not require authentication. However, in production deployments, consider:
- Adding API key authentication
- Implementing rate limiting
- Restricting access to sensitive endpoints
- Using HTTPS for all communications
