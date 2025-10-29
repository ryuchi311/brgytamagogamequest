# Telegram User Mention Feature

## Overview

When a user clicks "Verify Me" and successfully completes a Telegram group quest, the bot will:
1. ✅ Verify their membership in the specific group
2. 🎉 Send an announcement to **that specific group** (from verification_data)
3. 🔔 **Mention/tag the user** so they receive a notification
4. 💎 Show quest details and points earned

## How It Works

### User Mention Format

The bot uses Telegram's user mention format:
```
[Display Name](tg://user?id=USER_ID)
```

**Benefits:**
- ✅ Creates a clickable mention
- ✅ User receives a notification
- ✅ Works even if user has no username
- ✅ Opens user's profile when clicked

### Announcement Message

When user completes verification, the group receives:

```
🎉 **New Member Verified!**

✅ [John Doe](tg://user?id=123456789) (@johndoe) has successfully completed the quest!

📍 Group: **Brgy Tamago Warriors**
🎮 Quest: **Join Brgy Tamago Community**
💎 Points earned: **50 XP**

🎊 Welcome to the community! 🚀
```

### Key Features

1. **User is Tagged**: Creates clickable mention that notifies the user
2. **Group-Specific**: Announcement goes to the group specified in quest's `verification_data.chat_id`
3. **Quest Details**: Shows which quest was completed
4. **Points Display**: Shows XP earned
5. **Graceful Fallback**: If announcement fails, verification still succeeds

## Configuration

### Quest Setup

Each Telegram group quest must have proper `verification_data`:

```json
{
  "task_type": "telegram",
  "platform": "telegram",
  "title": "Join Brgy Tamago Community",
  "url": "https://t.me/tamagowarriors",
  "points_reward": 50,
  "verification_data": {
    "type": "join_group",
    "method": "telegram_membership",
    "chat_id": "@tamagowarriors",
    "chat_name": "Brgy Tamago Warriors",
    "invite_link": "https://t.me/tamagowarriors"
  }
}
```

**Important Fields:**
- `chat_id` - Where to send announcement (@username or -100xxxxxxxx)
- `chat_name` - Display name for the group in messages

### Multiple Groups

If you have multiple Telegram group quests, each will announce to its own group:

```json
[
  {
    "title": "Join Brgy Tamago Community",
    "verification_data": {
      "chat_id": "@tamagowarriors",
      "chat_name": "Brgy Tamago Warriors"
    }
  },
  {
    "title": "Join B.Y.A.G.",
    "verification_data": {
      "chat_id": "@byagmo",
      "chat_name": "B.Y.A.G. Community"
    }
  }
]
```

When user verifies:
- Quest 1 → Announcement in @tamagowarriors
- Quest 2 → Announcement in @byagmo

## Testing

### Test User Mention

Use the test script to verify mentions work:

```bash
./test_telegram_mention.sh
```

**You'll need:**
1. Group Chat ID (e.g., @tamagowarriors)
2. User's Telegram ID (numeric)
3. User's First Name
4. Quest Title
5. Points Reward

The script will:
- Send a test announcement to the group
- Mention the user
- Show API response
- Confirm if mention was successful

### Manual Testing

1. **User joins your Telegram group**
2. **User opens Quest Hub**
3. **User clicks "Verify Me" on Telegram quest**
4. **Bot verifies membership**
5. **Bot sends announcement to the group**
6. **User receives notification** (because they're mentioned)
7. **Group sees the announcement** with clickable mention

### Verify Announcement Sent

Check backend logs:
```bash
tail -f backend.log | grep "📢"
```

Look for:
```
📢 Sending announcement to group...
✅ Announcement sent successfully!
```

## Requirements

### Bot Permissions

Bot needs these permissions in the group:
- ✅ Be a member of the group
- ✅ Permission to send messages
- ✅ Permission to mention users

### User Requirements

For mention to work:
- ✅ User must be a member of the group
- ✅ User must have allowed your bot (sent /start)
- ✅ User's privacy settings must allow mentions

## Troubleshooting

### Announcement Not Sent

**Check logs:**
```bash
./monitor_logs.sh backend
```

**Common issues:**

1. **Bot not in group**
   ```
   Error: bot is not a member of the chat
   Solution: Add bot to the group
   ```

2. **No permission to send messages**
   ```
   Error: not enough rights to send messages
   Solution: Make bot admin or change group settings
   ```

3. **Wrong chat_id**
   ```
   Error: chat not found
   Solution: Verify chat_id in verification_data
   ```

### User Not Notified

**Possible reasons:**

1. **User's privacy settings** - User blocked mentions from non-contacts
   - Solution: User adjusts privacy settings

2. **User hasn't started bot** - User never sent /start to your bot
   - Solution: User sends /start to bot first

3. **Notification settings** - User muted group or turned off notifications
   - Solution: User checks Telegram notification settings

### Test Without Real User

Use the test script with your own Telegram ID:

```bash
./test_telegram_mention.sh

# Enter:
# Chat ID: @tamagowarriors
# User ID: YOUR_TELEGRAM_ID
# First Name: Your Name
# Quest Title: Test Quest
# Points: 50
```

Check the group - you should see the announcement and receive a notification!

## Code Implementation

### Location
**File:** `app/api.py`  
**Function:** `verify_task()`  
**Lines:** ~481-505

### Key Code

```python
# Build announcement message with user mention
user_mention = f"[{user_display_name}](tg://user?id={telegram_id})"

announcement = f"🎉 **New Member Verified!**\n\n"
announcement += f"✅ {user_mention}"
if username:
    announcement += f" (@{username})"
announcement += f" has successfully completed the quest!\n\n"
announcement += f"📍 Group: **{verification_data.get('chat_name', 'Brgy Tamago')}**\n"
announcement += f"🎮 Quest: **{task.get('title', 'Join Quest')}**\n"
announcement += f"💎 Points earned: **{task.get('points_reward', 0)} XP**\n\n"
announcement += f"🎊 Welcome to the community! 🚀"

# Send to specific group
send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
send_params = {
    "chat_id": chat_id,  # From verification_data
    "text": announcement,
    "parse_mode": "Markdown"
}
```

### Fallback Behavior

If announcement fails, verification still succeeds:
```python
try:
    # Send announcement
    ...
except Exception as announce_error:
    print(f"⚠️ Failed to send announcement: {str(announce_error)}")
    # Don't fail the verification if announcement fails
```

User gets points even if announcement doesn't send!

## Examples

### Example 1: Public Group

**Quest Configuration:**
```json
{
  "verification_data": {
    "chat_id": "@tamagowarriors",
    "chat_name": "Tamago Warriors"
  }
}
```

**Announcement:**
```
🎉 New Member Verified!

✅ [John Smith](tg://user?id=123456789) (@johnsmith) has successfully completed the quest!

📍 Group: **Tamago Warriors**
🎮 Quest: **Join Brgy Tamago Community**
💎 Points earned: **50 XP**

🎊 Welcome to the community! 🚀
```

### Example 2: Private Supergroup

**Quest Configuration:**
```json
{
  "verification_data": {
    "chat_id": "-1001234567890",
    "chat_name": "VIP Members Only"
  }
}
```

**Announcement:**
```
🎉 New Member Verified!

✅ [Jane Doe](tg://user?id=987654321) has successfully completed the quest!

📍 Group: **VIP Members Only**
🎮 Quest: **Join VIP Group**
💎 Points earned: **100 XP**

🎊 Welcome to the community! 🚀
```

## Benefits

### For Users
- 🔔 Get notified when mentioned
- 🎉 Feel welcomed with public recognition
- 👥 Easy to connect (clickable profile)
- 📊 See progress (points earned)

### For Community
- 🎊 Celebrate new members
- 👋 Warm welcome experience
- 📢 Group engagement
- 🎮 Gamification visibility

### For Admins
- ✅ Automatic announcements
- 🔧 Group-specific targeting
- 📈 Track quest completions
- 🎯 No manual work needed

## Related Documentation

- [Telegram Verification Troubleshooting](./TELEGRAM_VERIFICATION_TROUBLESHOOTING.md)
- [Telegram Bot Setup Guide](./TELEGRAM_BOT_SETUP_GUIDE.md)
- [Quest Types Guide](./QUEST_TYPES_GUIDE.md)
- [Telegram Membership Verification Fix](./TELEGRAM_MEMBERSHIP_VERIFICATION_FIX.md)

## Test Commands

```bash
# Test mention feature
./test_telegram_mention.sh

# Test full verification flow
./test_telegram_membership.sh

# Monitor announcements in real-time
./monitor_logs.sh backend | grep "📢"

# Check all Telegram quests
curl -s http://localhost:8000/api/tasks | jq '.[] | select(.task_type == "telegram")'
```
