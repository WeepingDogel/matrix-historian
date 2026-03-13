# API Reference

## Base information

- API base URL (default local): `http://localhost:8500`
- API base path: `/api/v1`
- Swagger / OpenAPI UI: `http://localhost:8500/docs`

## Important timestamp note

API timestamps should be treated as **UTC-based data**.

If you are building a UI, timezone conversion should happen in the presentation layer. The built-in web frontend follows this rule and can display either:
- **Local** (browser timezone)
- **UTC**

## Main endpoint groups

The current API includes endpoint groups for:

- `messages`
- `rooms`
- `users`
- `analytics`
- `media`

Because the API evolves over time, the most reliable source for request/response schemas is the live Swagger UI.

## Common local URLs

- Messages: `http://localhost:8500/api/v1/messages`
- Rooms: `http://localhost:8500/api/v1/rooms`
- Users: `http://localhost:8500/api/v1/users`
- Analytics: `http://localhost:8500/api/v1/analytics/...`
- Media: `http://localhost:8500/api/v1/media/...`

## Typical capabilities

### Messages
- list messages
- search messages
- filter by room
- filter by user
- paginate results

### Rooms / users
- list archived rooms
- list known users

### Analytics
- overview and trends
- activity heatmaps
- user activity views
- topic / content analysis
- optional AI-assisted analysis when configured

### Media
- list archived media
- query media by room or user
- retrieve metadata
- get download URLs or downloads

## Recommendation

For up-to-date request parameters and response schemas, use:

```text
http://localhost:8500/docs
```

This document intentionally stays high-level so it does not drift as quickly as hand-maintained endpoint examples.
