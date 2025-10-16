# Quest Creation System - Complete Guide

## Overview
The admin dashboard now supports **4 different quest types**, each with its own verification method and configuration options.

## Quest Types

### 1. 🐦 Twitter Quest
**Best for:** Social media engagement, growing Twitter following

#### Configuration Options:
- **Action Types:**
  - **Follow Account** - User must follow a Twitter account
  - **Like Tweet** - User must like a specific tweet
  - **Retweet** - User must retweet a specific tweet
  - **Reply to Tweet** - User must reply to a tweet

#### Required Fields:
- Quest Title
- Description
- XP Reward
- Target Username (without @)
- Tweet URL (for like/retweet/reply actions)

#### Verification Method:
- **Auto-verification via Twitter API v2**
- Uses free tier (100 reads/day)
- 24-hour caching to conserve rate limits
- Real-time verification when user completes quest

#### Example Configuration:
```json
{
  "title": "Follow us on Twitter",
  "description": "Follow @YourCompany for daily updates!",
  "points_reward": 100,
  "platform": "twitter",
  "verification_data": {
    "method": "twitter_api",
    "type": "follow",
    "username": "YourCompany"
  }
}
```

---

### 2. 📺 YouTube Quest
**Best for:** Video engagement, watch time, content promotion

#### Configuration Options:
- **YouTube Video URL** - Full YouTube link
- **Secret Code** - Code shown in the video (e.g., "QUEST2025")
- **Minimum Watch Time** - Seconds user must watch (default: 120)
- **Maximum Attempts** - Code entry attempts allowed (default: 3)
- **Code Hint** - When code appears (e.g., "at 2:30" or "at the end")

#### Required Fields:
- Quest Title
- Description
- XP Reward
- YouTube Video URL
- Secret Code

#### Verification Method:
- **Time-delay + Code verification**
- System tracks watch time from video start
- User must watch minimum time before code submission
- Limited attempts to prevent guessing
- Failed attempts tracked

#### How It Works:
1. User clicks "Start Quest"
2. System tracks video watch time
3. User finds secret code in video
4. After minimum watch time, user submits code
5. System verifies code and awards points

#### Example Configuration:
```json
{
  "title": "Watch Tutorial: Getting Started",
  "description": "Watch our complete tutorial and enter the code shown at the end",
  "points_reward": 200,
  "platform": "youtube",
  "url": "https://youtube.com/watch?v=abc123",
  "verification_data": {
    "method": "time_delay_code",
    "code": "TUTORIAL2025",
    "min_watch_time_seconds": 180,
    "code_timestamp": "at the end of the video",
    "max_attempts": 3
  }
}
```

---

### 3. 📅 Daily Check-in Quest
**Best for:** Daily engagement, user retention, habit building

#### Configuration Options:
- **Streak Bonus:**
  - None - Same points every day
  - Multiply by Streak - Day 7 = 7x points
  - Milestone Bonuses - Extra points on day 7, 30, 100
- **Reset Time** - When quest resets daily (UTC timezone)
- **Consecutive Required** - Whether missing a day breaks the streak

#### Required Fields:
- Quest Title
- Description
- Base XP Reward
- Streak Bonus Type
- Reset Time

#### Verification Method:
- **Auto-complete (button click)**
- One completion per day
- Streak tracking in database
- Automatic reset at configured time

#### Streak Calculation:
**No Bonus:**
- Day 1: 50 XP
- Day 2: 50 XP
- Day 7: 50 XP

**Multiply by Streak:**
- Day 1: 50 XP
- Day 2: 100 XP
- Day 7: 350 XP

**Milestone Bonuses:**
- Day 1-6: 50 XP
- Day 7: 100 XP (bonus)
- Day 30: 500 XP (huge bonus)
- Day 100: 2000 XP (legendary bonus)

#### Example Configuration:
```json
{
  "title": "Daily Login Bonus",
  "description": "Check in every day to build your streak!",
  "points_reward": 50,
  "platform": "daily",
  "task_type": "daily",
  "verification_data": {
    "method": "daily_checkin",
    "streak_bonus": "milestone",
    "reset_time_utc": "00:00",
    "consecutive_required": true,
    "frequency": "daily"
  }
}
```

---

### 4. ✍️ Manual Verification Quest
**Best for:** Complex tasks, off-platform activities, flexible verification

#### Configuration Options:
- **Quest URL** - Optional external link
- **Submission Types:**
  - None - No submission needed
  - Text/Link - User submits text or URL
  - Screenshot - User uploads image proof
  - Enter Code - User enters a code you provide
- **Instructions** - Detailed steps for users

#### Required Fields:
- Quest Title
- Description
- XP Reward
- Submission Type
- User Instructions

#### Verification Method:
- **Admin manual review**
- User submits proof/completion
- Admin reviews in dashboard
- Admin approves or rejects
- Points awarded on approval

#### Use Cases:
- Join Discord server
- Create content (art, video, etc.)
- Participate in event
- Complete survey
- Off-platform actions

#### Example Configuration:
```json
{
  "title": "Join Our Discord Community",
  "description": "Join our Discord and introduce yourself in #introductions",
  "points_reward": 150,
  "platform": "manual",
  "url": "https://discord.gg/yourserver",
  "verification_data": {
    "method": "manual_review",
    "submission_type": "text",
    "instructions": "1. Join Discord server\n2. Go to #introductions\n3. Post your intro\n4. Submit your Discord username here",
    "requires_approval": true
  }
}
```

---

## Admin Dashboard - How to Create Quest

### Step 1: Open Quest Creation Modal
- Navigate to Admin Dashboard → Quests tab
- Click "⚔️ CREATE NEW QUEST" button

### Step 2: Select Quest Type
Choose from 4 quest types:
- 🐦 **Twitter** - Social media tasks
- 📺 **YouTube** - Video watching tasks
- 📅 **Daily Check-in** - Recurring daily tasks
- ✍️ **Manual** - Flexible manual review tasks

### Step 3: Fill Common Fields
All quest types require:
- **Quest Title** - Short, clear name
- **Description** - What user needs to do
- **XP Reward** - Points awarded on completion

### Step 4: Configure Type-Specific Settings
Fill in the fields specific to your chosen quest type (see sections above)

### Step 5: Create Quest
- Click "🚀 CREATE QUEST" button
- Quest appears in active quests list
- Users can now see and complete it

---

## Verification Methods Comparison

| Quest Type | Verification | Speed | Rate Limits | Admin Work |
|------------|--------------|-------|-------------|------------|
| Twitter | API Auto | Instant | 100/day | None |
| YouTube | Time + Code | 2-5 min | None | None |
| Daily | Auto | Instant | None | None |
| Manual | Admin Review | Varies | None | High |

---

## Best Practices

### Twitter Quests:
✅ Use for genuine engagement
✅ Vary between follows, likes, retweets
✅ Monitor rate limits (100/day)
❌ Don't spam users with too many Twitter quests

### YouTube Quests:
✅ Place code at different timestamps
✅ Use clear, memorable codes
✅ Set realistic watch times
❌ Don't make videos too long (user retention)

### Daily Check-in:
✅ Use milestone bonuses for long-term engagement
✅ Set consistent reset times
✅ Consider time zones of your users
❌ Don't make base reward too high (inflation risk)

### Manual Quests:
✅ Provide clear, step-by-step instructions
✅ Review submissions promptly
✅ Use for high-value activities
❌ Don't use for simple tasks (automation is better)

---

## API Endpoints Used

### Quest Creation:
```
POST /api/tasks
Authorization: Bearer <admin_token>
Content-Type: application/json
```

### Quest Verification (User Side):
```
POST /api/verify
Content-Type: application/json
{
  "telegram_id": 123456789,
  "task_id": "quest-uuid"
}
```

### Manual Quest Approval (Admin):
```
PUT /api/admin/user-tasks/{user_task_id}/verify
Authorization: Bearer <admin_token>
{
  "approved": true
}
```

---

## Database Schema

### Tasks Table:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(200),
    description TEXT,
    task_type VARCHAR(50),
    platform VARCHAR(50),
    url TEXT,
    points_reward INTEGER,
    verification_required BOOLEAN,
    verification_data JSONB,  -- Platform-specific config
    is_active BOOLEAN,
    created_at TIMESTAMP
);
```

### Verification Data Examples:

**Twitter:**
```json
{
  "method": "twitter_api",
  "type": "follow",
  "username": "YourCompany"
}
```

**YouTube:**
```json
{
  "method": "time_delay_code",
  "code": "SECRET123",
  "min_watch_time_seconds": 120,
  "max_attempts": 3
}
```

**Daily:**
```json
{
  "method": "daily_checkin",
  "streak_bonus": "milestone",
  "reset_time_utc": "00:00",
  "consecutive_required": true
}
```

**Manual:**
```json
{
  "method": "manual_review",
  "submission_type": "text",
  "requires_approval": true
}
```

---

## Troubleshooting

### Twitter Quest Not Verifying
- Check rate limits (100/day free tier)
- Verify Twitter credentials in `.env`
- Check if username exists
- Wait 24 hours for cache refresh

### YouTube Code Failed
- User may not have watched minimum time
- Code is case-sensitive
- Check max attempts not exceeded
- Verify code matches exactly

### Daily Quest Not Resetting
- Check server timezone (UTC)
- Verify cron job is running
- Check database streak records
- Ensure reset_time_utc is correct

### Manual Quest Pending Too Long
- Admins must manually approve
- Check admin dashboard regularly
- Set up notifications for admins
- Consider auto-approve for simple tasks

---

## Future Enhancements

### Planned Features:
- 🎮 **Gaming Platform Integrations** (Steam, Epic, etc.)
- 📸 **Instagram Quest Support**
- 💬 **Telegram Group/Channel Verification**
- 🎯 **Quest Chains** (Complete A to unlock B)
- ⏰ **Time-Limited Quests** (Available for 24h only)
- 🏆 **Quest Tiers** (Bronze, Silver, Gold difficulty)

---

## Date Updated
October 16, 2025

## Status
🟢 **All 4 Quest Types Fully Functional**
