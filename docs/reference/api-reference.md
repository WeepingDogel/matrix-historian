# API Reference

{% hint style="info" %}
**Category**: Reference
{% endhint %}

## Base URL
All endpoints are prefixed with `/api/v1`.

## Endpoints

### GET /messages/
- Description: Retrieve a list of messages.
- Parameters:
  - room_id (optional): Filter by room ID. Example: `!roomid:matrix.org`
  - user_id (optional): Filter by user ID. Example: `@user:matrix.org`
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
