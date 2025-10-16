# Supabase Database Fixes Required

**Issue:** Quest creation system is functional but two database configuration issues prevent full operation.

---

## 🔴 Issue #1: PostgREST Schema Cache

**Problem:**
- The `verification_data` column exists in the `tasks` table
- Supabase PostgREST hasn't refreshed its schema cache
- API strips verification_data when inserting tasks
- Twitter quests can't access target username configuration

**Impact:**
- ❌ Twitter verification cannot function (missing target username)
- ❌ YouTube quests missing code/watch time config
- ✅ Daily and Manual quests work (don't need verification_data)

**Fix:**

### Option 1: Manual Refresh (Immediate)
```sql
-- Run in Supabase SQL Editor
NOTIFY pgrst, 'reload schema';
```

### Option 2: Restart PostgREST Service
Via Supabase Dashboard:
1. Navigate to Settings → Database
2. Click "Restart" button
3. Wait 30 seconds

### Option 3: Wait (24 hours)
PostgREST automatically refreshes cache every 24 hours

### Verification:
```bash
# After fix, create a new Twitter task and check:
curl -s http://localhost/api/tasks/{task_id} | jq .verification_data

# Should show:
# {
#   "method": "twitter_api",
#   "type": "follow",
#   "username": "targetuser"
# }

# Instead of: null
```

---

## 🔴 Issue #2: Missing video_views Table

**Problem:**
- YouTube watch tracking requires `video_views` table
- Migration file exists: `database/migrations/001_video_views.sql`
- Migration not applied to Supabase cloud database
- Backend uses fallback mode (immediate completion)

**Impact:**
- ❌ No watch time verification
- ❌ No secret code entry system
- ✅ YouTube quests complete immediately (degraded mode)

**Fix:**

### Run Migration in Supabase

1. **Open Supabase SQL Editor**
   - Dashboard → SQL Editor → New Query

2. **Copy Migration Content:**
```sql
-- Create video_views table for YouTube watch tracking
CREATE TABLE IF NOT EXISTS video_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    video_id VARCHAR(20),
    verification_code VARCHAR(50),
    status VARCHAR(20) DEFAULT 'watching',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE,
    watch_duration INTEGER,
    code_attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    min_watch_seconds INTEGER DEFAULT 120,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for user lookups
CREATE INDEX IF NOT EXISTS idx_video_views_user 
ON video_views(user_id);

-- Index for task lookups
CREATE INDEX IF NOT EXISTS idx_video_views_task 
ON video_views(task_id);

-- Index for status queries
CREATE INDEX IF NOT EXISTS idx_video_views_status 
ON video_views(status);

-- Composite index for active sessions
CREATE INDEX IF NOT EXISTS idx_video_views_user_task 
ON video_views(user_id, task_id, status);

-- Function to check watch time
CREATE OR REPLACE FUNCTION check_video_watch_time(
    p_view_id UUID,
    p_code VARCHAR(50)
)
RETURNS JSONB AS $$
DECLARE
    v_record video_views%ROWTYPE;
    v_elapsed INTEGER;
BEGIN
    SELECT * INTO v_record 
    FROM video_views 
    WHERE id = p_view_id;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'Session not found');
    END IF;
    
    -- Calculate elapsed time
    v_elapsed := EXTRACT(EPOCH FROM (NOW() - v_record.started_at))::INTEGER;
    
    -- Check code attempts
    IF v_record.code_attempts >= v_record.max_attempts THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'Maximum attempts exceeded'
        );
    END IF;
    
    -- Verify code
    IF v_record.verification_code != p_code THEN
        UPDATE video_views 
        SET code_attempts = code_attempts + 1
        WHERE id = p_view_id;
        
        RETURN jsonb_build_object(
            'success', false,
            'error', 'Invalid code',
            'attempts_remaining', v_record.max_attempts - v_record.code_attempts - 1
        );
    END IF;
    
    -- Check watch time
    IF v_elapsed < v_record.min_watch_seconds THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'Insufficient watch time',
            'watched', v_elapsed,
            'required', v_record.min_watch_seconds
        );
    END IF;
    
    -- Success!
    UPDATE video_views 
    SET 
        status = 'verified',
        verified_at = NOW(),
        watch_duration = v_elapsed
    WHERE id = p_view_id;
    
    RETURN jsonb_build_object(
        'success', true,
        'watch_duration', v_elapsed
    );
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON video_views TO authenticated;
GRANT SELECT, INSERT, UPDATE ON video_views TO anon;
```

3. **Execute Query**
   - Click "Run" button
   - Verify: "Success. No rows returned"

### Verification:
```bash
# Check table exists
curl -s "http://localhost/api/video-views?select=id&limit=1"

# Should return: [] or existing records
# Instead of: {"error": "table not found"}
```

### After Fix:
YouTube quest flow will work properly:
1. User starts quest → Creates video_views record
2. User opens video → Timer starts
3. User watches video → Sees secret code
4. User enters code → Backend verifies time + code
5. Success → Award points

---

## ✅ Post-Fix Testing

### 1. Test Twitter Quest with verification_data
```bash
# Create Twitter quest via admin UI
# Check verification_data persists:
curl http://localhost/api/tasks/{task_id} | jq .verification_data

# Test verification:
curl -X POST http://localhost/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "task_id": "{twitter_task_id}",
    "twitter_username": "testuser"
  }'

# Should verify against Twitter API
```

### 2. Test YouTube Quest with code entry
```bash
# Create YouTube quest with code "TEST2025"
# Start verification:
curl -X POST http://localhost/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "task_id": "{youtube_task_id}"
  }'

# Response will include session_id
# Wait 60+ seconds, then verify code:
curl -X POST http://localhost/api/video-views/verify \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_uuid}",
    "code": "TEST2025"
  }'

# Should award points after time check passes
```

### 3. Verify All Quest Types Working
```bash
python3 /workspaces/codespaces-blank/tmp/test_verification.py

# Expected results:
# ✅ Daily check-in: Complete
# ✅ YouTube: Code entry flow
# ✅ Twitter: API verification
# ✅ Manual: Pending status
```

---

## 📊 Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Admin UI | ✅ Working | All 4 quest types create |
| API Endpoints | ✅ Working | Verification routing complete |
| Daily Check-in | ✅ Working | Fully functional |
| Manual Review | ✅ Working | Creates pending tasks |
| Twitter Verification | ⚠️ Degraded | Needs schema cache refresh |
| YouTube Verification | ⚠️ Fallback | Needs video_views table |

---

## 🔧 How to Apply Fixes

### Prerequisites
- Supabase dashboard access
- Database permissions (service role or owner)

### Estimated Time
- Schema cache refresh: 1 minute
- Table creation: 2 minutes
- Testing: 5 minutes
- **Total: ~10 minutes**

### Steps
1. Open Supabase dashboard
2. Navigate to SQL Editor
3. Run schema refresh: `NOTIFY pgrst, 'reload schema';`
4. Run migration (copy SQL from above)
5. Test via admin UI or curl commands
6. Verify all quest types working

---

## 📞 Support

If issues persist after applying fixes:

1. **Check Logs:**
```bash
docker logs questx-api-1 | grep -i error
```

2. **Verify Columns:**
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tasks';
```

3. **Check PostgREST:**
```bash
# Should include verification_data
curl http://localhost/api/tasks?select=verification_data&limit=1
```

---

**Last Updated:** October 16, 2025  
**Priority:** High - Required for full quest system functionality
