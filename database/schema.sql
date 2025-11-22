-- Telegram Bot Database Schema
-- Compatible with Supabase PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    points INTEGER DEFAULT 0,
    total_earned_points INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    is_banned BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tasks Table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL, -- 'social_follow', 'like_post', 'share_post', 'watch_video', 'custom'
    platform VARCHAR(50), -- 'instagram', 'twitter', 'youtube', 'facebook', 'tiktok'
    url TEXT,
    points_reward INTEGER NOT NULL,
    is_bonus BOOLEAN DEFAULT false,
    max_completions INTEGER DEFAULT 1, -- How many times a user can complete this task
    verification_required BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    
    -- YouTube Settings Columns
    youtube_video_id VARCHAR(20), -- Auto-extracted from YouTube URL (e.g., dQw4w9WgXcQ)
    min_watch_time_seconds INTEGER, -- Minimum watch time before code input appears
    video_duration_seconds INTEGER, -- Total video duration
    verification_code VARCHAR(100), -- Code shown in video for verification
    code_display_time_seconds INTEGER, -- When code appears in video (seconds from start)
    
    -- Generic verification data (JSONB for flexibility)
    verification_data JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints for YouTube settings
    CONSTRAINT check_min_watch_time_positive CHECK (min_watch_time_seconds IS NULL OR min_watch_time_seconds >= 0),
    CONSTRAINT check_video_duration_positive CHECK (video_duration_seconds IS NULL OR video_duration_seconds > 0),
    CONSTRAINT check_code_display_time_positive CHECK (code_display_time_seconds IS NULL OR code_display_time_seconds >= 0),
    CONSTRAINT check_code_display_before_duration CHECK (
        code_display_time_seconds IS NULL 
        OR video_duration_seconds IS NULL 
        OR code_display_time_seconds <= video_duration_seconds
    )
);

-- User Tasks (Task Completion Tracking)
CREATE TABLE user_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_progress', 'submitted', 'verified', 'completed', 'rejected'
    proof_url TEXT,
    completion_count INTEGER DEFAULT 0,
    points_earned INTEGER DEFAULT 0,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, task_id)
);

-- Rewards Table
CREATE TABLE rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reward_type VARCHAR(50) NOT NULL, -- 'discount', 'gift_card', 'exclusive_content', 'custom'
    points_cost INTEGER NOT NULL,
    quantity_available INTEGER,
    quantity_claimed INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    image_url TEXT,
    code_prefix VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Rewards (Redemption History)
CREATE TABLE user_rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reward_id UUID REFERENCES rewards(id) ON DELETE CASCADE,
    redemption_code VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'delivered', 'used', 'expired'
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    used_at TIMESTAMP WITH TIME ZONE
);

-- Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50), -- 'new_task', 'task_verified', 'reward_available', 'leaderboard_update', 'system'
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Admin Users Table
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin', -- 'admin', 'super_admin', 'moderator'
    permissions TEXT,
    is_super_admin BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Points Transaction Log
CREATE TABLE points_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50), -- 'earned', 'spent', 'bonus', 'refund', 'adjustment'
    reference_id UUID, -- Can reference task_id or reward_id
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Activity Logs
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_points ON users(points DESC);
CREATE INDEX idx_user_tasks_user_id ON user_tasks(user_id);
CREATE INDEX idx_user_tasks_task_id ON user_tasks(task_id);
CREATE INDEX idx_user_tasks_status ON user_tasks(status);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_tasks_updated_at BEFORE UPDATE ON user_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rewards_updated_at BEFORE UPDATE ON rewards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample admin user (password: changeme123)
-- Note: You should change this password in production
INSERT INTO admin_users (username, password_hash, email, role, permissions, is_super_admin)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5qlJ3U/pqWU7m', 'admin@example.com', 'super_admin', 'quests,users,verification', true);

-- Insert sample tasks
INSERT INTO tasks (title, description, task_type, platform, url, points_reward, is_bonus)
VALUES 
    ('Follow us on Instagram', 'Follow our Instagram account to stay updated', 'social_follow', 'instagram', 'https://instagram.com/yourhandle', 50, false),
    ('Like our latest post', 'Like our latest Instagram post', 'like_post', 'instagram', 'https://instagram.com/p/example', 20, false),
    ('Watch our YouTube video', 'Watch our latest tutorial video on YouTube', 'watch_video', 'youtube', 'https://youtube.com/watch?v=example', 30, false),
    ('Share on Twitter', 'Share our tweet with your followers', 'share_post', 'twitter', 'https://twitter.com/handle/status/123', 40, false),
    ('Daily Bonus Check-in', 'Check in daily to receive bonus points', 'custom', null, null, 10, true);

-- Insert sample rewards
INSERT INTO rewards (title, description, reward_type, points_cost, quantity_available)
VALUES 
    ('10% Discount Code', 'Get 10% off on your next purchase', 'discount', 500, 100),
    ('$5 Gift Card', 'Redeem for a $5 gift card', 'gift_card', 1000, 50),
    ('Exclusive Premium Content', 'Access to exclusive premium content', 'exclusive_content', 2000, 20),
    ('Free Product Sample', 'Get a free product sample delivered to you', 'custom', 1500, 30);
