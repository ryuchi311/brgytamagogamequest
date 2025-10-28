# Telegram Verification Issue - Troubleshooting Guide

## Problem: "Not a member in group" error when user has already joined

### Quick Diagnosis

Run this command to test the verification:
```bash
./debug_telegram_verification.sh
```

This will:
1. Test the Telegram Bot API with your group
2. Check the user's actual membership status
3. Show if verification should pass or fail
4. Provide specific solutions

## Common Causes & Solutions

### 1. Wrong Chat ID Format

**Problem:** Quest has incorrect `chat_id` in `verification_data`

**Check:**
```sql
SELECT id, title, verification_data 
FROM tasks 
WHERE platform = 'telegram';
```

**Solutions:**

**For Public Groups (@username):**
```json
{
  "chat_id": "@tamagowarriors",
  "chat_name": "Tamago Warriors",
  "method": "api"
}
```

**For Private Groups/Supergroups (numeric ID):**
```json
{
  "chat_id": "-1001234567890",
  "chat_name": "Private VIP Group",
  "method": "api"
}
```

**How to get Chat ID:**
1. Add your bot to the group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for: `"chat":{"id":-1001234567890}`

### 2. Bot Not in Group

**Problem:** Bot (@bt_taskerbot) hasn't been added to the target group

**Check:**
```bash
# Test if bot can access the group
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChat?chat_id=@tamagowarriors"
```

**Solution:**
1. Open the Telegram group
2. Click "Add Members"
3. Search for: @bt_taskerbot
4. Add the bot
5. Bot should appear in member list

### 3. Wrong User Telegram ID

**Problem:** User's `telegram_id` in database doesn't match their actual Telegram ID

**Check user's Telegram ID:**
1. User starts bot: /start
2. Bot shows: "Your Telegram ID: 123456789"
3. Check database:
```sql
SELECT telegram_id, username 
FROM users 
WHERE telegram_id = 123456789;
```

**Solution:**
- User must use the same Telegram account that's registered in the app
- If using Telegram Mini App, ID should auto-sync
- If using manual registration, verify ID is correct

### 4. User Actually Left the Group

**Problem:** User joined, verified, then left the group

**Check:**
```bash
# Run debug script with user's ID
./debug_telegram_verification.sh
# Status will show "left" if user left the group
```

**Solution:**
- User needs to rejoin the group
- Check with: "Are you currently in the group?"

### 5. Channel vs Group Permissions

**Problem:** Quest is for a channel, not a group

**Note:** Channels require different bot permissions

**For Channels:**
- Bot must be added as an **administrator**
- Bot needs "View Messages" permission
- Chat ID starts with `-100` (e.g., `-1001234567890`)

**For Groups:**
- Bot can be regular member
- No admin rights needed
- Chat ID starts with `-` or uses `@username`

## Step-by-Step Debugging

### Step 1: Test Bot Connection
```bash
./diagnose_telegram_quest.sh
```

Expected output:
```
✅ Bot is working!
   Bot Name: BrgyTamago
   Bot Username: @bt_taskerbot
```

### Step 2: Test Specific Verification
```bash
./debug_telegram_verification.sh
```

Enter:
- Chat ID from your quest (e.g., `@tamagowarriors`)
- User's Telegram ID (e.g., `7988161711`)

### Step 3: Check Backend Logs
```bash
# Watch verification in real-time
./monitor_logs.sh backend

# Or check recent logs
tail -n 100 backend.log | grep -A 20 "Telegram Verification Debug"
```

Look for:
```
🔍 Telegram Verification Debug:
   Task ID: xxx
   Chat ID: @tamagowarriors
   User Telegram ID: 7988161711
   Response Status: 200
   Member Status: member
✅ Verification successful! User is a member
```

### Step 4: Verify Quest Configuration
```bash
# Check quest in database
psql $DATABASE_URL -c "
SELECT 
  id, 
  title, 
  platform,
  task_type,
  verification_data::json->>'chat_id' as chat_id,
  verification_data::json->>'method' as method
FROM tasks 
WHERE platform = 'telegram'
"
```

Should show:
```
| id   | title              | chat_id        | method |
|------|--------------------|----------------|--------|
| uuid | Join Tamago Group  | @tamagowarriors | api    |
```

## Testing Checklist

Before users try to verify:

- [ ] Bot (@bt_taskerbot) is added to the target group ✓
- [ ] Bot appears in group member list ✓
- [ ] Quest has correct `chat_id` in `verification_data` ✓
- [ ] User has actually joined the group ✓
- [ ] User is using correct Telegram account ✓
- [ ] Run `./debug_telegram_verification.sh` - should show "member" status ✓

## Real-Time Debugging

When user reports "not a member" error:

**Step 1: Get User's Telegram ID**
```bash
# Ask user to send /start to bot
# Bot will reply with their Telegram ID
```

**Step 2: Get Quest Chat ID**
```bash
# Find the quest they're trying to complete
SELECT verification_data FROM tasks WHERE id = 'quest_id';
```

**Step 3: Test with Debug Script**
```bash
./debug_telegram_verification.sh
# Enter chat_id and user's telegram_id
# Script will show exact status
```

**Step 4: Fix Based on Status**

| Status | Meaning | Solution |
|--------|---------|----------|
| `member` | User IS in group | ✅ Should work - check logs |
| `left` | User LEFT group | ❌ User must rejoin |
| `kicked` | User was banned | ❌ Admin must unban |
| `restricted` | User restricted but in group | ✅ Should work |
| Error 403 | Bot not in group | ❌ Add bot to group |
| Error 400 | Invalid chat_id | ❌ Fix chat_id in quest |

## Frontend Error Messages

User-friendly messages now shown:

| Backend Error | User Sees |
|---------------|-----------|
| Bot not in group | "❌ Bot is not in the group. Please contact admin to add the bot first." |
| Chat not found | "❌ Group not found. Please check the group link and try again." |
| User not found | "❌ User not found. Please make sure you're using the correct Telegram account." |
| Status: left | "❌ You are not a member of [group name]. Please join first! (Status: left)" |
| Status: kicked | "❌ You are not a member of [group name]. Please join first! (Status: kicked)" |

## Backend Improvements Made

### Enhanced Error Handling
```python
# Now provides specific error messages based on error type
if 'bot is not a member' in error_description.lower():
    verification_message = "❌ Bot is not in the group. Please contact admin..."
elif 'chat not found' in error_description.lower():
    verification_message = "❌ Group not found. Please check the group link..."
```

### Better Logging
```python
# Logs now show:
print(f"   Chat ID: {chat_id}")
print(f"   User Telegram ID: {telegram_id}")
print(f"   Member Status: {member_status}")
print(f"   Response Data: {data}")
```

## Quick Fix Commands

```bash
# 1. Test bot works
./diagnose_telegram_quest.sh

# 2. Debug specific user verification
./debug_telegram_verification.sh

# 3. Monitor verification attempts live
./monitor_logs.sh backend | grep "Telegram Verification"

# 4. Check quest configuration
psql $DATABASE_URL -c "SELECT * FROM tasks WHERE platform='telegram'"

# 5. Restart backend after changes
./restart.sh
```

## Example: Successful Verification

**Backend logs should show:**
```
🔍 Telegram Verification Debug:
   Task ID: abc-123
   Task Type: telegram_join_group
   Platform: telegram
   Bot Token: 8373360183:AAEnV...
   Chat ID: @tamagowarriors
   User Telegram ID: 7988161711
   Verification Data: {'chat_id': '@tamagowarriors', 'method': 'api'}
   API URL: https://api.telegram.org/bot8373360183...
   Params: {'chat_id': '@tamagowarriors', 'user_id': 7988161711}
   Calling Telegram Bot API...
   Response Status: 200
   Response Data: {'ok': True, 'result': {'status': 'member', 'user': {...}}}
   Member Status: member
   User Info: {'id': 7988161711, 'first_name': 'John', 'username': 'johndoe'}
✅ Verification successful! User is a member
   📢 Sending announcement to group...
   ✅ Announcement sent successfully!
```

**User sees:**
```
✅ Telegram membership verified! Welcome to Tamago Warriors
+100 points earned
```

**Group sees:**
```
🎉 New Member Joined!

✅ John (@johndoe) has successfully verified 
and joined the Brgy Tamago Quest Hub!

🎮 Congratulations and welcome to the community! 🚀
💎 Points earned: 100
```

## Still Not Working?

If after all checks it still fails:

1. **Check exact error from backend logs:**
   ```bash
   tail -f backend.log
   ```

2. **Test with curl directly:**
   ```bash
   curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChatMember?chat_id=@tamagowarriors&user_id=7988161711"
   ```

3. **Contact Support with:**
   - User's Telegram ID
   - Quest chat_id
   - Backend log output
   - Result from debug script

## Summary

✅ Created: `debug_telegram_verification.sh` - Interactive debugging  
✅ Improved: Error messages - More user-friendly  
✅ Enhanced: Logging - Shows all verification details  
✅ Added: Specific solutions for each error type  

**Use `./debug_telegram_verification.sh` to diagnose any verification issues!**
