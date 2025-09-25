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
- Description: Get activity heatmap data by hour and weekday.
- Parameters:
  - days (optional): Number of days. Default: 7
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "heatmap": [[0, 1, 2], [3, 4, 5]],
    "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "hours": [0, 1, 2, ..., 23]
  }
  ```

### GET /api/v1/analytics/topic-evolution
- Description: Analyze topic evolution over time.
- Parameters:
  - days (optional): Number of days. Default: 7
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {
    "topics": [
      {
        "topic": "Technical Discussion",
        "weight": 1.0,
        "timestamp": "2024-01-01T12:00:00Z"
      }
    ],
    "summary": {
      "main_topics": ["Daily Chat", "Tech Support", "Q&A"],
      "trend": "stable"
    }
  }
  ```

### GET /api/v1/analytics/content-analysis
- Description: Content analysis utilities like word frequency.
- Parameters:
  - days (optional): Number of days. Default: 7
  - room_id (optional): Filter by room ID
- Response Example:
  ```json
  {"word_frequency": [{"word": "hello", "count": 42}]}
  ```

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
