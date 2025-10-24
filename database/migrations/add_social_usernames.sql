-- Migration: Add social media username columns to users table
-- Date: 2025-10-24
-- Purpose: Store user's social media usernames for API verification

-- Add Twitter username column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS twitter_username VARCHAR(15);

-- Add Instagram username column (for future use)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS instagram_username VARCHAR(30);

-- Add Discord username column (for future use)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS discord_username VARCHAR(37);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_twitter_username ON users(twitter_username);
CREATE INDEX IF NOT EXISTS idx_users_instagram_username ON users(instagram_username);
CREATE INDEX IF NOT EXISTS idx_users_discord_username ON users(discord_username);

-- Add comments
COMMENT ON COLUMN users.twitter_username IS 'Twitter username (without @) for API verification';
COMMENT ON COLUMN users.instagram_username IS 'Instagram username for API verification';
COMMENT ON COLUMN users.discord_username IS 'Discord username#discriminator for API verification';
