# Telegram Mini App Authentication Implementation

## Overview
This document outlines the implementation of Telegram-only authentication for the Gaming Quest Hub. Users must have a Telegram account to participate, with automated registration through Telegram WebApp integration.

## Current State
The system currently uses a hardcoded `TELEGRAM_ID = 123456789` for testing purposes in `frontend/index.html`. This needs to be replaced with real Telegram WebApp authentication.

## Implementation Plan

### 1. Telegram WebApp Integration

#### Frontend Changes (index.html)

Replace the hardcoded TELEGRAM_ID with real Telegram WebApp data:

```javascript
// Load Telegram WebApp SDK
<script src="https://telegram.org/js/telegram-web-app.js"></script>

// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand(); // Expand to full screen
tg.enableClosingConfirmation(); // Prevent accidental closing

// Get user data from Telegram
const telegramUser = tg.initDataUnsafe?.user;

if (!telegramUser) {
    // Not opened in Telegram - show error
    document.body.innerHTML = `
        <div class="min-h-screen flex items-center justify-center bg-gaming-dark p-4">
            <div class="text-center">
                <div class="text-6xl mb-4">🚫</div>
                <h1 class="text-2xl font-bold text-brand-gold mb-2">Access Denied</h1>
                <p class="text-gray-400">This app must be opened through Telegram.</p>
                <p class="text-sm text-gray-500 mt-4">Please use the Telegram bot to access the game.</p>
            </div>
        </div>
    `;
    throw new Error('Not opened in Telegram');
}

// Extract Telegram user data
const TELEGRAM_ID = telegramUser.id;
const TELEGRAM_USERNAME = telegramUser.username || '';
const TELEGRAM_FIRST_NAME = telegramUser.first_name || '';
const TELEGRAM_LAST_NAME = telegramUser.last_name || '';
const TELEGRAM_PHOTO_URL = telegramUser.photo_url || '';
```

### 2. Backend Authentication Endpoint

Add Telegram WebApp data validation in API:

```python
# app/api.py

from hashlib import sha256
import hmac

def validate_telegram_webapp_data(init_data: str, bot_token: str) -> dict:
    """
    Validate Telegram WebApp initData
    Returns user data if valid, raises HTTPException if invalid
    """
    try:
        # Parse init_data
        data_dict = {}
        for item in init_data.split('&'):
            key, value = item.split('=', 1)
            data_dict[key] = value
        
        # Extract hash
        received_hash = data_dict.pop('hash', None)
        if not received_hash:
            raise HTTPException(status_code=401, detail="No hash in init data")
        
        # Create data-check-string
        data_check_arr = [f"{k}={v}" for k, v in sorted(data_dict.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            sha256
        ).hexdigest()
        
        # Compare hashes
        if calculated_hash != received_hash:
            raise HTTPException(status_code=401, detail="Invalid init data hash")
        
        # Parse user data
        import json
        import urllib.parse
        user_data = json.loads(urllib.parse.unquote(data_dict.get('user', '{}')))
        
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Init data validation failed: {str(e)}")


@app.post("/api/auth/telegram")
async def telegram_auth(init_data: str):
    """
    Authenticate user via Telegram WebApp
    Automatically creates account if doesn't exist
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Validate init data
    telegram_user = validate_telegram_webapp_data(init_data, bot_token)
    
    # Get or create user
    user = DatabaseService.get_user_by_telegram_id(telegram_user['id'])
    
    if not user:
        # Auto-register new user
        user_data = {
            "telegram_id": telegram_user['id'],
            "username": telegram_user.get('username'),
            "first_name": telegram_user.get('first_name'),
            "last_name": telegram_user.get('last_name'),
            "points": 0,
            "total_earned_points": 0,
            "is_active": True
        }
        user = DatabaseService.create_user(user_data)
    
    return {
        "user": user,
        "message": "Authenticated successfully"
    }
```

### 3. Security Features

#### A. Init Data Validation
- Validates Telegram WebApp initData using HMAC-SHA256
- Prevents unauthorized access
- Ensures data comes from Telegram

#### B. Bot Token Security
- Store bot token securely in environment variables
- Never expose in frontend code
- Use server-side validation only

#### C. Session Management
- Telegram WebApp provides secure session
- No need for JWT tokens
- User data verified on each request

### 4. User Experience Flow

```
1. User opens bot in Telegram
   ↓
2. Bot sends WebApp button or inline URL
   ↓
3. User clicks to open mini app
   ↓
4. WebApp loads with Telegram context
   ↓
5. Frontend extracts user data from Telegram.WebApp
   ↓
6. Frontend sends initData to backend for validation
   ↓
7. Backend validates and auto-registers user
   ↓
8. User can now participate in quests
```

### 5. Database Schema (Already Implemented)

The `users` table already supports Telegram authentication:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    points INTEGER DEFAULT 0,
    total_earned_points INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### 6. Bot Integration

Update the Telegram bot to provide WebApp access:

```python
# app/telegram_bot.py

async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with WebApp button"""
    user = update.effective_user
    
    # WebApp URL (replace with your actual URL)
    webapp_url = os.getenv("WEBAPP_URL", "https://your-app-url.com")
    
    keyboard = [
        [InlineKeyboardButton("🎮 Open Game", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
        [InlineKeyboardButton("👤 My Profile", callback_data="view_profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🎉 Welcome to Gaming Quest Hub, {user.first_name}!

Tap "🎮 Open Game" to launch the web app and start completing quests!

You can also:
• View available tasks
• Check your profile
• See the leaderboard
    """
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
```

### 7. Environment Variables Required

Add to `.env`:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBAPP_URL=https://your-codespaces-url-8080.app.github.dev
```

### 8. Frontend Loading States

Add loading screen while authenticating:

```html
<!-- Loading Screen -->
<div id="authLoading" class="fixed inset-0 bg-gaming-dark flex items-center justify-center z-50">
    <div class="text-center">
        <div class="text-6xl mb-4 animate-bounce">🎮</div>
        <h2 class="text-2xl font-bold text-brand-gold mb-2">Loading Game...</h2>
        <p class="text-gray-400">Authenticating with Telegram</p>
        <div class="mt-4 flex justify-center gap-2">
            <div class="w-2 h-2 bg-brand-gold rounded-full animate-pulse"></div>
            <div class="w-2 h-2 bg-brand-gold rounded-full animate-pulse delay-100"></div>
            <div class="w-2 h-2 bg-brand-gold rounded-full animate-pulse delay-200"></div>
        </div>
    </div>
</div>
```

### 9. Error Handling

```javascript
// Handle authentication errors
async function authenticateUser() {
    try {
        // Show loading
        document.getElementById('authLoading').classList.remove('hidden');
        
        // Get Telegram init data
        const initData = tg.initData;
        
        if (!initData) {
            throw new Error('No Telegram init data available');
        }
        
        // Send to backend for validation
        const response = await fetch(`${API_URL}/auth/telegram`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ init_data: initData })
        });
        
        if (!response.ok) {
            throw new Error('Authentication failed');
        }
        
        const data = await response.json();
        
        // Store user data
        window.currentUser = data.user;
        
        // Hide loading, show app
        document.getElementById('authLoading').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden');
        
        // Load initial data
        loadUserData();
        loadTasks();
        
    } catch (error) {
        console.error('Authentication error:', error);
        document.getElementById('authLoading').innerHTML = `
            <div class="text-center p-4">
                <div class="text-6xl mb-4">❌</div>
                <h2 class="text-2xl font-bold text-brand-red mb-2">Authentication Failed</h2>
                <p class="text-gray-400 mb-4">${error.message}</p>
                <button onclick="location.reload()" 
                        class="px-6 py-3 bg-brand-gold text-gaming-dark rounded-xl font-bold">
                    Try Again
                </button>
            </div>
        `;
    }
}
```

### 10. Testing & Development

For local development without Telegram:

```javascript
// Development mode (only for testing)
const IS_DEV_MODE = window.location.hostname === 'localhost' && 
                    new URLSearchParams(window.location.search).get('dev') === 'true';

if (IS_DEV_MODE) {
    console.warn('⚠️ Running in DEV MODE - using mock Telegram data');
    window.Telegram = {
        WebApp: {
            initDataUnsafe: {
                user: {
                    id: 123456789,
                    first_name: 'Test',
                    last_name: 'User',
                    username: 'testuser'
                }
            },
            expand: () => {},
            enableClosingConfirmation: () => {},
            initData: 'mock_init_data_for_testing'
        }
    };
}
```

## Benefits of Telegram-Only Auth

✅ **Automatic Registration**: No signup forms needed
✅ **Verified Identity**: Telegram verifies phone numbers
✅ **Single Sign-On**: Users already logged into Telegram
✅ **No Password Management**: Telegram handles authentication
✅ **Spam Prevention**: Phone verification reduces fake accounts
✅ **Seamless UX**: Opens directly from bot
✅ **Push Notifications**: Can send updates via bot
✅ **Profile Data**: Get username, name, photo automatically

## Implementation Checklist

- [ ] Add Telegram WebApp SDK to index.html
- [ ] Replace hardcoded TELEGRAM_ID with real data
- [ ] Add loading/error screens
- [ ] Implement backend validation endpoint
- [ ] Update bot to provide WebApp button
- [ ] Add WEBAPP_URL to environment variables
- [ ] Test authentication flow
- [ ] Add error handling
- [ ] Test on mobile devices
- [ ] Document for users

## Next Steps

1. **Implement Frontend Auth** - Replace hardcoded ID
2. **Add Backend Validation** - Secure init data check
3. **Update Bot Commands** - Add WebApp button
4. **Test End-to-End** - Full authentication flow
5. **Deploy to Production** - Update environment variables

## Additional Resources

- [Telegram WebApps Documentation](https://core.telegram.org/bots/webapps)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Validating WebApp Data](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
