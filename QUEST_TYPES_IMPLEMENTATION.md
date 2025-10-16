# Quest Type System - Complete Implementation Guide

**Date:** October 16, 2025  
**Status:** ✅ Core implemented | ⚠️ Database setup required

---

## 🎯 Overview

The gaming quest system now supports **four specialized quest types** with automated verification:

| Type | Icon | Verification | Status |
|------|------|--------------|--------|
| Twitter | 🐦 | API (Follow/Like/RT) | ⚠️ Needs DB fix |
| YouTube | 📺 | Watch time + Code | ⚠️ Needs table |
| Manual | ✍️ | Admin review | ✅ Working |
| Daily | 📅 | Auto (once/day) | ✅ Working |

---

## 📋 Admin UI Guide

### Creating a Quest

1. **Navigate:** Admin Dashboard → Quests → CREATE QUEST
2. **Select Type:** Click one of four quest type buttons
3. **Fill Fields:** Form shows fields specific to selected type
4. **Submit:** Click CREATE QUEST button

### Quest Type Fields

#### 🐦 Twitter Quest
```
Required:
- Action Type: [Follow / Like / Retweet / Reply]
- Target Username: @handle (without @)
- Tweet URL: (for Like/Retweet/Reply only)

Example:
- Title: "Follow Us on Twitter"
- Action: Follow
- Username: example
- Points: 25
```

#### 📺 YouTube Quest
```
Required:
- Video URL: https://youtube.com/watch?v=...
- Secret Code: Text shown in video
- Min Watch Time: Seconds (default: 120)
- Max Attempts: Code entry attempts (default: 3)

Example:
- Title: "Watch Tutorial"
- URL: https://youtube.com/watch?v=dQw4w9WgXcQ
- Code: QUEST2025
- Watch Time: 60 seconds
- Points: 100
```

#### 📅 Daily Check-in Quest
```
Required:
- Streak Bonus: [None / Multiply / Milestones]
- Reset Time: HH:MM UTC (default: 00:00)
- Consecutive Required: [Yes / No]

Example:
- Title: "Daily Login"
- Reset: 00:00 UTC
- Streak: None
- Points: 10
```

#### ✍️ Manual Quest
```
Optional:
- Quest URL: Link to instructions
- Submission Type: [None / Text / Screenshot / Code]
- Instructions: What user must do

Example:
- Title: "Join Discord Server"
- Submission: Screenshot
- Instructions: "Join our Discord and screenshot the welcome message"
- Points: 50
```

---

## 🔧 Technical Implementation

### Database Schema

**Tasks Table:**
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  description TEXT,
  task_type VARCHAR(50), -- NEW: twitter_follow, youtube_watch, etc.
  platform VARCHAR(50),
  url TEXT,
  points_reward INTEGER,
  verification_required BOOLEAN,
  verification_data JSONB, -- NEW: Quest-specific config
  is_active BOOLEAN,
  created_at TIMESTAMP
);
```

### Backend Models

**TaskCreate (Pydantic):**
```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str  # Required: twitter_follow, youtube_watch, etc.
    platform: Optional[str] = None
    url: Optional[str] = None
    points_reward: int = 0
    verification_required: bool = False
    verification_data: Optional[dict] = None
```

### API Endpoints

#### Create Quest
```http
POST /api/tasks
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "title": "Follow Us",
  "task_type": "twitter_follow",
  "platform": "twitter",
  "points_reward": 25,
  "verification_required": true,
  "verification_data": {
    "method": "twitter_api",
    "type": "follow",
    "username": "example"
  }
}
```

#### Verify Quest Completion
```http
POST /api/verify
Content-Type: application/json

{
  "telegram_id": 123456789,
  "task_id": "quest-uuid",
  "twitter_username": "user123"  // Required for Twitter
}
```

---

## 🔄 Verification Flows

### Twitter Flow
```
User clicks quest
  ↓
Frontend: Prompt for Twitter username
  ↓
POST /api/verify {telegram_id, task_id, twitter_username}
  ↓
Backend: Calls Twitter API
  ↓
✅ Verified: Award points immediately
❌ Failed: Return error message
```

**Twitter API Methods:**
- `verify_follow(user, target)` - Check if user follows target
- `verify_like(user, tweet_id)` - Check if user liked tweet
- `verify_retweet(user, tweet_id)` - Check if user retweeted

### YouTube Flow
```
User clicks quest
  ↓
POST /api/verify
  ↓
Backend: Creates video_views record
  ↓
User watches video (opens new tab)
  ↓
User enters code from video
  ↓
POST /api/video-views/verify {user_id, code}
  ↓
Backend checks:
  - Code matches
  - Watch time >= minimum
  - Attempts < maximum
  ↓
✅ All pass: Award points
❌ Failed: Decrement attempts
```

### Daily Check-in Flow
```
User clicks quest
  ↓
POST /api/verify
  ↓
Backend checks: Already completed today?
  ↓
No: Award points, mark completed
Yes: Return "come back tomorrow"
```

### Manual Flow
```
User clicks quest
  ↓
User submits proof (screenshot/link)
  ↓
Creates pending user_task
  ↓
Admin reviews in verification queue
  ↓
Admin approves/rejects
  ↓
Approved: Award points
Rejected: Notify user
```

---

## 🐛 Known Issues & Fixes

### Issue #1: verification_data Not Stored

**Symptom:** Twitter quests can't access target username  
**Cause:** Supabase PostgREST schema cache doesn't recognize `verification_data` column  
**Status:** Column exists but cache not refreshed

**Temporary Workaround:**
Backend catches error and creates task without verification_data

**Permanent Fix:**
```sql
-- Run in Supabase SQL Editor
NOTIFY pgrst, 'reload schema';

-- Or manually check column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tasks' AND column_name = 'verification_data';
```

**Alternative:** Wait 24 hours for auto-refresh

### Issue #2: video_views Table Missing

**Symptom:** YouTube quests show 500 error  
**Cause:** Migration not run in Supabase cloud  
**Status:** Table schema exists locally but not in cloud

**Fix:** Run migration in Supabase dashboard:
```sql
-- Copy contents from database/migrations/001_video_views.sql
-- Paste in Supabase SQL Editor
-- Execute

CREATE TABLE IF NOT EXISTS video_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    video_id VARCHAR(20),
    verification_code VARCHAR(50),
    status VARCHAR(20) DEFAULT 'watching',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    code_attempts INTEGER DEFAULT 0
);
```

---

## ✅ Test Results

### Test Commands
```bash
# Created 4 sample quests
python3 /workspaces/codespaces-blank/tmp/post_tasks.py

# Test Results:
✅ Twitter task created (ID: 63f558a8-eb3e-414d-997c-76d8b4897fad)
✅ YouTube task created (ID: 88a3f240-1b85-4d1d-bc7c-e786a281ee51)
✅ Manual task created (ID: 97012ebc-ec2e-4e06-aafe-4d5405864643)
✅ Daily task created (ID: 51b64498-08e6-452e-8060-104c94c20804)
```

### Verification Tests
```bash
python3 /workspaces/codespaces-blank/tmp/test_verification.py

# Results:
✅ Daily check-in: Completed (+10 points)
✅ Daily check-in duplicate: Rejected correctly
✅ YouTube: Fallback message shown
✅ Twitter: Username validation working
⚠️ Twitter: Can't verify (no verification_data)
```

---

## 📝 Code Changes Summary

### Frontend (`frontend/admin.html`)

**Added:**
- Quest type selector (4 buttons)
- Dynamic form fields per type
- `selectQuestType()` function
- Updated `submitTask()` to build type-specific payloads

**Key Code:**
```javascript
function selectQuestType(type) {
  selectedQuestType = type;
  // Show common fields
  document.querySelector('.common-fields').style.display = 'block';
  // Show type-specific fields
  document.getElementById(`${type}Fields`).classList.remove('hidden');
  // Set task_type and platform
  document.getElementById('taskType').value = typeMap[type];
  document.getElementById('taskPlatform').value = type;
}

async function submitTask(event) {
  // Build verification_data based on selectedQuestType
  if (selectedQuestType === 'twitter') {
    taskData.task_type = 'twitter_follow'; // or twitter_like, etc.
    taskData.verification_data = {
      method: 'twitter_api',
      type: actionType,
      username: username
    };
  }
  // ... similar for other types
}
```

### Backend (`app/api.py`)

**Modified:**
1. `TaskCreate` model - Made optional fields have defaults
2. `create_task()` - Added APIError handling for schema cache
3. `/api/verify` - Completely rewrote to use task_type routing

**Key Changes:**
```python
# Old: Routed by platform
if platform == 'twitter':
    # verification logic

# New: Routes by task_type
if task_type.startswith('twitter_'):
    verification_type = task_type.replace('twitter_', '')
    if verification_type == 'follow':
        result = twitter_client.verify_follow(user_twitter, target_username)
    elif verification_type == 'like':
        result = twitter_client.verify_like(user_twitter, tweet_id)
    # etc.
```

---

## 🚀 Next Steps

### Priority 1: Database Setup (Required)
1. Refresh Supabase PostgREST schema cache
2. Run video_views migration
3. Test Twitter verification with verification_data
4. Test YouTube code entry flow

### Priority 2: Frontend Enhancements
5. Add YouTube code entry modal
6. Show watch time countdown
7. Display remaining code attempts
8. Add Twitter username to user profile

### Priority 3: Admin Tools
9. Manual review queue UI
10. One-click approve/reject
11. View user submissions
12. Quest analytics dashboard

### Priority 4: Advanced Features
13. Daily streak tracking and bonuses
14. Quest completion analytics
15. Automated testing suite
16. Rate limit monitoring

---

## 📚 References

- **Admin Dashboard:** http://localhost/admin.html
- **API Docs:** http://localhost/api/docs
- **Twitter Client:** `app/twitter_client.py`
- **Migrations:** `database/migrations/`
- **Sample Tasks:** `tmp/twitter_task.json`, etc.

---

**Last Updated:** October 16, 2025  
**Contributors:** GitHub Copilot  
**Status:** Core implementation complete, database setup required
