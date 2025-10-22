-- Migration: Add YouTube Settings Columns to Tasks Table
-- This migration adds dedicated columns for YouTube quest settings
-- These columns provide a structured way to store YouTube-specific data
-- alongside the existing verification_data JSONB column

-- Add YouTube-specific columns to tasks table
DO $$ 
BEGIN
    -- Video ID (Auto-extracted from YouTube URL)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'youtube_video_id'
    ) THEN
        ALTER TABLE tasks ADD COLUMN youtube_video_id VARCHAR(20);
        COMMENT ON COLUMN tasks.youtube_video_id IS 'Auto-extracted YouTube video ID (e.g., dQw4w9WgXcQ)';
    END IF;

    -- Minimum Watch Time (seconds)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'min_watch_time_seconds'
    ) THEN
        ALTER TABLE tasks ADD COLUMN min_watch_time_seconds INTEGER;
        COMMENT ON COLUMN tasks.min_watch_time_seconds IS 'Minimum time user must watch before code input appears (seconds)';
    END IF;

    -- Video Duration (seconds)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'video_duration_seconds'
    ) THEN
        ALTER TABLE tasks ADD COLUMN video_duration_seconds INTEGER;
        COMMENT ON COLUMN tasks.video_duration_seconds IS 'Total duration of the YouTube video (seconds)';
    END IF;

    -- Verification Code
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'verification_code'
    ) THEN
        ALTER TABLE tasks ADD COLUMN verification_code VARCHAR(100);
        COMMENT ON COLUMN tasks.verification_code IS 'Code shown in video that user must enter to verify watching';
    END IF;

    -- Code Display Time (seconds)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'code_display_time_seconds'
    ) THEN
        ALTER TABLE tasks ADD COLUMN code_display_time_seconds INTEGER;
        COMMENT ON COLUMN tasks.code_display_time_seconds IS 'Timestamp in video when verification code is displayed (seconds from start)';
    END IF;

END $$;

-- Add constraints for data validation
ALTER TABLE tasks 
    ADD CONSTRAINT check_min_watch_time_positive 
    CHECK (min_watch_time_seconds IS NULL OR min_watch_time_seconds >= 0);

ALTER TABLE tasks 
    ADD CONSTRAINT check_video_duration_positive 
    CHECK (video_duration_seconds IS NULL OR video_duration_seconds > 0);

ALTER TABLE tasks 
    ADD CONSTRAINT check_code_display_time_positive 
    CHECK (code_display_time_seconds IS NULL OR code_display_time_seconds >= 0);

ALTER TABLE tasks 
    ADD CONSTRAINT check_code_display_before_duration 
    CHECK (
        code_display_time_seconds IS NULL 
        OR video_duration_seconds IS NULL 
        OR code_display_time_seconds <= video_duration_seconds
    );

-- Create index for YouTube video ID lookups
CREATE INDEX IF NOT EXISTS idx_tasks_youtube_video_id 
    ON tasks(youtube_video_id) 
    WHERE youtube_video_id IS NOT NULL;

-- Create index for tasks with verification codes
CREATE INDEX IF NOT EXISTS idx_tasks_with_verification_code 
    ON tasks(verification_code) 
    WHERE verification_code IS NOT NULL;

-- Add helpful comment to the table
COMMENT ON TABLE tasks IS 'Quest/Task definitions including YouTube video quests with time-based verification';

-- Migration completed successfully
-- The tasks table now has dedicated columns for YouTube settings:
-- 1. youtube_video_id - Auto-extracted from URL
-- 2. min_watch_time_seconds - Minimum watch time before code input
-- 3. video_duration_seconds - Total video length
-- 4. verification_code - Code user must enter
-- 5. code_display_time_seconds - When code appears in video
--
-- These columns work alongside verification_data JSONB for backward compatibility
