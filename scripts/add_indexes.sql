-- Composite indexes for common query patterns
-- These cover the most frequent analytics and search queries

-- Messages: room + timestamp (room filtering with time range/ordering)
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_messages_room_id_timestamp
ON messages (room_id, timestamp DESC);

-- Messages: sender + timestamp (user filtering with time range/ordering)
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_messages_sender_id_timestamp
ON messages (sender_id, timestamp DESC);

-- Messages: timestamp + room_id (analytics: group by date filtered by room)
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_messages_timestamp_room_id
ON messages (timestamp, room_id);

-- Messages: GIN index for full-text search on content (much faster than LIKE %%)
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_messages_content_trgm
ON messages USING gin (content gin_trgm_ops);
-- Note: requires pg_trgm extension: CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Media: event_id + mime_type (JOIN with messages + type filtering)
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_media_event_id_mime_type
ON media (event_id, mime_type);
