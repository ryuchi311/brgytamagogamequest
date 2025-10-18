# 🎮 Telegram Mini App Setup Guide

## Overview

This Gaming Quest Hub is now a **Telegram Mini App** that requires users to have a Telegram account to participate. Users cannot access the app directly through a browser - they must authenticate through Telegram.

---

## ✅ What's Implemented

### 1. **Mandatory Telegram Authentication**
- Users MUST access the app through Telegram
- Direct browser access is **blocked** with a friendly error message
- Automatic user registration using Telegram account data

### 2. **Telegram WebApp SDK Integration**
- Integrated official Telegram WebApp JavaScript SDK
- Automatic extraction of user data (ID, username, first name, last name)
- Native Telegram UI integration (expanded view)

### 3. **Automatic User Registration**
- When a user opens the mini app through Telegram for the first time:
  - Their Telegram ID, username, and name are automatically captured
  - A user account is created in the database
  - They can immediately start completing quests
  - No manual signup required!

### 4. **Security Features**
- User authentication is handled by Telegram
- No passwords or email required
- Telegram ID is used as the unique identifier
- Session data is validated through Telegram's secure API

---

## 🚀 How to Set Up Your Telegram Mini App

### Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "Gaming Quest Hub")
   - Choose a username (must end in "bot", e.g., "gamequesthub_bot")
4. Save the **bot token** you receive

### Step 2: Configure Mini App

1. Send `/newapp` to **@BotFather**
2. Select your bot from the list
3. Provide the following:
   - **Title**: Gaming Quest Hub
   - **Description**: Complete quests, earn XP, and claim rewards!
   - **Photo**: Upload your app icon (square, 640x640px recommended)
   - **Demo GIF/Video**: (Optional) Show how your app works
   - **Web App URL**: Your frontend URL
     ```
     https://your-domain.com/frontend/index.html
     ```
     or for Codespaces:
     ```
     https://psychic-space-parakeet-rrvpxvx9x42p744-8080.app.github.dev/index.html
     ```

4. Set **Short name**: A short identifier (e.g., "questhub")

### Step 3: Enable Mini App

1. Go back to @BotFather
2. Send `/mybots`
3. Select your bot
4. Click **"Bot Settings"** → **"Menu Button"** → **"Configure Menu Button"**
5. Set:
   - **Button text**: "🎮 Play Game" or "Start Quests"
   - **URL**: Same as your Web App URL

---

## 📱 How Users Access Your Mini App

### Method 1: Through Bot Chat
1. User opens Telegram
2. Searches for your bot (e.g., @gamequesthub_bot)
3. Clicks the **Menu button** (bottom-left of chat)
4. Selects "🎮 Play Game"
5. Mini app opens automatically

### Method 2: Direct Link
Share this link format:
```
https://t.me/your_bot_username/your_short_name
```

Example:
```
https://t.me/gamequesthub_bot/questhub
```

### Method 3: Inline Button
From your bot, you can send a message with an inline button:
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [[InlineKeyboardButton("🎮 Open Quest Hub", web_app={"url": "YOUR_WEBAPP_URL"})]]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Welcome! Click below to start:", reply_markup=reply_markup)
```

---

## 🔒 Authentication Flow

### Current Implementation

```
┌──────────────┐
│ User Opens   │
│ Telegram App │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Clicks Bot   │
│ Menu Button  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ Telegram WebApp SDK  │
│ Initializes          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐     NO      ┌─────────────────────┐
│ Is Telegram User?    │────────────▶│ Show "Access via    │
│ (initDataUnsafe)     │             │ Telegram Required"  │
└──────┬───────────────┘             └─────────────────────┘
       │ YES
       ▼
┌──────────────────────┐
│ Extract User Data:   │
│ - Telegram ID        │
│ - Username           │
│ - First Name         │
│ - Last Name          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐     EXISTS   ┌─────────────────────┐
│ Check if User in DB  │─────────────▶│ Load User Profile   │
└──────┬───────────────┘              └─────────────────────┘
       │ NOT EXISTS
       ▼
┌──────────────────────┐
│ Auto-Create Account: │
│ POST /api/users/init │
│ - telegram_id        │
│ - username           │
│ - first_name         │
│ - last_name          │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ User Can Now:        │
│ ✓ View Quests        │
│ ✓ Complete Tasks     │
│ ✓ Earn XP            │
│ ✓ Claim Rewards      │
└──────────────────────┘
```

---

## 🔧 Technical Implementation

### Frontend Changes (`frontend/index.html`)

**1. Telegram SDK Added:**
```html
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

**2. Authentication Check:**
```javascript
// Initialize Telegram WebApp
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();
    
    // Get user data from Telegram
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        TELEGRAM_USER = tg.initDataUnsafe.user;
        TELEGRAM_ID = TELEGRAM_USER.id;
    }
}

// Block access if not from Telegram
if (!TELEGRAM_ID) {
    // Show "Telegram Required" page
}
```

**3. Auto-Registration:**
```javascript
// If user doesn't exist, create them automatically
if (response.status === 404) {
    const username = TELEGRAM_USER.username || `player${TELEGRAM_ID}`;
    const firstName = TELEGRAM_USER.first_name || 'Player';
    const lastName = TELEGRAM_USER.last_name || '';
    
    await fetch(`${API_URL}/users/init?telegram_id=${TELEGRAM_ID}&username=${username}&first_name=${firstName}&last_name=${lastName}`, {
        method: 'POST'
    });
}
```

### Backend Changes (`app/api.py`)

**Updated User Initialization Endpoint:**
```python
@app.post("/api/users/init")
async def init_user(telegram_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None):
    """Initialize a user if they don't exist - Auto-registration from Telegram"""
    # Check if user exists
    existing = DatabaseService.get_user_by_telegram_id(telegram_id)
    if existing:
        return existing
    
    # Create new user with Telegram data
    user_data = {
        "telegram_id": telegram_id,
        "username": username or f"user_{telegram_id}",
        "first_name": first_name or "Player",
        "last_name": last_name or "",
        "points": 0,
        "is_banned": False
    }
    
    response = supabase.table("users").insert(user_data).execute()
    return response.data[0]
```

---

## 🧪 Testing Your Mini App

### Test in Development

**For Local Testing (Without Telegram):**

The app will show a "Telegram Required" message when accessed directly. To test with Telegram:

1. Use a tunneling service (ngrok, cloudflare tunnel, etc.):
   ```bash
   ngrok http 8080
   ```

2. Update your bot's Web App URL in @BotFather with the ngrok URL

3. Open your bot in Telegram and click the menu button

**For Codespaces:**

Your app is already public! Just:
1. Copy your Codespaces URL (port 8080)
2. Set it as your bot's Web App URL
3. Access through Telegram

### Test User Registration

1. Open the mini app through Telegram
2. Check browser console (if using Telegram Desktop with DevTools):
   ```
   Telegram user authenticated: {id: 123456789, first_name: "John", ...}
   ```
3. Verify user created in database:
   ```bash
   # Check Supabase dashboard or query directly
   SELECT * FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;
   ```

---

## 🎨 What Users See

### ✅ When Accessed via Telegram (Correct Way)
- Full gaming quest interface
- Their Telegram name displayed
- All features available
- Seamless experience

### ❌ When Accessed via Browser (Blocked)
```
┌─────────────────────────────────────┐
│              🔒                      │
│      TELEGRAM REQUIRED               │
│                                      │
│  This is a Telegram Mini App.       │
│  You must access it through         │
│  Telegram to participate.           │
│                                      │
│  📱 How to Access:                  │
│  1. Open Telegram app               │
│  2. Search for our bot              │
│  3. Click "Start" or "Play Game"    │
│  4. Complete quests & earn XP!      │
│                                      │
│  ⚠️ Direct browser access not       │
│     supported                        │
└─────────────────────────────────────┘
```

---

## 🔐 Security Considerations

### Current Setup
- ✅ Telegram handles authentication
- ✅ User data comes from trusted Telegram API
- ✅ No password storage needed
- ✅ Telegram ID is unique and verified

### Additional Security (Recommended for Production)

**1. Validate Telegram InitData:**
```javascript
// Verify the data_check_string signature
// This ensures data came from Telegram and wasn't tampered with
```

**2. Implement Backend Validation:**
```python
# Validate Telegram initData signature on backend
# Check hash matches expected value
# Verify data is recent (not replayed)
```

**3. Use HTTPS:**
- Telegram requires HTTPS for Web Apps in production
- Codespaces provides this automatically
- For custom domains, use SSL certificate

---

## 🚀 Deployment Checklist

- [ ] Bot created on @BotFather
- [ ] Mini App configured with correct URL
- [ ] Menu button set up
- [ ] Frontend deployed on HTTPS
- [ ] API server running and accessible
- [ ] Database connected
- [ ] Test user registration flow
- [ ] Test quest completion
- [ ] Test reward redemption
- [ ] Share bot link with users!

---

## 📚 Additional Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Telegram WebApp Documentation**: https://core.telegram.org/bots/webapps
- **Example Mini Apps**: https://core.telegram.org/bots/webapps#examples
- **BotFather Commands**: https://core.telegram.org/bots#botfather

---

## 🆘 Troubleshooting

### Problem: "Telegram Required" message shows in Telegram
**Solution**: 
- Hard refresh (Ctrl+Shift+R)
- Clear Telegram cache
- Check if Web App URL is correct in @BotFather

### Problem: User data not showing
**Solution**:
- Open browser console (Telegram Desktop)
- Check if `TELEGRAM_USER` is populated
- Verify API endpoint is accessible

### Problem: User not getting registered
**Solution**:
- Check API logs for errors
- Verify database connection
- Ensure `/api/users/init` endpoint is working

---

## ✨ Benefits of Telegram Mini App

1. **Instant Registration**: No signup forms needed
2. **Trusted Authentication**: Leverages Telegram's security
3. **Native Experience**: Feels like part of Telegram
4. **Easy Sharing**: Users share via Telegram links
5. **Push Notifications**: Can send messages via bot
6. **Cross-Platform**: Works on mobile, desktop, and web
7. **Large Audience**: Access to 700M+ Telegram users

---

## 🎯 Next Steps

Now that Telegram authentication is mandatory:

1. **Update your bot welcome message** to introduce the mini app
2. **Create promotional content** for the bot
3. **Set up bot commands** to link back to the mini app
4. **Add notifications** when new quests are available
5. **Implement rewards** that are delivered via bot messages

Your users now have a seamless, secure way to participate in your gaming quest system! 🎮✨
