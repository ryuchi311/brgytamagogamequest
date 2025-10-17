# 🗄️ Supabase PostgreSQL Database Architecture

**Project:** Gaming Quest System  
**Database:** Supabase (PostgreSQL)  
**Last Updated:** October 16, 2025  
**Status:** 🟢 Production Ready

---

## 📊 Database Overview

### Technology Stack:
- **Database Engine:** PostgreSQL 15+
- **Hosting:** Supabase (Cloud PostgreSQL)
- **Connection:** Python Supabase Client v2.22.0
- **ORM:** Pydantic Models (FastAPI)
- **Migrations:** SQL Scripts

### Key Features:
✅ **UUID Primary Keys** - Secure and distributed  
✅ **Automatic Timestamps** - created_at, updated_at triggers  
✅ **Referential Integrity** - Foreign key constraints  
✅ **Indexed Performance** - Strategic indexes on key columns  
✅ **JSONB Support** - Flexible data storage  
✅ **Row Level Security** - Supabase RLS (optional)

---

## 📁 Database Schema

### Core Tables (9 Tables)

#### 1. **users** - User Accounts
Stores Telegram user information and point balances.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    points INTEGER DEFAULT 0,                    -- Current available points
    total_earned_points INTEGER DEFAULT 0,       -- Lifetime earned points
    twitter_username VARCHAR(100),               -- For Twitter verification
    twitter_verified BOOLEAN DEFAULT FALSE,
    twitter_verified_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    is_banned BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_users_telegram_id` ON telegram_id
- `idx_users_points` ON points DESC (for leaderboard)
- `idx_users_twitter_username` ON twitter_username

**Key Columns:**
- `points` - Current spendable points (decreases on reward redemption)
- `total_earned_points` - Historical total (never decreases)
- `telegram_id` - Unique Telegram user identifier
- `twitter_username` - Cached Twitter handle for verification

---

#### 2. **tasks** - Quest Definitions
Defines available quests/tasks for users to complete.

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,              -- Quest type identifier
    platform VARCHAR(50),                         -- twitter, youtube, telegram, etc.
    url TEXT,                                     -- Action URL (tweet, video, channel)
    points_reward INTEGER NOT NULL,
    is_bonus BOOLEAN DEFAULT false,
    max_completions INTEGER DEFAULT 1,            -- How many times user can complete
    verification_required BOOLEAN DEFAULT false,
    verification_data JSONB,                      -- Quest-specific data
    is_active BOOLEAN DEFAULT true,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Task Types:**
- `twitter_follow` - Follow Twitter account
- `twitter_like` - Like tweet
- `twitter_retweet` - Retweet
- `twitter_reply` - Reply to tweet
- `twitter_quote` - Quote tweet
- `youtube_watch` - Watch video
- `youtube_subscribe` - Subscribe channel
- `youtube_like` - Like video
- `youtube_comment` - Comment on video
- `telegram_join_group` - Join Telegram group
- `telegram_subscribe_channel` - Subscribe to channel
- `daily_checkin` - Daily streak tracking
- `manual_submission` - Custom submission (text/image)

**Verification Data (JSONB Examples):**
```json
// Twitter Quest
{
  "action": "follow",
  "twitter_handle": "@username"
}

// YouTube Quest
{
  "video_id": "dQw4w9WgXcQ",
  "min_watch_time": 120,
  "secret_code": "GAME2025",
  "max_attempts": 3
}

// Telegram Quest
{
  "chat_id": "-1001234567890",
  "chat_username": "@gamingchannel",
  "action": "join"
}
```

---

#### 3. **user_tasks** - Task Completion Tracking
Junction table tracking user progress on tasks.

```sql
CREATE TABLE user_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',        -- Workflow status
    proof_url TEXT,                              -- Screenshot/submission URL
    completion_count INTEGER DEFAULT 0,          -- Times completed
    points_earned INTEGER DEFAULT 0,
    verified_by UUID REFERENCES users(id),       -- Admin who verified
    verified_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, task_id)
);
```

**Status Workflow:**
1. `pending` - Task available, not started
2. `in_progress` - User started task
3. `submitted` - User submitted proof (manual tasks)
4. `verified` - Admin verified completion
5. `completed` - Task completed, points awarded
6. `rejected` - Submission rejected

**Indexes:**
- `idx_user_tasks_user_id` ON user_id
- `idx_user_tasks_task_id` ON task_id
- `idx_user_tasks_status` ON status

---

#### 4. **rewards** - Reward Catalog
Available rewards users can redeem with points.

```sql
CREATE TABLE rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reward_type VARCHAR(50) NOT NULL,
    points_cost INTEGER NOT NULL,
    quantity_available INTEGER,                  -- NULL = unlimited
    quantity_claimed INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    image_url TEXT,
    code_prefix VARCHAR(50),                     -- For auto-generated codes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Reward Types:**
- `discount` - Discount codes
- `gift_card` - Gift cards
- `exclusive_content` - Premium access
- `merchandise` - Physical items
- `custom` - Custom rewards

---

#### 5. **user_rewards** - Redemption History
Tracks which users redeemed which rewards.

```sql
CREATE TABLE user_rewards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    reward_id UUID REFERENCES rewards(id) ON DELETE CASCADE,
    redemption_code VARCHAR(255),                -- Unique code for user
    status VARCHAR(50) DEFAULT 'pending',
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP WITH TIME ZONE,
    used_at TIMESTAMP WITH TIME ZONE
);
```

**Status Values:**
- `pending` - Redeemed, awaiting delivery
- `delivered` - Code/item delivered to user
- `used` - User confirmed usage
- `expired` - Redemption expired

---

#### 6. **video_views** - Video Quest Tracking
Special table for YouTube video verification.

```sql
CREATE TABLE video_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    verification_code VARCHAR(50),               -- Secret code from video
    code_attempts INTEGER DEFAULT 0,             -- Failed attempt counter
    status VARCHAR(20) DEFAULT 'watching',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Unique Constraint:** One active watch per user-task combination

**Workflow:**
1. User starts video → `status='watching'`, `started_at` recorded
2. After min_watch_time → User can submit code
3. Correct code → `status='completed'`, points awarded
4. Wrong code → `code_attempts++`, max 3 attempts

---

#### 7. **twitter_verifications** - Twitter Verification Cache
Caches Twitter API verification results to reduce API calls.

```sql
CREATE TABLE twitter_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    twitter_username VARCHAR(100) NOT NULL,
    verification_type VARCHAR(20) NOT NULL,      -- 'follow', 'like', 'retweet'
    tweet_id VARCHAR(100),                       -- For like/retweet
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    expires_at TIMESTAMP,                        -- Cache expiry (24 hours)
    api_response JSONB,                          -- Full Twitter API response
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Benefits:**
- Reduces Twitter API rate limit usage
- Faster verification for returning users
- Stores proof of verification

---

#### 8. **admin_users** - Admin Authentication
Admin panel user accounts.

```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,                 -- bcrypt hashed
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);
```

**Default Admin:**
- Username: `admin`
- Password: `changeme123` (hashed with bcrypt)
- Role: `super_admin`

**Roles:**
- `super_admin` - Full access
- `admin` - Standard admin access
- `moderator` - Limited access (verify tasks only)

---

#### 9. **points_transactions** - Transaction Log
Audit trail for all point movements.

```sql
CREATE TABLE points_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,                     -- Positive = earned, Negative = spent
    transaction_type VARCHAR(50),
    reference_id UUID,                           -- task_id or reward_id
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Transaction Types:**
- `earned` - Points earned from task
- `spent` - Points spent on reward
- `bonus` - Bonus points awarded
- `refund` - Points refunded
- `adjustment` - Manual admin adjustment

**Index:** `idx_points_transactions_user_id` ON user_id

---

## 🔄 Database Migrations

### Migration Files:
1. **001_video_views.sql** - YouTube quest tracking
2. **002_twitter_verification.sql** - Twitter verification cache

### How to Apply Migrations:
```sql
-- In Supabase SQL Editor, run:
\i database/migrations/001_video_views.sql
\i database/migrations/002_twitter_verification.sql
```

---

## 🔌 API Integration

### Supabase Client Configuration:
```python
# app/models.py
from supabase import create_client, Client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)
```

### Environment Variables (.env):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-jwt-secret-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Common Query Patterns:

#### Get User by Telegram ID:
```python
response = supabase.table("users")\
    .select("*")\
    .eq("telegram_id", telegram_id)\
    .single()\
    .execute()
user = response.data
```

#### Get Active Tasks:
```python
response = supabase.table("tasks")\
    .select("*")\
    .eq("is_active", True)\
    .order("created_at", desc=True)\
    .execute()
tasks = response.data
```

#### Create User Task:
```python
data = {
    "user_id": user_id,
    "task_id": task_id,
    "status": "in_progress"
}
response = supabase.table("user_tasks")\
    .insert(data)\
    .execute()
```

#### Award Points:
```python
# Update user points
supabase.table("users")\
    .update({
        "points": user["points"] + points,
        "total_earned_points": user["total_earned_points"] + points
    })\
    .eq("id", user_id)\
    .execute()

# Log transaction
supabase.table("points_transactions")\
    .insert({
        "user_id": user_id,
        "amount": points,
        "transaction_type": "earned",
        "reference_id": task_id,
        "description": f"Completed task: {task_title}"
    })\
    .execute()
```

#### Get Leaderboard:
```python
response = supabase.table("users")\
    .select("telegram_id, username, first_name, total_earned_points")\
    .eq("is_active", True)\
    .order("total_earned_points", desc=True)\
    .limit(10)\
    .execute()
leaderboard = response.data
```

---

## 📊 Database Performance

### Indexed Queries (Fast):
✅ Find user by telegram_id  
✅ Get leaderboard (sorted by points)  
✅ Get user's tasks  
✅ Get task completions  
✅ Get active notifications  

### Optimization Tips:
1. **Use indexes** - All foreign keys are indexed
2. **Batch operations** - Use bulk insert when possible
3. **Pagination** - Use `.range(start, end)` for large datasets
4. **Select specific columns** - Don't use `SELECT *` in production
5. **Cache frequently accessed data** - Use Redis for hot data

---

## 🔒 Security Best Practices

### Row Level Security (RLS):
Enable RLS in Supabase for additional security:

```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);

-- Policy: Admins can see all data
CREATE POLICY "Admins can view all data"
ON users FOR SELECT
USING (auth.role() = 'admin');
```

### Data Validation:
- ✅ Use Pydantic models for input validation
- ✅ Sanitize user inputs (prevent SQL injection)
- ✅ Hash passwords with bcrypt (never store plain text)
- ✅ Use UUID instead of incremental IDs
- ✅ Set proper foreign key constraints

---

## 🧪 Sample Data

### Test Users:
```sql
INSERT INTO users (telegram_id, username, first_name, points, total_earned_points)
VALUES 
    (123456789, 'testuser1', 'Test User 1', 500, 1000),
    (987654321, 'testuser2', 'Test User 2', 1500, 2500);
```

### Test Tasks:
```sql
INSERT INTO tasks (title, task_type, platform, url, points_reward)
VALUES 
    ('Follow @GameQuest', 'twitter_follow', 'twitter', 'https://twitter.com/gamequest', 50),
    ('Watch Tutorial Video', 'youtube_watch', 'youtube', 'https://youtube.com/watch?v=abc123', 100),
    ('Join Telegram Channel', 'telegram_subscribe_channel', 'telegram', 'https://t.me/gamechannel', 75);
```

---

## 📈 Analytics Queries

### Total Users:
```sql
SELECT COUNT(*) FROM users WHERE is_active = true;
```

### Points Distribution:
```sql
SELECT 
    CASE 
        WHEN points < 100 THEN '0-99'
        WHEN points < 500 THEN '100-499'
        WHEN points < 1000 THEN '500-999'
        ELSE '1000+'
    END as point_range,
    COUNT(*) as user_count
FROM users
WHERE is_active = true
GROUP BY point_range
ORDER BY point_range;
```

### Task Completion Rate:
```sql
SELECT 
    t.title,
    COUNT(ut.id) as attempts,
    SUM(CASE WHEN ut.status = 'completed' THEN 1 ELSE 0 END) as completed,
    ROUND(100.0 * SUM(CASE WHEN ut.status = 'completed' THEN 1 ELSE 0 END) / COUNT(ut.id), 2) as completion_rate
FROM tasks t
LEFT JOIN user_tasks ut ON t.id = ut.task_id
WHERE t.is_active = true
GROUP BY t.id, t.title
ORDER BY completion_rate DESC;
```

### Daily Active Users:
```sql
SELECT 
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users
FROM user_tasks
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🛠️ Maintenance

### Backup Strategy:
- ✅ Supabase automatic daily backups
- ✅ Point-in-time recovery available
- ✅ Export schema: `pg_dump` via Supabase CLI

### Clean Up Old Data:
```sql
-- Delete expired video views
DELETE FROM video_views 
WHERE status = 'completed' 
AND completed_at < NOW() - INTERVAL '90 days';

-- Delete expired verification cache
DELETE FROM twitter_verifications 
WHERE expires_at < NOW();
```

### Database Health Check:
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

---

## 📚 Related Files

- `database/schema.sql` - Main schema definition
- `database/migrations/001_video_views.sql` - Video tracking
- `database/migrations/002_twitter_verification.sql` - Twitter cache
- `app/models.py` - Pydantic models
- `app/api.py` - FastAPI endpoints
- `.env` - Supabase credentials

---

## 🔗 Quick Links

- **Supabase Dashboard:** https://app.supabase.com
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Supabase Python Client:** https://supabase.com/docs/reference/python/introduction
- **FastAPI + Supabase:** https://fastapi.tiangolo.com/

---

**Database Status:** 🟢 Healthy  
**Tables:** 9 core + 2 extended  
**Indexes:** 15+ for performance  
**Migrations:** 2 applied  
**Connection:** ✅ Active via Supabase client
