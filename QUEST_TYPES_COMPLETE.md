# 🎮 Complete Quest Types Guide

**Date:** October 16, 2025  
**Status:** ✅ All Quest Types Implemented & Mobile-Responsive

---

## 📋 Overview

The admin panel now supports **5 specialized quest types**, each with dedicated configuration forms and automation features:

| Quest Type | Icon | Automation | Purpose |
|------------|------|------------|---------|
| **🐦 Twitter** | Blue Bird | Semi-Auto (API) | Social media engagement |
| **📺 YouTube** | Red Play | Auto (Time + Code) | Video watch verification |
| **✈️ Telegram** | Plane | Auto (Bot API) | Community growth |
| **📅 Daily Check-in** | Calendar | Auto | User retention |
| **✍️ Manual** | Pencil | Manual Review | Custom tasks |

---

## 🐦 Quest Type 1: Twitter

### Purpose
Verify Twitter actions like follows, likes, retweets, and replies.

### Configuration Fields

```
┌──────────────────────────────────────────────────┐
│ 🐦 Twitter Quest Configuration                   │
├──────────────────────────────────────────────────┤
│                                                   │
│ ACTION TYPE:                                      │
│ ☑ Follow Account                                 │
│ ☐ Like Tweet                                     │
│ ☐ Retweet                                        │
│ ☐ Reply to Tweet                                 │
│                                                   │
│ TARGET USERNAME (without @):                      │
│ [elonmusk              ]                          │
│ Example: elonmusk                                 │
│                                                   │
│ TWEET URL (for like/retweet/reply):               │
│ [https://twitter.com/username/status/123456]     │
│                                                   │
│ ⚡ Auto-Verification: Uses Twitter API            │
│    (Rate limited: 100 checks/day)                 │
└──────────────────────────────────────────────────┘
```

### Automation
- **Follow**: API checks if user follows target account
- **Like**: API checks if user liked specific tweet
- **Retweet**: API checks if user retweeted
- **Reply**: API searches for user's reply

### Technical Details
- **API**: Twitter API v2 with Bearer token
- **Rate Limit**: 100 requests/month (Free tier) or 10,000/month (Basic $100)
- **Verification**: 24-hour caching to reduce API calls
- **Fallback**: Manual verification if quota exceeded

### Task Types Generated
- `twitter_follow`
- `twitter_like`
- `twitter_retweet`
- `twitter_reply`

### Example Quest
```json
{
  "title": "Follow us on Twitter",
  "description": "Follow @BRGYTamago for gaming updates!",
  "task_type": "twitter_follow",
  "platform": "twitter",
  "url": "https://twitter.com/BRGYTamago",
  "points_reward": 50,
  "verification_required": true,
  "verification_data": {
    "method": "twitter_api",
    "type": "follow",
    "username": "BRGYTamago"
  }
}
```

---

## 📺 Quest Type 2: YouTube

### Purpose
Verify users actually watched YouTube videos with time-delay and secret code verification.

### Configuration Fields

```
┌──────────────────────────────────────────────────┐
│ 📺 YouTube Video Quest                            │
├──────────────────────────────────────────────────┤
│                                                   │
│ YOUTUBE VIDEO URL:                                │
│ [https://youtube.com/watch?v=ABC123    ]         │
│                                                   │
│ SECRET CODE (shown in video):                     │
│ [QUEST2025            ]                           │
│ Users must enter this code after watching         │
│                                                   │
│ MIN. WATCH TIME:    MAX ATTEMPTS:                 │
│ [120] seconds       [3]                           │
│                                                   │
│ CODE APPEARS AT:                                  │
│ [2:30 or at the end        ]                      │
│                                                   │
│ ⚡ How it works: User watches video,              │
│    enters code shown. Watch time is tracked.      │
└──────────────────────────────────────────────────┘
```

### Automation
- **Time Tracking**: Server-side timestamp validation
- **Code Verification**: Case-insensitive code check
- **Attempt Limiting**: Max 3 attempts to prevent brute force
- **State Management**: watching → completed/failed

### Technical Details
- **Database**: `video_views` table tracks watch sessions
- **Validation**: Server-side timestamps (cannot be manipulated)
- **Security**: Unique constraint on user_id + task_id
- **Status**: watching/completed/failed

### Task Types Generated
- `youtube_watch`

### Example Quest
```json
{
  "title": "Watch our gameplay video",
  "description": "Watch the full video and enter the secret code!",
  "task_type": "youtube_watch",
  "platform": "youtube",
  "url": "https://youtube.com/watch?v=ABC123",
  "points_reward": 100,
  "verification_required": true,
  "verification_data": {
    "method": "time_delay_code",
    "code": "QUEST2025",
    "min_watch_time_seconds": 120,
    "code_timestamp": "2:30",
    "max_attempts": 3
  }
}
```

### User Flow
1. User clicks quest → Bot starts timer
2. User watches video for minimum time
3. User finds secret code in video
4. User sends code to bot
5. Bot verifies time elapsed AND code matches
6. Quest complete! Points awarded

---

## ✈️ Quest Type 3: Telegram

### Purpose
Verify users joined Telegram groups or subscribed to channels.

### Configuration Fields

```
┌──────────────────────────────────────────────────┐
│ ✈️ Telegram Quest Configuration                  │
├──────────────────────────────────────────────────┤
│                                                   │
│ ACTION TYPE:                                      │
│ ☑ Join Group/Supergroup                          │
│ ☐ Subscribe to Channel                           │
│                                                   │
│ TELEGRAM LINK:                                    │
│ [https://t.me/yourgroupname  ]                   │
│ Example: https://t.me/mychannel or @mychannel    │
│                                                   │
│ GROUP/CHANNEL ID:                                 │
│ [-1001234567890          ]                        │
│ Numeric ID or username (e.g., @mychannel)        │
│                                                   │
│ GROUP/CHANNEL NAME:                               │
│ [My Awesome Channel      ]                        │
│ Display name for users                            │
│                                                   │
│ ⚡ Auto-Verification: Bot checks membership       │
│                                                   │
│ ⚠️ Requirements:                                  │
│   • Bot must be admin in the group/channel        │
│   • Group/channel must be accessible              │
│   • Bot needs "See Members" permission            │
└──────────────────────────────────────────────────┘
```

### Automation
- **Membership Check**: Bot API `getChatMember` call
- **Real-time**: Instant verification
- **Statuses**: creator, administrator, member, restricted

### Technical Details
- **API**: Telegram Bot API
- **Endpoint**: `getChatMember`
- **Permissions**: Bot must be admin with "See Members"
- **Chat ID**: Numeric (-1001234567890) or @username

### Task Types Generated
- `telegram_join_group`
- `telegram_join_channel`

### Example Quest
```json
{
  "title": "Join our Telegram community",
  "description": "Join our main group for exclusive updates!",
  "task_type": "telegram_join_group",
  "platform": "telegram",
  "url": "https://t.me/mygaminggroup",
  "points_reward": 75,
  "verification_required": true,
  "verification_data": {
    "method": "telegram_membership",
    "type": "join_group",
    "chat_id": "-1001234567890",
    "chat_name": "My Gaming Group",
    "invite_link": "https://t.me/mygaminggroup"
  }
}
```

---

## 📅 Quest Type 4: Daily Check-in

### Purpose
Simple daily task to keep users engaged and coming back.

### Configuration Fields

```
┌──────────────────────────────────────────────────┐
│ 📅 Daily Check-in Quest                           │
├──────────────────────────────────────────────────┤
│                                                   │
│ STREAK BONUS:                                     │
│ ☑ No Streak Bonus                                │
│ ☐ Multiply by Streak (Day 7 = 7x points)         │
│ ☐ Milestone Bonuses (Day 7, 30, 100)             │
│                                                   │
│ RESET TIME (UTC):                                 │
│ [00:00] (midnight UTC)                            │
│ When the daily quest resets                       │
│                                                   │
│ ☑ Require consecutive days                       │
│   (break streak if missed a day)                  │
│                                                   │
│ ⚡ Auto-Completion: Simple button click.          │
│    Users can complete once per day.               │
└──────────────────────────────────────────────────┘
```

### Automation
- **Auto-complete**: One-click completion
- **Daily Reset**: Automatic at specified time
- **Streak Tracking**: Optional streak bonuses
- **No Verification**: Instant completion

### Technical Details
- **Frequency**: Once per day
- **Reset**: UTC timezone-based
- **Tracking**: Server-side date comparison
- **Bonus Logic**: Multiplier or milestone-based

### Task Types Generated
- `daily_checkin`

### Example Quest
```json
{
  "title": "Daily Login Reward",
  "description": "Check in daily to earn XP and maintain your streak!",
  "task_type": "daily_checkin",
  "platform": "daily",
  "points_reward": 10,
  "verification_required": false,
  "verification_data": {
    "method": "daily_checkin",
    "streak_bonus": "multiply",
    "reset_time_utc": "00:00",
    "consecutive_required": true,
    "frequency": "daily"
  }
}
```

### Bonus Examples
- **No Bonus**: 10 XP every day
- **Multiply**: Day 1 = 10 XP, Day 7 = 70 XP, Day 30 = 300 XP
- **Milestone**: Day 1-6 = 10 XP, Day 7 = 100 XP bonus, Day 30 = 500 XP bonus

---

## ✍️ Quest Type 5: Manual

### Purpose
Custom tasks requiring admin review (website visits, creative submissions, etc.).

### Configuration Fields

```
┌──────────────────────────────────────────────────┐
│ ✍️ Manual Verification Quest                     │
├──────────────────────────────────────────────────┤
│                                                   │
│ QUEST URL (Optional):                             │
│ [https://example.com/contest  ]                  │
│ Link to instructions or external platform         │
│                                                   │
│ SUBMISSION TYPE:                                  │
│ ☑ No Submission Needed                           │
│ ☐ Text/Link Submission                           │
│ ☐ Screenshot Upload                              │
│ ☐ Enter Code                                     │
│                                                   │
│ INSTRUCTIONS FOR USERS:                           │
│ [Tell users exactly what to do...               │
│  1. Visit the website                             │
│  2. Complete the task                             │
│  3. Submit proof (screenshot/link)]               │
│                                                   │
│ ⚡ Admin Review: Users submit completion.         │
│    Admin manually approves/rejects.               │
└──────────────────────────────────────────────────┘
```

### Automation
- **User Submission**: Optional text/screenshot/code
- **Admin Review**: Manual approval queue
- **Flexible**: Works for any custom task

### Technical Details
- **Verification**: Manual admin review
- **Queue**: Pending verification table
- **Proof**: Text, URL, or screenshot upload
- **Approval**: Admin clicks verify/reject

### Task Types Generated
- `manual_review`

### Example Quests

**Website Visit:**
```json
{
  "title": "Visit our partner website",
  "description": "Check out our sponsor's new game!",
  "task_type": "manual_review",
  "platform": "manual",
  "url": "https://partner-game.com",
  "points_reward": 25,
  "verification_required": true,
  "verification_data": {
    "method": "manual_review",
    "submission_type": "screenshot",
    "instructions": "1. Visit the website\n2. Take a screenshot showing you're there\n3. Submit for review",
    "requires_approval": true
  }
}
```

**Creative Contest:**
```json
{
  "title": "Fan Art Contest",
  "description": "Submit your best gaming artwork!",
  "task_type": "manual_review",
  "platform": "manual",
  "points_reward": 200,
  "verification_required": true,
  "verification_data": {
    "method": "manual_review",
    "submission_type": "text",
    "instructions": "Upload your artwork to imgur.com and paste the link here",
    "requires_approval": true
  }
}
```

---

## 📊 Quest Type Comparison

| Feature | Twitter | YouTube | Telegram | Daily | Manual |
|---------|---------|---------|----------|-------|--------|
| **Automation** | Semi-Auto | Auto | Auto | Auto | Manual |
| **API Cost** | $0-$100/mo | Free | Free | Free | Free |
| **Verification Time** | Instant | 2-5 min | Instant | Instant | 1-24 hours |
| **User Effort** | Low | Medium | Low | Very Low | Varies |
| **Admin Work** | Minimal | None | None | None | High |
| **Scalability** | Good | Excellent | Excellent | Excellent | Poor |
| **Cheating Risk** | Low | Very Low | Very Low | Medium | Low |

---

## 🎯 Recommended Use Cases

### Twitter Quests (🐦)
- **Best for**: Social media growth, viral campaigns
- **Example**: "Follow us for exclusive updates" (50 XP)
- **Frequency**: Weekly or per campaign

### YouTube Quests (📺)
- **Best for**: Content engagement, tutorial completion
- **Example**: "Watch our guide video" (100 XP)
- **Frequency**: Per video release

### Telegram Quests (✈️)
- **Best for**: Community building, group growth
- **Example**: "Join our main community" (75 XP)
- **Frequency**: One-time or per new group/channel

### Daily Check-in (📅)
- **Best for**: User retention, habit formation
- **Example**: "Daily login reward" (10 XP + streak bonus)
- **Frequency**: Daily (resets at midnight)

### Manual Quests (✍️)
- **Best for**: High-value tasks, creative contests, partnerships
- **Example**: "Submit fan art" (200 XP)
- **Frequency**: Special events, limited time

---

## 🔧 Technical Implementation

### Database Schema

All quests stored in `tasks` table:

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,  -- twitter_follow, youtube_watch, etc.
    platform VARCHAR(50),             -- twitter, youtube, telegram, daily, manual
    url TEXT,
    points_reward INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_bonus BOOLEAN DEFAULT false,
    verification_required BOOLEAN DEFAULT true,
    verification_data JSONB,          -- Quest-specific config
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Verification Data Structure

Each quest type uses `verification_data` JSONB column:

**Twitter:**
```json
{
  "method": "twitter_api",
  "type": "follow",
  "username": "BRGYTamago",
  "tweet_id": "123456789" // optional, for like/retweet
}
```

**YouTube:**
```json
{
  "method": "time_delay_code",
  "code": "QUEST2025",
  "min_watch_time_seconds": 120,
  "code_timestamp": "2:30",
  "max_attempts": 3
}
```

**Telegram:**
```json
{
  "method": "telegram_membership",
  "type": "join_group",
  "chat_id": "-1001234567890",
  "chat_name": "My Gaming Group",
  "invite_link": "https://t.me/mygaminggroup"
}
```

**Daily:**
```json
{
  "method": "daily_checkin",
  "streak_bonus": "multiply",
  "reset_time_utc": "00:00",
  "consecutive_required": true,
  "frequency": "daily"
}
```

**Manual:**
```json
{
  "method": "manual_review",
  "submission_type": "screenshot",
  "instructions": "Upload proof...",
  "requires_approval": true
}
```

---

## 📱 Mobile Responsive Design

All quest forms are fully mobile-responsive:

### Desktop View (≥1024px)
- Full form layout with all fields visible
- Side-by-side inputs where applicable
- Hover effects and animations

### Mobile View (<1024px)
- Stacked layout for better readability
- Touch-friendly buttons (44px min height)
- Simplified grid (2 columns for quest type selector)
- Full-width inputs and buttons

### Quest Type Selector

**Desktop:**
```
[🐦 Twitter] [📺 YouTube] [✈️ Telegram] [📅 Daily] [✍️ Manual]
```

**Mobile:**
```
[🐦 Twitter]  [📺 YouTube]
[✈️ Telegram] [📅 Daily]
[✍️ Manual]
```

---

## 🎮 User Experience

### Quest Creation Flow

1. **Admin opens quest modal**
2. **Selects quest type** (Twitter, YouTube, etc.)
3. **Quest-specific form appears** with relevant fields
4. **Fills in details**:
   - Common: Title, Description, XP Reward
   - Specific: Platform-specific configuration
5. **Clicks "🚀 CREATE QUEST"**
6. **Quest appears in list** with proper status badge

### User Completion Flow

**Twitter Quest:**
1. User sees quest → Clicks to start
2. Bot shows Twitter link
3. User completes action (follow/like/retweet)
4. User submits @username
5. Bot verifies via API → Instant result

**YouTube Quest:**
1. User sees quest → Clicks to start
2. Bot starts timer + shows video link
3. User watches video (minimum time)
4. User finds secret code in video
5. User sends code to bot
6. Bot verifies time + code → Quest complete

**Telegram Quest:**
1. User sees quest → Clicks to start
2. Bot shows Telegram group/channel link
3. User joins group/channel
4. User clicks "Verify"
5. Bot checks membership → Instant result

**Daily Check-in:**
1. User sees quest (available once per day)
2. User clicks "Check In"
3. Instant completion + XP awarded
4. Streak bonus applied (if enabled)

**Manual Quest:**
1. User sees quest → Clicks to start
2. Bot shows instructions + URL
3. User completes task
4. User submits proof (text/screenshot)
5. Admin reviews and approves/rejects

---

## 🚀 Quick Start Examples

### Create Twitter Follow Quest
```javascript
// Admin Dashboard → Create Quest → Select Twitter
{
  "title": "Follow us on Twitter",
  "description": "Follow @BRGYTamago for gaming news!",
  "action_type": "follow",
  "username": "BRGYTamago",
  "xp_reward": 50
}
```

### Create YouTube Watch Quest
```javascript
// Admin Dashboard → Create Quest → Select YouTube
{
  "title": "Watch our gameplay",
  "description": "Watch the full video and find the code!",
  "video_url": "https://youtube.com/watch?v=ABC123",
  "secret_code": "GAMING2025",
  "min_watch_time": 120,
  "xp_reward": 100
}
```

### Create Telegram Join Quest
```javascript
// Admin Dashboard → Create Quest → Select Telegram
{
  "title": "Join our community",
  "description": "Join our main Telegram group!",
  "action_type": "join_group",
  "telegram_link": "https://t.me/mygaminggroup",
  "chat_id": "-1001234567890",
  "chat_name": "My Gaming Group",
  "xp_reward": 75
}
```

### Create Daily Check-in Quest
```javascript
// Admin Dashboard → Create Quest → Select Daily
{
  "title": "Daily Login Reward",
  "description": "Check in daily for XP!",
  "streak_bonus": "multiply",
  "reset_time": "00:00",
  "xp_reward": 10
}
```

### Create Manual Review Quest
```javascript
// Admin Dashboard → Create Quest → Select Manual
{
  "title": "Submit Fan Art",
  "description": "Create awesome gaming art!",
  "submission_type": "text",
  "instructions": "Upload to imgur and paste link",
  "xp_reward": 200
}
```

---

## 📈 Success Metrics

### Track These KPIs:

**Per Quest Type:**
- Completion rate
- Average time to complete
- User drop-off points
- Verification success rate

**Overall:**
- Total quests created
- Active users per quest type
- XP distributed per type
- Most popular quest types

---

## 🎉 Summary

✅ **5 Quest Types Implemented**
- 🐦 Twitter (Semi-automated via API)
- 📺 YouTube (Fully automated with time + code)
- ✈️ Telegram (Fully automated with bot API)
- 📅 Daily Check-in (Automated, simple click)
- ✍️ Manual (Admin review, flexible)

✅ **Features:**
- Dedicated configuration forms for each type
- Mobile-responsive design
- Comprehensive verification systems
- Clear user flows
- Admin analytics

✅ **Ready for Production:**
- All quest types tested
- Documentation complete
- Mobile-friendly UI
- Scalable architecture

---

**Last Updated:** October 16, 2025  
**Status:** ✅ Production Ready  
**Access:** http://localhost/admin.html → Create Quest
