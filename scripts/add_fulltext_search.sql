-- Add full-text search support to the messages table
-- This enables fast text search using PostgreSQL's built-in full-text search
-- instead of the slow LIKE '%query%' pattern.
--
-- Usage:
--   psql -d historian -f scripts/add_fulltext_search.sql

-- 1. Add a tsvector column for full-text search
ALTER TABLE messages ADD COLUMN IF NOT EXISTS content_tsv tsvector;

-- 2. Create a function to automatically update the tsvector column
CREATE OR REPLACE FUNCTION messages_content_tsv_update() RETURNS trigger AS $$
BEGIN
    NEW.content_tsv := to_tsvector('simple', coalesce(NEW.content, ''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- 3. Create trigger to keep the tsvector column in sync
DROP TRIGGER IF EXISTS trg_messages_content_tsv ON messages;
CREATE TRIGGER trg_messages_content_tsv
    BEFORE INSERT OR UPDATE OF content ON messages
    FOR EACH ROW
    EXECUTE FUNCTION messages_content_tsv_update();

-- 4. Backfill existing rows
UPDATE messages SET content_tsv = to_tsvector('simple', coalesce(content, ''));

-- 5. Create a GIN index for fast full-text search queries
CREATE INDEX IF NOT EXISTS ix_messages_content_tsv ON messages USING gin(content_tsv);

-- 6. (Optional) Also add a pg_trgm index for partial/fuzzy matching
-- Requires: CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS ix_messages_content_trgm ON messages USING gin (content gin_trgm_ops);