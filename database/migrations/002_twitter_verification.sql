-- Migration: Add Twitter username to users table
-- This allows us to verify Twitter actions without asking every time

-- Add twitter_username column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS twitter_username VARCHAR(100),
ADD COLUMN IF NOT EXISTS twitter_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS twitter_verified_at TIMESTAMP;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_twitter_username ON users(twitter_username);

-- Create table for Twitter verification cache (reduce API calls)
CREATE TABLE IF NOT EXISTS twitter_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    twitter_username VARCHAR(100) NOT NULL,
    verification_type VARCHAR(20) NOT NULL, -- 'follow', 'like', 'retweet'
    tweet_id VARCHAR(100), -- For like/retweet verification
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    expires_at TIMESTAMP, -- Cache expiry
    api_response JSONB, -- Store full API response
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for twitter_verifications
CREATE INDEX IF NOT EXISTS idx_twitter_verifications_user ON twitter_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_twitter_verifications_task ON twitter_verifications(task_id);
CREATE INDEX IF NOT EXISTS idx_twitter_verifications_username ON twitter_verifications(twitter_username);
CREATE INDEX IF NOT EXISTS idx_twitter_verifications_expires ON twitter_verifications(expires_at);

-- Unique constraint: One verification per user-task combination
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_twitter_verification 
ON twitter_verifications(user_id, task_id) 
WHERE verified = TRUE;

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_twitter_verifications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS twitter_verifications_updated_at ON twitter_verifications;
CREATE TRIGGER twitter_verifications_updated_at
    BEFORE UPDATE ON twitter_verifications
    FOR EACH ROW
    EXECUTE FUNCTION update_twitter_verifications_updated_at();

-- Create table for Twitter API usage tracking (rate limit management)
CREATE TABLE IF NOT EXISTS twitter_api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint VARCHAR(100) NOT NULL, -- 'follow', 'like', 'retweet', etc.
    requests_made INT DEFAULT 0,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for current period lookup
CREATE INDEX IF NOT EXISTS idx_twitter_api_usage_period ON twitter_api_usage(period_start, period_end);

-- Insert initial usage tracking for current month
INSERT INTO twitter_api_usage (endpoint, requests_made, period_start, period_end)
VALUES 
    ('follow', 0, DATE_TRUNC('month', NOW()), DATE_TRUNC('month', NOW()) + INTERVAL '1 month'),
    ('like', 0, DATE_TRUNC('month', NOW()), DATE_TRUNC('month', NOW()) + INTERVAL '1 month'),
    ('retweet', 0, DATE_TRUNC('month', NOW()), DATE_TRUNC('month', NOW()) + INTERVAL '1 month')
ON CONFLICT DO NOTHING;

-- Verify tables created
SELECT 'Twitter verification tables created successfully' as status, COUNT(*) as row_count FROM twitter_verifications;
