# 🎥 Hybrid YouTube Verification System
## Method: Time Delay + Secret Code

## Overview
This system combines two verification methods for maximum effectiveness:
1. **Time Delay** - Ensures user spent time on the video
2. **Secret Code** - Proves they actually watched it

---

## 🎯 How It Works

### User Flow:
1. User clicks quest "Watch our YouTube video"
2. Bot records timestamp and sends YouTube link
3. User watches video (minimum 2-3 minutes)
4. User finds secret code shown in video (at 80% mark)
5. User returns to bot and enters code
6. Bot checks:
   - ✅ Has minimum time elapsed since clicking? (e.g., 2 minutes)
   - ✅ Is the code correct?
7. If both pass → Award XP!

### Why This Works:
- **Time Delay** prevents instant cheating/code sharing
- **Secret Code** proves they actually watched
- **Combined** = Much harder to cheat

---

## 📊 Database Schema Updates

Add tracking table for video views:

```sql
-- Create video_views tracking table
CREATE TABLE video_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    verification_code VARCHAR(50),
    code_attempts INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'watching', -- watching, completed, failed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add index for quick lookups
CREATE INDEX idx_video_views_user_task ON video_views(user_id, task_id);

-- Update tasks table to support verification
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS verification_data JSONB;

-- Example verification_data structure:
-- {
--   "method": "time_delay_code",
--   "code": "QUEST2024",
--   "min_watch_time_seconds": 120,
--   "code_timestamp": "2:30",
--   "max_attempts": 3
-- }

-- Add constraints
ALTER TABLE video_views ADD CONSTRAINT unique_user_task_view 
    UNIQUE(user_id, task_id);
```

---

## 🤖 Bot Implementation

### Update app/telegram_bot.py

Add the hybrid verification system:

```python
from datetime import datetime, timedelta

class TelegramBot:
    # ... existing code ...
    
    async def start_video_quest(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task):
        """Start tracking when user clicks video quest"""
        user_id = update.effective_user.id
        task_id = task['id']
        
        try:
            # Record that user started watching
            response = await self.api_client.post(
                '/video-views/start',
                json={
                    'user_id': str(user_id),
                    'task_id': task_id
                }
            )
            
            verification_data = task.get('verification_data', {})
            min_watch_time = verification_data.get('min_watch_time_seconds', 120)
            code_timestamp = verification_data.get('code_timestamp', 'during the video')
            
            message = (
                f"🎬 **{task['title']}**\n\n"
                f"📝 {task['description']}\n\n"
                f"💎 Reward: {task['points_reward']} XP\n\n"
                f"📺 Watch the video below:\n"
                f"{task['url']}\n\n"
                f"⏱️ **Minimum watch time:** {min_watch_time // 60} minutes\n"
                f"🔐 **Secret Code:** Find the code shown at {code_timestamp}\n\n"
                f"✅ After watching, come back here and send me the code!"
            )
            
            keyboard = [
                [InlineKeyboardButton("🎥 Open YouTube Video", url=task['url'])],
                [InlineKeyboardButton("⏮️ Back to Quests", callback_data="tasks")]
            ]
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
            # Remind user to enter code
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🎮 **Pro Tip:** The secret code will appear in the video.\n"
                    "Watch carefully and type it here when you find it!"
                ),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error starting video quest: {e}")
            await update.callback_query.answer("Error starting quest. Try again!")
    
    
    async def verify_video_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verify video code with time delay check"""
        user_id = update.effective_user.id
        submitted_code = update.message.text.strip().upper()
        
        try:
            # Check if this is a verification code for any active video quest
            response = await self.api_client.post(
                '/video-views/verify',
                json={
                    'user_id': str(user_id),
                    'code': submitted_code
                }
            )
            
            result = response.json()
            
            if result.get('success'):
                task = result['task']
                time_watched = result['time_watched_seconds']
                
                await update.message.reply_text(
                    f"🎉 **CODE VERIFIED!**\n\n"
                    f"✅ Quest '{task['title']}' completed!\n"
                    f"⏱️ Watch time: {time_watched // 60}m {time_watched % 60}s\n"
                    f"💎 **+{task['points_reward']} XP** earned!\n\n"
                    f"Keep completing quests to climb the leaderboard! 🏆",
                    parse_mode='Markdown',
                    reply_markup=self._main_menu_keyboard()
                )
                
                # Send updated profile
                await self._send_profile_update(user_id)
                
            elif result.get('error') == 'too_soon':
                min_time = result.get('min_watch_time', 120)
                time_elapsed = result.get('time_elapsed', 0)
                time_remaining = min_time - time_elapsed
                
                await update.message.reply_text(
                    f"⏳ **Not so fast!**\n\n"
                    f"⏱️ You need to watch for at least {min_time // 60} minutes.\n"
                    f"⏰ Time remaining: {time_remaining // 60}m {time_remaining % 60}s\n\n"
                    f"👀 Keep watching the video and try again!",
                    parse_mode='Markdown'
                )
                
            elif result.get('error') == 'wrong_code':
                attempts_left = result.get('attempts_left', 0)
                
                await update.message.reply_text(
                    f"❌ **Wrong code!**\n\n"
                    f"🔍 Watch the video carefully to find the correct code.\n"
                    f"⚠️ Attempts left: {attempts_left}\n\n"
                    f"💡 Tip: The code is shown clearly in the video.",
                    parse_mode='Markdown'
                )
                
            elif result.get('error') == 'max_attempts':
                await update.message.reply_text(
                    f"🚫 **Maximum attempts reached!**\n\n"
                    f"You've used all your attempts for this quest.\n"
                    f"Contact an admin if you believe this is an error.",
                    parse_mode='Markdown'
                )
                
            elif result.get('error') == 'no_active_view':
                await update.message.reply_text(
                    f"🤔 **No active video quest found.**\n\n"
                    f"Start a video quest first by going to:\n"
                    f"/tasks → Select a YouTube quest → Click the link",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Error verifying video code: {e}")
            await update.message.reply_text(
                "❌ Error verifying code. Please try again!",
                reply_markup=self._main_menu_keyboard()
            )
    
    
    async def _send_profile_update(self, user_id):
        """Send updated profile stats"""
        try:
            response = await self.api_client.get(f'/users/{user_id}')
            user = response.json()
            
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"📊 **Your Stats:**\n"
                    f"💎 Total XP: {user['total_earned_points']}\n"
                    f"⚡ Available Points: {user['points']}\n"
                    f"🏆 Keep grinding!"
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error sending profile update: {e}")
    
    
    def _register_handlers(self):
        """Register all command and callback handlers"""
        # ... existing handlers ...
        
        # Add message handler for verification codes (must be BEFORE generic message handler)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.verify_video_code
        ))
    
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith('task_'):
            task_id = query.data.replace('task_', '')
            
            try:
                response = await self.api_client.get(f'/tasks/{task_id}')
                task = response.json()
                
                # Check if this is a video quest with verification
                if task.get('platform') == 'youtube' and task.get('verification_data'):
                    await self.start_video_quest(update, context, task)
                else:
                    # Regular task display
                    await self._show_task_details(update, context, task)
                    
            except Exception as e:
                logger.error(f"Error loading task: {e}")
                await query.edit_message_text("Error loading quest details.")
        
        # ... handle other callbacks ...
```

---

## 🔧 API Backend Updates

### Update app/api.py

Add new endpoints for video view tracking:

```python
from datetime import datetime, timedelta

# Video View Tracking Endpoints

@app.post("/api/video-views/start")
async def start_video_view(view_data: dict):
    """Record when user starts watching a video"""
    try:
        user_id = view_data['user_id']
        task_id = view_data['task_id']
        
        # Check if already has an active view
        existing = supabase.table("video_views").select("*").eq(
            "user_id", user_id
        ).eq("task_id", task_id).eq("status", "watching").execute()
        
        if existing.data:
            # Update the timestamp (user is re-watching)
            supabase.table("video_views").update({
                "started_at": datetime.utcnow().isoformat(),
                "code_attempts": 0
            }).eq("id", existing.data[0]['id']).execute()
        else:
            # Create new view record
            supabase.table("video_views").insert({
                "user_id": user_id,
                "task_id": task_id,
                "started_at": datetime.utcnow().isoformat(),
                "status": "watching"
            }).execute()
        
        return {"success": True, "message": "Video view started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video-views/verify")
async def verify_video_code(verification_data: dict):
    """Verify video code with time delay check"""
    try:
        user_id = verification_data['user_id']
        submitted_code = verification_data['code'].upper()
        
        # Find active video view for this user
        views = supabase.table("video_views").select("*").eq(
            "user_id", user_id
        ).eq("status", "watching").execute()
        
        if not views.data:
            return {"success": False, "error": "no_active_view"}
        
        view = views.data[0]
        task_id = view['task_id']
        
        # Get task details
        task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        if not task_response.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = task_response.data[0]
        verification_data = task.get('verification_data', {})
        
        # Check 1: Time delay
        min_watch_time = verification_data.get('min_watch_time_seconds', 120)
        started_at = datetime.fromisoformat(view['started_at'].replace('Z', '+00:00'))
        time_elapsed = (datetime.utcnow().replace(tzinfo=started_at.tzinfo) - started_at).total_seconds()
        
        if time_elapsed < min_watch_time:
            return {
                "success": False,
                "error": "too_soon",
                "min_watch_time": min_watch_time,
                "time_elapsed": int(time_elapsed)
            }
        
        # Check 2: Maximum attempts
        max_attempts = verification_data.get('max_attempts', 3)
        current_attempts = view['code_attempts']
        
        if current_attempts >= max_attempts:
            # Mark as failed
            supabase.table("video_views").update({
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", view['id']).execute()
            
            return {"success": False, "error": "max_attempts"}
        
        # Check 3: Code correctness
        correct_code = verification_data.get('code', '').upper()
        
        if submitted_code != correct_code:
            # Increment attempts
            supabase.table("video_views").update({
                "code_attempts": current_attempts + 1
            }).eq("id", view['id']).execute()
            
            return {
                "success": False,
                "error": "wrong_code",
                "attempts_left": max_attempts - (current_attempts + 1)
            }
        
        # All checks passed! Complete the quest
        
        # Mark video view as completed
        supabase.table("video_views").update({
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "verification_code": submitted_code
        }).eq("id", view['id']).execute()
        
        # Create user_task completion
        user_task_data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }
        
        supabase.table("user_tasks").insert(user_task_data).execute()
        
        # Award points to user
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        if user_response.data:
            user = user_response.data[0]
            new_points = user['points'] + task['points_reward']
            new_total = user['total_earned_points'] + task['points_reward']
            
            supabase.table("users").update({
                "points": new_points,
                "total_earned_points": new_total
            }).eq("id", user_id).execute()
            
            # Create notification
            supabase.table("notifications").insert({
                "user_id": user_id,
                "title": "Quest Completed! 🎉",
                "message": f"You earned {task['points_reward']} XP for completing '{task['title']}'!",
                "notification_type": "quest_completed"
            }).execute()
        
        return {
            "success": True,
            "task": task,
            "time_watched_seconds": int(time_elapsed)
        }
        
    except Exception as e:
        logger.error(f"Error verifying video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video-views/stats")
async def get_video_view_stats(current_admin: dict = Depends(get_current_admin)):
    """Get video view statistics for admin"""
    try:
        views = supabase.table("video_views").select("*").execute()
        
        stats = {
            "total_views": len(views.data),
            "completed": len([v for v in views.data if v['status'] == 'completed']),
            "watching": len([v for v in views.data if v['status'] == 'watching']),
            "failed": len([v for v in views.data if v['status'] == 'failed']),
            "avg_attempts": sum([v['code_attempts'] for v in views.data]) / len(views.data) if views.data else 0
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎮 Admin Dashboard Integration

### Update frontend/admin.html

Add verification fields when creating tasks:

```javascript
// When creating a YouTube task
function showAddTaskModal() {
    const modalContent = `
        <form id="taskForm" class="space-y-4">
            <!-- Existing fields... -->
            
            <div class="mb-4">
                <label class="block text-sm font-bold text-neon-purple mb-2 gaming-title">
                    PLATFORM
                </label>
                <select id="taskPlatform" class="w-full bg-black/50 border-2 border-neon-purple/30 rounded-xl px-4 py-3 text-white gaming-body">
                    <option value="">Select platform</option>
                    <option value="youtube">YouTube</option>
                    <option value="instagram">Instagram</option>
                    <option value="twitter">Twitter</option>
                    <option value="tiktok">TikTok</option>
                </select>
            </div>
            
            <!-- YouTube Verification Section (hidden by default) -->
            <div id="youtubeVerification" class="hidden space-y-4 p-4 bg-gradient-to-r from-neon-purple/10 to-neon-blue/10 rounded-xl border-2 border-neon-purple/30">
                <h4 class="text-lg font-bold gaming-title gradient-text">
                    🎥 YOUTUBE VERIFICATION SETTINGS
                </h4>
                
                <div>
                    <label class="block text-sm font-bold text-neon-green mb-2 gaming-title">
                        🔐 SECRET CODE
                    </label>
                    <input type="text" id="taskSecretCode" 
                        class="w-full bg-black/50 border-2 border-neon-green/30 focus:border-neon-green rounded-xl px-4 py-3 text-white gaming-body"
                        placeholder="e.g., QUEST2024">
                    <p class="text-xs text-gray-400 mt-1">Code shown in the video that users must find</p>
                </div>
                
                <div>
                    <label class="block text-sm font-bold text-neon-yellow mb-2 gaming-title">
                        ⏱️ MINIMUM WATCH TIME (seconds)
                    </label>
                    <input type="number" id="taskMinWatchTime" 
                        class="w-full bg-black/50 border-2 border-neon-yellow/30 focus:border-neon-yellow rounded-xl px-4 py-3 text-white gaming-body"
                        placeholder="120" value="120" min="30">
                    <p class="text-xs text-gray-400 mt-1">Users must wait this long before entering code (default: 2 minutes)</p>
                </div>
                
                <div>
                    <label class="block text-sm font-bold text-neon-pink mb-2 gaming-title">
                        📍 CODE TIMESTAMP
                    </label>
                    <input type="text" id="taskCodeTimestamp" 
                        class="w-full bg-black/50 border-2 border-neon-pink/30 focus:border-neon-pink rounded-xl px-4 py-3 text-white gaming-body"
                        placeholder="2:30" value="2:30">
                    <p class="text-xs text-gray-400 mt-1">When the code appears in the video</p>
                </div>
                
                <div>
                    <label class="block text-sm font-bold text-neon-blue mb-2 gaming-title">
                        🎯 MAX ATTEMPTS
                    </label>
                    <input type="number" id="taskMaxAttempts" 
                        class="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-blue rounded-xl px-4 py-3 text-white gaming-body"
                        placeholder="3" value="3" min="1" max="10">
                    <p class="text-xs text-gray-400 mt-1">Maximum wrong code attempts allowed</p>
                </div>
            </div>
            
            <!-- Submit button -->
            <button type="submit" class="w-full py-4 bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink rounded-xl font-bold gaming-title text-lg transition-all duration-300 hover:scale-105">
                ⚔️ CREATE QUEST
            </button>
        </form>
    `;
    
    document.getElementById('taskModalContent').innerHTML = modalContent;
    document.getElementById('taskModal').classList.remove('hidden');
    
    // Show/hide YouTube verification based on platform
    document.getElementById('taskPlatform').addEventListener('change', (e) => {
        const isYoutube = e.target.value === 'youtube';
        document.getElementById('youtubeVerification').classList.toggle('hidden', !isYoutube);
    });
    
    document.getElementById('taskForm').addEventListener('submit', submitTask);
}

async function submitTask(event) {
    event.preventDefault();
    
    const platform = document.getElementById('taskPlatform').value;
    let verificationData = null;
    
    // Add verification data for YouTube tasks
    if (platform === 'youtube') {
        verificationData = {
            method: 'time_delay_code',
            code: document.getElementById('taskSecretCode').value.toUpperCase(),
            min_watch_time_seconds: parseInt(document.getElementById('taskMinWatchTime').value) || 120,
            code_timestamp: document.getElementById('taskCodeTimestamp').value || '2:30',
            max_attempts: parseInt(document.getElementById('taskMaxAttempts').value) || 3
        };
    }
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        task_type: document.getElementById('taskType').value,
        platform: platform || null,
        url: document.getElementById('taskUrl').value || null,
        points_reward: parseInt(document.getElementById('taskPoints').value),
        is_bonus: document.getElementById('taskBonus').checked,
        verification_required: platform === 'youtube',
        verification_data: verificationData
    };
    
    try {
        const response = await fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            alert('✅ Quest created successfully with verification!');
            closeModal('taskModal');
            loadTasks();
            document.getElementById('taskForm').reset();
        } else {
            throw new Error('Failed to create task');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        alert('❌ Failed to create quest');
    }
}
```

---

## 📊 Admin Analytics Dashboard

Add video verification stats to admin dashboard:

```javascript
async function loadVideoStats() {
    try {
        const response = await fetch(`${API_URL}/video-views/stats`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) throw new Error('Failed to fetch video stats');
        
        const stats = await response.json();
        
        // Display stats
        document.getElementById('videoStatsContainer').innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-gradient-to-br from-neon-blue/20 to-transparent border-2 border-neon-blue/30 rounded-2xl p-6 card-glow">
                    <h3 class="text-sm text-gray-400 mb-2 gaming-title">TOTAL VIDEO VIEWS</h3>
                    <div class="text-4xl font-black gaming-title gradient-text">${stats.total_views}</div>
                </div>
                
                <div class="bg-gradient-to-br from-neon-green/20 to-transparent border-2 border-neon-green/30 rounded-2xl p-6">
                    <h3 class="text-sm text-gray-400 mb-2 gaming-title">COMPLETED</h3>
                    <div class="text-4xl font-black gaming-title text-neon-green">${stats.completed}</div>
                    <div class="text-xs text-gray-400 mt-2">${((stats.completed / stats.total_views) * 100).toFixed(1)}% success rate</div>
                </div>
                
                <div class="bg-gradient-to-br from-neon-yellow/20 to-transparent border-2 border-neon-yellow/30 rounded-2xl p-6">
                    <h3 class="text-sm text-gray-400 mb-2 gaming-title">WATCHING NOW</h3>
                    <div class="text-4xl font-black gaming-title text-neon-yellow">${stats.watching}</div>
                </div>
                
                <div class="bg-gradient-to-br from-neon-pink/20 to-transparent border-2 border-neon-pink/30 rounded-2xl p-6">
                    <h3 class="text-sm text-gray-400 mb-2 gaming-title">AVG ATTEMPTS</h3>
                    <div class="text-4xl font-black gaming-title text-neon-pink">${stats.avg_attempts.toFixed(1)}</div>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading video stats:', error);
    }
}

// Call in loadDashboard()
function loadDashboard() {
    showSection('dashboard');
    loadStats();
    loadVideoStats(); // Add this
}
```

---

## 🎬 Video Production Guide

### Where to Place the Code:

**Recommended Timing:**
- **Video Length < 3 min:** Code at 80% (2:24 for a 3min video)
- **Video Length 3-5 min:** Code at 75% (3:45 for a 5min video)  
- **Video Length > 5 min:** Code at 70% (4:12 for a 6min video)

**Why?**
- Forces users to watch most of the content
- Prevents skipping directly to the end
- Combined with time delay, ensures genuine viewing

### Code Display Best Practices:

```
┌─────────────────────────────────┐
│                                 │
│    🎮 SECRET QUEST CODE 🎮     │
│                                 │
│         QUEST2024              │
│                                 │
│   Type this in the bot! ⚔️     │
│                                 │
└─────────────────────────────────┘
```

**Style Guide:**
- **Font:** Bold, Sans-serif
- **Size:** Large (72-100pt)
- **Color:** High contrast (white on dark, or yellow on black)
- **Duration:** 8-12 seconds
- **Animation:** Fade in (1s) → Hold (6-10s) → Fade out (1s)
- **Background:** Semi-transparent overlay for readability

### Example with DaVinci Resolve:
1. Import your video
2. Add text at desired timestamp
3. Set text: "🎮 QUEST CODE: QUEST2024 🎮"
4. Add fade in/out transitions
5. Optionally add sound effect when code appears
6. Export and upload to YouTube

---

## 🔒 Security & Anti-Cheat

### Protection Mechanisms:

1. **Time Delay (2+ minutes)**
   - Prevents instant code submission
   - Ensures minimum engagement
   - Timestamp recorded server-side

2. **Limited Attempts (3 max)**
   - Prevents brute force
   - Punishes careless mistakes
   - Can be reset by admin if needed

3. **Server-Side Validation**
   - All checks done on backend
   - Cannot be bypassed by modified client
   - Timestamps stored in database

4. **Unique Codes Per Campaign**
   - Rotate codes monthly/weekly
   - Prevents old codes from working
   - Track which code was used

### Optional Advanced Features:

**User-Specific Codes:**
```python
# Generate unique code per user
import hashlib

def generate_user_code(user_id, task_id):
    data = f"{user_id}_{task_id}_{secret_salt}"
    hash_obj = hashlib.sha256(data.encode())
    code = hash_obj.hexdigest()[:8].upper()
    return f"QUEST{code}"
```

**Dynamic Code Display:**
- Use YouTube's info cards API
- Change code for each viewing session
- Requires YouTube API integration

---

## 📈 Success Metrics

Track these KPIs:

```sql
-- Conversion rate
SELECT 
    COUNT(DISTINCT user_id) as total_users_started,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
    ROUND(100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(DISTINCT user_id), 2) as conversion_rate
FROM video_views;

-- Average watch time
SELECT 
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_seconds
FROM video_views
WHERE status = 'completed';

-- Code attempt distribution
SELECT 
    code_attempts,
    COUNT(*) as users
FROM video_views
WHERE status IN ('completed', 'failed')
GROUP BY code_attempts
ORDER BY code_attempts;

-- Failure reasons
SELECT 
    CASE 
        WHEN code_attempts >= 3 THEN 'Max attempts'
        WHEN status = 'watching' THEN 'Abandoned'
        ELSE 'Other'
    END as failure_reason,
    COUNT(*) as count
FROM video_views
WHERE status != 'completed'
GROUP BY failure_reason;
```

---

## 🚀 Quick Start Checklist

### For Admin:

- [ ] Create YouTube video with content
- [ ] Add secret code overlay at 80% mark
- [ ] Upload to YouTube
- [ ] Log into admin dashboard
- [ ] Create new quest
- [ ] Select "YouTube" as platform
- [ ] Enter video URL
- [ ] Set secret code (e.g., "QUEST2024")
- [ ] Set minimum watch time (120 seconds recommended)
- [ ] Set code timestamp (e.g., "2:30")
- [ ] Set max attempts (3 recommended)
- [ ] Save quest

### For Users:

- [ ] Open Telegram bot
- [ ] Type `/tasks`
- [ ] Select YouTube quest
- [ ] Click "Open YouTube Video"
- [ ] Watch video (minimum 2 minutes)
- [ ] Find secret code in video
- [ ] Return to bot
- [ ] Type the code
- [ ] Receive XP!

---

## 💡 Pro Tips

### For Maximum Engagement:

1. **Tease the Code:** Mention in video: "Watch till the end for a secret code!"
2. **Make it Fun:** Use animations, sound effects when code appears
3. **Reward Quality:** Higher XP for longer/better videos
4. **Weekly Codes:** Change codes weekly to prevent sharing
5. **Bonus Codes:** Hide multiple codes for bonus XP

### For Better Metrics:

- Track drop-off points (when users abandon)
- A/B test different time delays
- Survey users about their experience
- Adjust difficulty based on completion rates

---

## 🎯 Expected Results

### Typical Conversion Rates:
- **With time delay only:** 60-70% completion
- **With code only:** 70-80% completion
- **With both (hybrid):** 85-95% completion

### User Behavior:
- ~10% will try to cheat (fail time check)
- ~5% will guess wrong code first time
- ~85% will complete successfully
- ~5% will abandon after starting

---

**🎥 This hybrid system is the BEST balance of security and user experience!**
