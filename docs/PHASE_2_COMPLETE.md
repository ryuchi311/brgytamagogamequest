# Phase 2 Complete: YouTube Video Verification - Bot & API Implementation

## ✅ Completed Components

### 1. Bot Code Updates (`app/telegram_bot.py`)

#### Modified Methods:
- **`show_task_details()`**: Now detects YouTube video quests and routes them to `start_video_quest()`
  - Checks if `task.platform == 'youtube'` and `verification_data.method == 'time_delay_code'`
  - Regular tasks continue with normal flow

#### New Methods Added:

**`start_video_quest(query, task)`**
- Calls `BotAPIClient.start_video_view()` to record start timestamp in database
- Displays video information with verification instructions
- Shows minimum watch time and code location hint
- Stores active task ID in user context for code verification
- Beautiful gaming-themed message with emojis

**`verify_video_code_handler(update, context)`**
- Handles text messages when user has active video quest
- Calls `BotAPIClient.verify_video_code()` with submitted code
- Handles 4 response scenarios:
  - ✅ **Success**: Quest completed, points awarded
  - ⏱️ **Too Soon**: User needs to watch more (shows time remaining)
  - ❌ **Wrong Code**: Incorrect code (shows attempts remaining)
  - 🚫 **Max Attempts**: All 3 attempts used, quest failed
- Clears active quest from user context on completion/failure

#### Handler Registration:
- Added `MessageHandler` for text messages (non-commands)
- Registered in `_register_handlers()` method
- Order: commands → callback queries → text messages

---

### 2. API Endpoints (`app/api.py`)

#### New Endpoints:

**POST `/api/video-views/start`**
```json
Request: {
  "user_id": "uuid",
  "task_id": "uuid"
}

Response: {
  "message": "Video view started",
  "view": {
    "id": "uuid",
    "user_id": "uuid",
    "task_id": "uuid",
    "verification_code": "QUEST2024",
    "status": "watching",
    "started_at": "2025-10-15T21:00:00Z",
    "code_attempts": 0
  }
}
```

**Features:**
- Validates task has video verification enabled
- Checks for existing active view (prevents duplicates)
- Creates `video_views` record with status "watching"
- Stores verification code from task's `verification_data`

**POST `/api/video-views/verify`**
```json
Request: {
  "user_id": "uuid",
  "code": "QUEST2024"
}

Response (Success): {
  "success": true,
  "message": "Video quest completed successfully!",
  "task": {...},
  "points_earned": 100,
  "time_watched_seconds": 150,
  "attempts_left": 2
}

Response (Too Soon): {
  "success": false,
  "error": "too_soon",
  "message": "Please watch more of the video",
  "time_watched_seconds": 90,
  "min_watch_time_seconds": 120,
  "time_remaining_seconds": 30,
  "attempts_left": 2
}

Response (Wrong Code): {
  "success": false,
  "error": "wrong_code",
  "message": "Incorrect verification code",
  "attempts_left": 1,
  "time_watched_seconds": 150
}

Response (Max Attempts): {
  "success": false,
  "error": "max_attempts",
  "message": "Maximum verification attempts reached",
  "attempts_left": 0
}
```

**Verification Logic:**
1. Find active video view by user_id + code
2. Check if max attempts (3) already reached → fail
3. Increment attempt counter
4. Validate code (case-insensitive comparison)
5. Calculate time watched: `now - started_at`
6. Check if `time_watched >= min_watch_time_seconds`
7. On success:
   - Update video_views status to "completed"
   - Create user_tasks record with status "verified"
   - Award points to user
   - Create notification
8. On failure:
   - Return appropriate error with remaining attempts
   - Mark as "failed" if no attempts left

---

### 3. API Client Methods (`app/bot_api_client.py`)

Already completed in Phase 1, but here's the summary:

**`start_video_view(user_id, task_id)`**
- POST to `/api/video-views/start`
- Returns view data or None on error

**`verify_video_code(user_id, code)`**
- POST to `/api/video-views/verify`
- Returns verification result with success/error details

---

## 🔄 Verification Flow

### User Interaction:
1. User clicks YouTube task button
2. Bot detects it's a video quest → calls `start_video_quest()`
3. Bot records start time in database
4. Bot shows video link + instructions
5. User watches video and finds secret code
6. User sends code as text message to bot
7. Bot calls `verify_video_code_handler()`
8. API validates:
   - Time elapsed ≥ min_watch_time
   - Code matches (case-insensitive)
   - Attempts < max_attempts
9. On success: Award points, complete task, send celebration
10. On failure: Send error with helpful feedback

### State Management:
- **Database**: `video_views` table tracks watching status
- **Bot Context**: `user_data[user_id]['active_video_task']` stores current task
- **Unique Constraint**: Only one active view per user-task at a time

---

## 🧪 Testing Guide

### Test YouTube Video Quest:

1. **Create YouTube Task via Admin Dashboard** (manual for now):
```sql
INSERT INTO tasks (title, description, platform, url, points_reward, verification_data, is_active)
VALUES (
  'Watch Gaming Tutorial',
  'Watch this 5-minute gaming tutorial and find the secret code!',
  'youtube',
  'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
  100,
  '{"method": "time_delay_code", "code": "GAMER2024", "min_watch_time_seconds": 120, "code_timestamp": "2:30", "max_attempts": 3}'::jsonb,
  true
);
```

2. **Test Flow in Telegram Bot**:
   - Send `/tasks` command
   - Click YouTube task
   - See verification instructions
   - Try submitting code too early → "watch more" message
   - Wait 2+ minutes, submit wrong code → "incorrect code" message
   - Submit correct code "GAMER2024" → success! 🎉

3. **Test API Endpoints with curl**:
```bash
# Start video view
curl -X POST http://localhost:8000/api/video-views/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_UUID", "task_id": "TASK_UUID"}'

# Verify code (too soon)
curl -X POST http://localhost:8000/api/video-views/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_UUID", "code": "GAMER2024"}'

# Wait 2 minutes, verify again (success)
sleep 120
curl -X POST http://localhost:8000/api/video-views/verify \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_UUID", "code": "GAMER2024"}'
```

---

## 📊 Database Queries for Testing

### Check video views:
```sql
SELECT 
  vv.id,
  u.username,
  t.title as task_title,
  vv.status,
  vv.code_attempts,
  vv.started_at,
  vv.completed_at,
  EXTRACT(EPOCH FROM (COALESCE(vv.completed_at, NOW()) - vv.started_at)) as seconds_elapsed
FROM video_views vv
JOIN users u ON vv.user_id = u.id
JOIN tasks t ON vv.task_id = t.id
ORDER BY vv.created_at DESC;
```

### Check task completions:
```sql
SELECT 
  u.username,
  t.title,
  ut.status,
  ut.completed_at
FROM user_tasks ut
JOIN users u ON ut.user_id = u.id
JOIN tasks t ON ut.task_id = t.id
WHERE t.platform = 'youtube'
ORDER BY ut.completed_at DESC;
```

---

## 🚀 Deployment Status

✅ **Containers Restarted**: Both API and Bot containers restarted successfully
✅ **Bot Polling**: Bot is polling Telegram API every 10 seconds
✅ **API Running**: FastAPI server running on port 8000
✅ **No Errors**: Clean startup logs, no Python exceptions

---

## 📝 Next Steps: Phase 3

### Admin Dashboard YouTube Quest Creation UI

**Files to Update:**
- `frontend/admin.html`

**Changes Needed:**
1. Add YouTube verification section in task creation modal
2. Fields to add:
   - Secret Code (text input)
   - Minimum Watch Time (number input, default 120 seconds / 2 minutes)
   - Code Timestamp Hint (text input, e.g., "2:30" or "at the end")
   - Max Attempts (number input, default 3)
3. Show/hide section based on platform selection
4. Update `submitTask()` to include `verification_data` object
5. Add video statistics dashboard:
   - Total views
   - Completed vs Failed
   - Average watch time
   - Code attempt distribution

**Suggested Implementation:**
```javascript
// In showAddTaskModal() - add after platform selection
if (taskPlatform === 'youtube') {
  // Show verification fields
  document.getElementById('youtubeVerification').style.display = 'block';
}

// In submitTask() - build verification_data
if (taskPlatform === 'youtube') {
  taskData.verification_data = {
    method: 'time_delay_code',
    code: document.getElementById('taskSecretCode').value,
    min_watch_time_seconds: parseInt(document.getElementById('taskMinWatchTime').value) || 120,
    code_timestamp: document.getElementById('taskCodeTimestamp').value || 'during the video',
    max_attempts: parseInt(document.getElementById('taskMaxAttempts').value) || 3
  };
}
```

---

## 🎮 Gaming Theme Integration

All bot messages use gaming-themed emojis and language:
- 🎬 Video quest icon
- 📺 Watch instruction
- ⏱️ Time delay feedback
- 🔍 Code verification
- 🎉 Success celebration
- 🚫 Failure notification
- 💰 Points reward
- 🏆 Leaderboard reference

Consistent with existing gaming UI in frontend!

---

## 🔐 Security Features

✅ **Server-side timing**: Can't manipulate time delays
✅ **Attempt limiting**: Max 3 code attempts prevents brute force
✅ **Case-insensitive codes**: Better UX, no case typos
✅ **Unique constraints**: One active view per user-task
✅ **Status tracking**: watching → completed/failed state machine
✅ **Code verification**: Stored in database, compared server-side

---

## 📚 Documentation

Related docs:
- `HYBRID_VIDEO_VERIFICATION.md` - Complete verification system guide
- `YOUTUBE_VERIFICATION.md` - Method comparison and analysis
- `database/migrations/001_video_views.sql` - Database schema
- This file - Phase 2 implementation details

---

**Phase 2 Status: ✅ COMPLETE**

Ready to proceed with Phase 3: Admin Dashboard UI updates!
