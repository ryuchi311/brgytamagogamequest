-- Video Views Tracking Table
-- Tracks when users start and complete video quests with time delay + code verification

CREATE TABLE IF NOT EXISTS video_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    verification_code VARCHAR(50),
    code_attempts INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'watching' CHECK (status IN ('watching', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_video_views_user_id ON video_views(user_id);
CREATE INDEX IF NOT EXISTS idx_video_views_task_id ON video_views(task_id);
CREATE INDEX IF NOT EXISTS idx_video_views_status ON video_views(status);
CREATE INDEX IF NOT EXISTS idx_video_views_user_task ON video_views(user_id, task_id);

-- Create unique constraint to prevent duplicate active views
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_view 
    ON video_views(user_id, task_id) 
    WHERE status = 'watching';

-- Add verification_data column to tasks table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'verification_data'
    ) THEN
        ALTER TABLE tasks ADD COLUMN verification_data JSONB;
    END IF;
END $$;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_video_views_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic updated_at
DROP TRIGGER IF EXISTS video_views_updated_at_trigger ON video_views;
CREATE TRIGGER video_views_updated_at_trigger
    BEFORE UPDATE ON video_views
    FOR EACH ROW
    EXECUTE FUNCTION update_video_views_updated_at();

-- Grant permissions (adjust based on your setup)
-- GRANT ALL ON video_views TO authenticated;
-- GRANT ALL ON video_views TO service_role;

-- Insert test data (optional, remove in production)
-- This helps verify the table is working
INSERT INTO video_views (user_id, task_id, status, code_attempts)
SELECT 
    u.id as user_id,
    t.id as task_id,
    'watching' as status,
    0 as code_attempts
FROM users u
CROSS JOIN tasks t
WHERE t.platform = 'youtube'
LIMIT 1
ON CONFLICT DO NOTHING;

-- Verify table creation
SELECT 
    'video_views table created successfully' as status,
    COUNT(*) as row_count 
FROM video_views;
