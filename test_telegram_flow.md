# Telegram Quest Flow Test

## Test Steps:

1. **Initial State**
   - Button should show: "Join Now"
   
2. **After clicking "Join Now"**
   - Telegram link should open (WebApp API or new window)
   - Button text should change to: "🔍 Verify Me"
   - Console should log: "✅ Opened Telegram link using WebApp API"
   - Console should log: "✅ Button changed to 'Verify Me'"

3. **After clicking "Verify Me"**
   - Button text should change to: "⏳ Verifying..."
   - Backend API called: `/complete-task`
   - Body includes: `telegram_id` and `task_id`

4. **If User is Member (Success)**
   - Button text: "✅ VERIFIED!"
   - Alert: "🎉 Membership Verified! +[points] XP earned!"
   - Redirects back to quest list
   - Points added to user profile

5. **If User is NOT Member (Failure)**
   - Button text returns to: "🔍 Verify Me"
   - Alert: "❌ Not a member yet. Please join the group first!"
   - User can click "Verify Me" again

## Backend Verification Process:

The backend (`app/api.py`) should:
1. Get `chat_id` from `verification_data` column in database
2. Get user's `telegram_id` from request
3. Call Telegram Bot API:
   ```
   GET https://api.telegram.org/bot{BOT_TOKEN}/getChatMember
   ?chat_id={chat_id}
   &user_id={telegram_id}
   ```
4. Check if `member_status` is: `creator`, `administrator`, `member`, or `restricted`
5. If yes → Award points, return success
6. If no → Return error message

## Database Requirements:

Task should have in `verification_data`:
```json
{
  "chat_id": "@your_telegram_group",
  "method": "telegram_verification"
}
```

Or:
```json
{
  "chat_id": "-1001234567890",  // numeric chat ID
  "method": "telegram_verification"
}
```

## Environment Variables:

Required in `.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Console Debugging:

Open browser console (F12) and watch for:
- "✅ Opened Telegram link using WebApp API"
- "✅ Button changed to 'Verify Me'"
- API request/response logs
- Error messages if verification fails
