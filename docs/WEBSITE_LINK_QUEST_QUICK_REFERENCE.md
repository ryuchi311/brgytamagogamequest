# 🚀 Website Link Quest - Quick Reference Guide

## 📊 Visual Workflow

```
┌─────────────┐
│   ADMIN     │
│   PANEL     │
└──────┬──────┘
       │
       │ 1. Login
       ↓
┌──────────────────┐
│ Get JWT Token    │
└──────┬───────────┘
       │
       │ 2. Navigate
       ↓
┌──────────────────┐
│ Quest Selector   │
│ Click "Website"  │
└──────┬───────────┘
       │
       │ 3. Fill Form
       ↓
┌──────────────────────────────┐
│ Title: "Visit Our Website"   │
│ Points: 50                    │
│ URL: https://example.com      │
│ Mode: Auto ⭐ or Manual       │
└──────┬───────────────────────┘
       │
       │ 4. Submit (POST /api/tasks)
       ↓
┌─────────────────────────────────────────┐
│         BACKEND PROCESSING              │
│ ┌───────────────────────────────────┐   │
│ │ 1. Verify JWT Token               │   │
│ │ 2. Validate Data (Pydantic)       │   │
│ │ 3. Save to Database                │   │
│ │ 4. Notify Users                    │   │
│ └───────────────────────────────────┘   │
└─────────────────┬───────────────────────┘
                  │
                  │ 5. Quest Created
                  ↓
        ┌─────────────────┐
        │    DATABASE     │
        │   tasks table   │
        └─────────┬───────┘
                  │
                  │ 6. User Opens Bot
                  ↓
        ┌─────────────────┐
        │  TELEGRAM BOT   │
        │ Detects Quest   │
        └─────────┬───────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ↓                           ↓
┌────────────┐          ┌────────────┐
│ AUTO MODE  │          │MANUAL MODE │
│ (instant)  │          │  (review)  │
└─────┬──────┘          └─────┬──────┘
      │                       │
      │ Shows:                │ Shows:
      │ • Visit button        │ • Start button
      │ • Claim button        │ • Submit form
      │                       │
      ↓                       ↓
┌─────────────┐         ┌──────────────┐
│ User Clicks │         │ User Submits │
│ "Claim"     │         │ For Review   │
└─────┬───────┘         └──────┬───────┘
      │                        │
      │ Instant!               │ Wait for admin
      ↓                        ↓
┌────────────┐          ┌──────────────┐
│ Points +50 │          │ Admin Reviews│
│ Done! 🎉   │          │ Then +50 pts │
└────────────┘          └──────────────┘
```

---

## 🔑 Key Fields

### Frontend → Backend

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `title` | string | "Visit Our Website" | Quest name |
| `description` | string | "Visit our homepage..." | Quest instructions |
| `points_reward` | int | 50 | Points to award |
| `is_active` | bool | true | Active/Inactive |
| `task_type` | string | "link" | Fixed: "link" |
| `platform` | string | "website" | Fixed: "website" |
| `url` | string | "https://..." | Website URL |
| `verification_required` | bool | false | false=Auto, true=Manual |
| `verification_data` | object | {...} | Metadata |

### Backend → Database

Same fields as above, stored in `tasks` table.

### Database Detection Logic

```python
# Bot checks these 3 conditions:
is_auto = (
    task_type == 'link' AND
    platform == 'website' AND
    verification_required == False
)
```

If ALL 3 match → Auto-complete flow  
Otherwise → Manual verification flow

---

## 📝 Code Snippets

### Frontend: Submit Quest

```javascript
const questData = {
    title: "Visit Our Website",
    description: "Check out our homepage",
    points_reward: 50,
    is_active: true,
    task_type: 'link',           // Fixed
    platform: 'website',         // Fixed
    url: 'https://example.com',
    verification_required: false, // false=Auto, true=Manual
    verification_data: {
        type: 'website_visit',
        method: 'auto'           // 'auto' or 'manual'
    }
};

const response = await fetch(`${API_URL}/tasks`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify(questData)
});
```

### Backend: Validate & Save

```python
@app.post("/api/tasks")
async def create_task(task: TaskCreate, admin=Depends(get_current_admin)):
    task_data = {
        "title": task.title,
        "task_type": task.task_type,      # 'link'
        "platform": task.platform,        # 'website'
        "url": task.url,
        "verification_required": task.verification_required,  # false for auto
        # ... other fields
    }
    
    response = supabase.table("tasks").insert(task_data).execute()
    return response.data[0]
```

### Bot: Detect & Route

```python
# Check if auto-complete
is_auto = (
    task['task_type'] == 'link' and
    task['platform'] == 'website' and
    not task['verification_required']
)

if is_auto:
    await self.start_auto_link_quest(query, task)
else:
    await self.start_manual_quest(query, task)
```

### Bot: Instant Reward

```python
async def claim_auto_quest_points(self, query, task_id):
    # No verification - instant completion!
    result = BotAPIClient.complete_task(user_id, task_id)
    
    if result and 'error' not in result:
        # Award points immediately
        await query.edit_message_text(
            f"🎉 You earned {task['points_reward']} points!"
        )
```

---

## 🎯 Quick Checklist

### Creating Auto-Complete Quest

- [ ] Login to admin panel
- [ ] Click "CREATE QUEST"
- [ ] Click "🔗 Website Link" card
- [ ] Fill in:
  - [ ] Title (required)
  - [ ] Description (required)
  - [ ] Points (default: 50)
  - [ ] Status: Active
  - [ ] Website URL (must start with http:// or https://)
  - [ ] **Verification: Auto-Complete** ⭐
- [ ] Click "🚀 CREATE WEBSITE QUEST"
- [ ] Check for success message
- [ ] Verify in admin panel

### Creating Manual Quest

Same as above, but:
- [ ] **Verification: Manual Verification** ⚠️

### Testing Auto-Complete Quest

- [ ] Open Telegram bot as user
- [ ] View available quests
- [ ] Find website quest (should say "INSTANT REWARD")
- [ ] Click "🌐 Visit Website" button
- [ ] Website opens in browser
- [ ] Return to bot
- [ ] Click "✅ I Visited - Claim Points"
- [ ] Instant success message!
- [ ] Points added to balance

### Testing Manual Quest

- [ ] Open Telegram bot as user
- [ ] View available quests
- [ ] Find website quest (standard quest UI)
- [ ] Click "Start Quest"
- [ ] Click URL to visit
- [ ] Return to bot
- [ ] Click "Complete Quest"
- [ ] Wait for admin approval
- [ ] Admin approves in panel
- [ ] Points added to balance

---

## 🔧 Troubleshooting

### Problem: 401 Unauthorized

**Quick Fix**:
```javascript
// Check token exists
console.log('Token:', localStorage.getItem('authToken'));

// If null → Login again
// If exists but fails → Token expired, login again
```

### Problem: Quest Not Auto-Complete

**Quick Fix**:
```sql
-- Check database
SELECT id, task_type, platform, verification_required 
FROM tasks 
WHERE id = 'your-quest-id';

-- Should be:
-- task_type = 'link'
-- platform = 'website'  
-- verification_required = false
```

### Problem: URL Not Opening

**Quick Fix**:
- Ensure URL starts with `https://` or `http://`
- Test URL in browser first
- Check for typos

### Problem: Points Not Awarded

**Quick Fix**:
```sql
-- Check if already completed
SELECT * FROM user_tasks 
WHERE user_id = 'user-id' AND task_id = 'task-id';

-- If exists → Already completed
-- If not exists → Check API logs for errors
```

---

## 💡 Pro Tips

### For Admins

1. **Use Auto-Complete for**:
   - Simple traffic generation
   - Blog post views
   - Product page visits
   - Landing page traffic

2. **Use Manual for**:
   - When you need proof
   - When tracking specific actions
   - When preventing abuse

3. **Point Values**:
   - Simple visits: 10-50 points
   - Long articles: 50-100 points
   - Important pages: 100-200 points

### For Developers

1. **Always validate URLs** before saving
2. **Log everything** for debugging
3. **Handle errors gracefully**
4. **Test both verification modes**
5. **Monitor completion rates**

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `frontend/create-website-quest.html` | Admin creation form |
| `app/api.py` | Backend API endpoint |
| `app/telegram_bot.py` | Bot logic & detection |
| `database/schema.sql` | Database structure |
| `WEBSITE_LINK_QUEST_WORKFLOW.md` | Full documentation |

---

## 🎯 Success Criteria

✅ Admin can create quest in < 1 minute  
✅ User can complete auto-quest in < 30 seconds  
✅ No 401 errors on quest creation  
✅ Points awarded instantly for auto-complete  
✅ Clear distinction between auto and manual modes  

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
