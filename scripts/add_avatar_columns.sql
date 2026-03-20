-- Add avatar_url columns to users and rooms tables
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;
