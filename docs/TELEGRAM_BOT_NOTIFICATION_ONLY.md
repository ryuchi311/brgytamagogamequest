# 🤖 Telegram Bot - Notification Only Mode

## 📋 Overview

This is a **simplified, notification-only** Telegram bot that focuses on:
1. ✅ **User Registration** - Register users via `/start`
2. ✅ **Notifications** - Send alerts about new quests and rewards
3. ✅ **Basic Verification** - Verify Telegram channel/group membership only
4. ✅ **Web App Redirect** - Direct all quest interactions to the web app

### What's Removed
- ❌ No quest viewing in bot
- ❌ No quest completion in bot
- ❌ No points claiming in bot
- ❌ No leaderboard in bot
- ❌ No profile viewing in bot
- ❌ No reward claiming in bot

**Result**: Pure notification + verification bot that redirects users to the web app for all interactions.

---

## 🎯 Bot Flow

```
┌─────────────────────────────────────────────────────────┐
│                    USER EXPERIENCE                       │
└─────────────────────────────────────────────────────────┘

1. USER REGISTRATION
   ↓
   User: /start
   Bot: Welcome! You're registered.
        Click button → Opens Web App
   ↓
   
2. NOTIFICATIONS (Automatic)
   ↓
   Bot: 🆕 New Quest Available!
        [View Quest] button → Opens Web App
   ↓
   Bot: 🎁 New Reward Added!
        [View Rewards] button → Opens Web App
   ↓
   Bot: ✅ Quest Completed!
        You earned 50 XP!
   ↓

3. VERIFICATION (Telegram Only)
   ↓
   User clicks "Verify" in Web App
   ↓
   Bot: Checks Telegram membership
   ↓
   If member → Award points
   If not member → Show "Join" button
   ↓

4. ALL OTHER ACTIONS
   ↓
   User tries to do anything else in bot
   Bot: "Visit Web App to continue"
        [Open Web App] button
```

---

## 🚀 Setup Instructions

### 1. Environment Variables

Make sure your `.env` file has:

```bash
# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Web App URL (your frontend)
WEBAPP_URL=https://your-domain.com

# Or for Codespaces:
WEBAPP_URL=https://your-codespace-8080.preview.app.github.dev
```

### 2. Replace Old Bot

**Option A: Replace current bot file**
```bash
# Backup current bot
cp app/telegram_bot.py app/telegram_bot_old.py

# Replace with notification bot
cp app/telegram_bot_notification_only.py app/telegram_bot.py
```

**Option B: Run separately**
```bash
# Run the notification bot directly
python app/telegram_bot_notification_only.py
```

### 3. Start the Bot

```bash
# If you replaced telegram_bot.py:
python -m app.telegram_bot

# Or directly:
python app/telegram_bot_notification_only.py
```

---

## 📝 Bot Commands

### User Commands

| Command | Description | Response |
|---------|-------------|----------|
| `/start` | Register user | Welcome message + Web App button |
| `/help` | Show help | Bot info + Web App button |

**That's it!** Only 2 commands. Everything else happens on the web app.

---

## 🔔 Notification Methods

The bot has 3 notification methods that can be called from your API:

### 1. New Quest Notification

```python
await bot.send_new_quest_notification(
    user_telegram_id=123456789,
    quest_data={
        'id': 'quest-id',
        'title': 'Visit Our Website',
        'description': 'Check out our homepage',
        'points_reward': 50,
        'task_type': 'link'
    }
)
```

User sees:
```
🆕 New Quest Available!

📋 Visit Our Website
Check out our homepage

💰 Reward: 50 XP
🏷️ Type: link

[View Quest] → Opens Web App
```

### 2. New Reward Notification

```python
await bot.send_new_reward_notification(
    user_telegram_id=123456789,
    reward_data={
        'title': 'Premium Badge',
        'description': 'Exclusive badge for top players',
        'points_cost': 500,
        'quantity_available': 10
    }
)
```

User sees:
```
🎁 New Reward Available!

✨ Premium Badge
Exclusive badge for top players

💎 Cost: 500 XP
📦 Available: 10

[View Rewards] → Opens Web App
```

### 3. Quest Completed Notification

```python
await bot.send_quest_completed_notification(
    user_telegram_id=123456789,
    quest_title='Visit Our Website',
    points=50
)
```

User sees:
```
✅ Quest Completed!

🎉 You earned 50 XP for completing:
📋 Visit Our Website

[View More Quests] → Opens Web App
```

---

## 🔐 Verification

The bot ONLY handles **Telegram membership verification**. All other verifications happen on the web app or API.

### Telegram Verification Flow

1. **User clicks "Verify" on Web App**
   - Web App sends verification request with callback_data
   
2. **Bot receives callback**
   ```python
   callback_data = "verify_telegram_quest-id-123"
   ```

3. **Bot checks membership**
   ```python
   chat_member = await bot.get_chat_member(
       chat_id="@your_channel",
       user_id=user.id
   )
   ```

4. **If member → Award points**
   - Complete quest via API
   - Send success message
   - Create notification

5. **If not member → Show join button**
   ```
   ❌ Not Verified
   
   You must join first.
   
   [Join Now] [Verify Again]
   ```

---

## 🔗 Integration with API

### Update API to Send Notifications

When creating a new quest (in `app/api.py`):

```python
@app.post("/api/tasks")
async def create_task(task: TaskCreate, admin=Depends(get_current_admin)):
    # ... create task code ...
    
    # Send notifications to all users
    users = supabase.table("users").select("telegram_id").eq("is_active", True).execute()
    
    for user in users.data:
        try:
            # Send notification via bot
            await notification_bot.send_new_quest_notification(
                user_telegram_id=user['telegram_id'],
                quest_data=created_task
            )
        except Exception as e:
            logger.error(f"Failed to notify user {user['telegram_id']}: {e}")
    
    return created_task
```

### When Quest is Completed

```python
@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str, user_id: str):
    # ... complete task code ...
    
    # Send notification
    user = get_user_by_id(user_id)
    task = get_task_by_id(task_id)
    
    await notification_bot.send_quest_completed_notification(
        user_telegram_id=user['telegram_id'],
        quest_title=task['title'],
        points=task['points_reward']
    )
    
    return {"success": True}
```

---

## 📊 Comparison: Old Bot vs New Bot

| Feature | Old Bot | New Bot |
|---------|---------|---------|
| **User Registration** | ✅ Yes | ✅ Yes |
| **View Quests in Bot** | ✅ Yes | ❌ No - Web App |
| **Complete Quests in Bot** | ✅ Yes | ❌ No - Web App |
| **Claim Points in Bot** | ✅ Yes | ❌ No - Web App |
| **Leaderboard in Bot** | ✅ Yes | ❌ No - Web App |
| **Profile in Bot** | ✅ Yes | ❌ No - Web App |
| **Notifications** | ⚠️ Limited | ✅ Full Support |
| **Telegram Verification** | ✅ Yes | ✅ Yes (Only This) |
| **Twitter Verification** | ✅ Yes | ❌ No - Web App |
| **YouTube Verification** | ✅ Yes | ❌ No - Web App |
| **Website Verification** | ✅ Yes | ❌ No - Auto |
| **Code Complexity** | ~1,130 lines | ~400 lines |
| **Maintenance** | Complex | Simple |
| **User Flow** | Mixed | Clean (Web-focused) |

---

## 💡 Benefits of Notification-Only Bot

### For Users
✅ **Cleaner Experience** - All interactions in one place (web app)  
✅ **Better UI** - Web app has better design than bot messages  
✅ **Faster** - No waiting for bot responses  
✅ **Notifications** - Stay updated on new content  

### For Developers
✅ **Simpler Code** - 70% less code to maintain  
✅ **Easier Debugging** - Fewer moving parts  
✅ **Better Separation** - Bot = notifications, Web = interactions  
✅ **Scalable** - Web app can handle more features  

### For System
✅ **Less Bot API Calls** - Reduced Telegram API usage  
✅ **Faster Responses** - Web app direct to database  
✅ **Better Reliability** - Fewer points of failure  
✅ **Cost Effective** - Lower server load  

---

## 🔧 Customization

### Change Notification Messages

Edit the `send_*_notification` methods in `telegram_bot_notification_only.py`:

```python
async def send_new_quest_notification(self, user_telegram_id: int, quest_data: dict):
    message = f"""🆕 **New Quest Available!**

📋 **{quest_data['title']}**
{quest_data.get('description', 'Complete this quest to earn XP!')}

💰 Reward: **{quest_data['points_reward']} XP**

Complete this quest on the web app now!
"""
    # ... rest of code ...
```

### Add More Verification Types

Currently only Telegram verification is supported. To add others, you would:

1. Add callback handler in `button_callback` method
2. Implement verification logic
3. Call API to complete quest
4. Send success/failure message

**However**, the recommended approach is to handle all non-Telegram verifications on the web app side.

---

## 🧪 Testing

### Test User Registration

```bash
# In Telegram, send:
/start

# Expected response:
# Welcome message with web app button
```

### Test Notification (Manual)

```python
# In Python console or test script:
from app.telegram_bot_notification_only import NotificationBot
import asyncio

async def test():
    bot = NotificationBot()
    await bot.send_new_quest_notification(
        user_telegram_id=YOUR_TELEGRAM_ID,
        quest_data={
            'id': 'test-123',
            'title': 'Test Quest',
            'description': 'Testing notifications',
            'points_reward': 100,
            'task_type': 'test'
        }
    )

asyncio.run(test())
```

### Test Telegram Verification

1. Create a Telegram quest in admin panel
2. User clicks verification button
3. Bot checks membership
4. Awards points if member

---

## 📚 File Structure

```
/workspaces/codespaces-blank/
├── app/
│   ├── telegram_bot.py                        # Old full-featured bot
│   ├── telegram_bot_notification_only.py      # New notification bot ⭐
│   ├── bot_api_client.py                      # API client (shared)
│   └── api.py                                 # Backend API
├── frontend/
│   └── *.html                                 # Web app pages
└── .env                                        # Environment variables
```

---

## 🚀 Deployment

### Development

```bash
# Run bot in development
python app/telegram_bot_notification_only.py
```

### Production

```bash
# Option 1: Using screen/tmux
screen -S telegram-bot
python app/telegram_bot_notification_only.py

# Option 2: Using systemd service
sudo nano /etc/systemd/system/telegram-bot.service

# Add:
[Unit]
Description=Telegram Notification Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 app/telegram_bot_notification_only.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start:
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

---

## 🐛 Troubleshooting

### Bot Not Responding

1. Check if bot is running:
   ```bash
   ps aux | grep telegram_bot
   ```

2. Check logs for errors

3. Verify `TELEGRAM_BOT_TOKEN` in `.env`

4. Test bot token:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

### Notifications Not Sending

1. Check if user's `telegram_id` is correct in database

2. Verify user hasn't blocked the bot

3. Check bot has permission to send messages

4. Look for errors in bot logs

### Verification Not Working

1. Ensure bot is admin in the Telegram channel/group

2. Check `channel_username` in quest's `verification_data`

3. Verify user is actually a member

4. Check bot has permission to read chat members

---

## 📝 Summary

### What This Bot Does
✅ Registers users via `/start`  
✅ Sends notifications about new quests  
✅ Sends notifications about new rewards  
✅ Sends notifications about quest completions  
✅ Verifies Telegram membership only  
✅ Redirects all other actions to web app  

### What This Bot DOESN'T Do
❌ No quest viewing in bot  
❌ No quest completion in bot (except Telegram verification)  
❌ No points claiming in bot  
❌ No leaderboard in bot  
❌ No profile in bot  
❌ No reward claiming in bot  

### Result
🎯 **Simple, focused bot** that does one thing well: **Notifications + Basic Verification**  
🎯 **Web app handles all interactions** for better UX  
🎯 **400 lines vs 1,130 lines** = 70% code reduction  
🎯 **Easier to maintain and debug**  

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
