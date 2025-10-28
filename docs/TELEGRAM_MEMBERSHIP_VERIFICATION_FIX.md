# Telegram Membership Verification Troubleshooting

## Issue: "User Already Joined but Verification Says Not a Member"

This document helps diagnose and fix Telegram membership verification issues where users have joined the group but the bot still says they're not a member.

## Quick Diagnosis

Run this command to see all possible issues:
```bash
./diagnose_membership_issue.sh
```

Run this command to test a specific user and group:
```bash
./test_telegram_membership.sh
```

## Common Causes & Solutions

### 1. Wrong Chat ID Format ❌

**Problem:** The `verification_data.chat_id` in the quest has the wrong format.

**Check:**
```bash
curl -s http://localhost:8000/api/tasks | jq '.[] | select(.task_type == "telegram") | {id, title, chat_id: .verification_data.chat_id}'
```

**Valid Formats:**
- Public groups/channels: `@username` (e.g., `@tamagowarriors`)
- Private supergroups: `-1001234567890` (starts with `-100`)
- Regular groups: `-1234567890` (negative number)

**How to Get Correct Chat ID:**
1. Forward a message from the group to [@userinfobot](https://t.me/userinfobot)
2. Or add [@RawDataBot](https://t.me/RawDataBot) to the group and check its message
3. Or use your bot: Add it to the group and check bot logs

**Fix:** Update the quest in admin panel with correct chat_id

---

### 2. Bot Not in Group ❌

**Problem:** Bot must be a member of the group to check user membership.

**Check:**
```bash
# Get your bot username
grep TELEGRAM_BOT_TOKEN .env | head -1

# Then manually verify bot is in the group
```

**Solution:**
1. Get your bot username from the token (it's in `.env`)
2. Go to the Telegram group
3. Click "Add Members" or group settings
4. Search for your bot username (e.g., `@bt_taskerbot`)
5. Add the bot as a member
6. For channels, make the bot an admin

**Test:**
```bash
./test_telegram_membership.sh
# Choose option 1 and enter task ID
```

---

### 3. User Privacy Settings ❌

**Problem:** User's privacy settings prevent bot from seeing their membership.

**Symptoms:**
- API returns error about user not found
- Or returns status "left" even though user is in group

**Solution (User must do this):**
1. User sends `/start` to your bot
2. This allows bot to interact with user
3. Wait 5 seconds
4. Try verification again

---

### 4. User Not Actually Joined ❌

**Problem:** User thinks they joined but didn't complete the process.

**User Instructions:**
1. Click the group/channel link
2. Wait for Telegram to open the group
3. Click the **"JOIN"** or **"JOIN CHANNEL"** button
4. Wait for confirmation (you'll see group messages)
5. **Wait 5-10 seconds** for Telegram API to update
6. Go back to Quest Hub
7. Click **"Verify Me"**

**Note:** Just opening the group link is NOT the same as joining!

---

### 5. Telegram API Delay ⏱️

**Problem:** Telegram API takes time to sync membership data.

**Solution:**
- User should wait 5-10 seconds after joining before clicking verify
- If failed, wait 30 seconds and try again
- Don't spam the verify button

---

### 6. Task Type Mismatch ❌

**Problem:** Quest has wrong task_type or missing verification_data.

**Check Task Configuration:**
```bash
curl -s http://localhost:8000/api/tasks | jq '.[] | select(.id == "YOUR_TASK_ID_HERE")'
```

**Required Fields:**
```json
{
  "task_type": "telegram",
  "platform": "telegram",
  "url": "https://t.me/groupusername",
  "verification_data": {
    "type": "join_group",
    "method": "telegram_membership",
    "chat_id": "@groupusername",
    "chat_name": "Group Name",
    "invite_link": "https://t.me/groupusername"
  }
}
```

**Valid task_type values:**
- `telegram`
- `telegram_group`
- `telegram_channel`

**Fix:** Update quest in admin panel with correct structure

---

## Testing Tools

### Tool 1: Quick Diagnostic
Shows all common issues and checks quest configuration:
```bash
./diagnose_membership_issue.sh
```

### Tool 2: Membership Tester
Interactive tool to test specific user and group:
```bash
./test_telegram_membership.sh
```

**What it checks:**
- ✅ Bot token is valid
- ✅ Chat exists and bot has access
- ✅ Bot is a member of the chat
- ✅ User's membership status
- ✅ Exact API response from Telegram

**Choose Option 1:** Test by Task ID (automatically gets chat_id from database)
**Choose Option 2:** Manual test (enter chat_id and user_id yourself)

### Tool 3: Monitor Logs
Watch real-time verification attempts:
```bash
./monitor_logs.sh backend
```

Look for:
```
🔍 Telegram Verification Debug:
   Task ID: xxx
   Chat ID: @groupname
   User Telegram ID: 123456789
   Response Status: 200
   Member Status: member
```

---

## Step-by-Step Debugging

### Step 1: Verify Quest Configuration
```bash
# List all Telegram quests
curl -s http://localhost:8000/api/tasks | jq '.[] | select(.task_type == "telegram") | {id, title, chat_id: .verification_data.chat_id}'
```

**Check:**
- [ ] `chat_id` exists in `verification_data`
- [ ] `chat_id` format is correct
- [ ] `chat_name` is set (for error messages)

### Step 2: Verify Bot Setup
```bash
# Check bot token
grep TELEGRAM_BOT_TOKEN .env

# Test bot
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

**Check:**
- [ ] Bot token is valid (response shows bot info)
- [ ] Bot username is correct
- [ ] Bot is added to the group

### Step 3: Test User Membership
```bash
./test_telegram_membership.sh
```

**Enter:**
- Task ID (e.g., `f510f52a-7bc5-4e11-a260-31251fa780a6`)
- User's Telegram ID (numeric)

**Expected Output:**
```
✅ Chat found!
   Title: Brgy Tamago Warriors
   Type: supergroup
✅ Bot is a member!
   Status: administrator
✅ VERIFICATION SHOULD PASS
   User is a valid member with status: member
```

### Step 4: Check User Actually Joined

Ask user to:
1. Open Telegram
2. Go to the group
3. Check if they see group messages
4. Check if they can send messages (if not restricted)
5. Send `/start` to your bot
6. Wait 10 seconds
7. Try verification again

---

## Manual API Testing

Test directly with Telegram Bot API:

```bash
# Get bot info
curl "https://api.telegram.org/bot<BOT_TOKEN>/getMe"

# Get chat info
curl "https://api.telegram.org/bot<BOT_TOKEN>/getChat?chat_id=@groupusername"

# Check user membership
curl "https://api.telegram.org/bot<BOT_TOKEN>/getChatMember?chat_id=@groupusername&user_id=123456789"
```

**Expected Response for Member:**
```json
{
  "ok": true,
  "result": {
    "user": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "User Name",
      "username": "username"
    },
    "status": "member"
  }
}
```

**Valid Status Values:**
- ✅ `creator` - Group creator (passes verification)
- ✅ `administrator` - Admin (passes verification)
- ✅ `member` - Regular member (passes verification)
- ✅ `restricted` - Restricted but member (passes verification)
- ❌ `left` - User left the group (fails verification)
- ❌ `kicked` - User banned (fails verification)

---

## Common Error Messages

### "Bot is not a member of the chat"
**Error Code:** 403  
**Cause:** Bot not added to group  
**Fix:** Add bot to the group

### "Chat not found"
**Error Code:** 400  
**Cause:** Wrong chat_id format or group doesn't exist  
**Fix:** Verify chat_id in quest configuration

### "User not found"
**Error Code:** 400  
**Cause:** Wrong user_id or user never interacted with bot  
**Fix:** User sends /start to bot

### "You are not a member of the group"
**Cause:** User status is "left" or "kicked"  
**Fix:** User needs to (re)join the group

---

## Quick Fix Checklist

Before contacting support, verify:

- [ ] Quest has correct `verification_data.chat_id`
- [ ] Bot is added to the group
- [ ] Bot has permission to see members
- [ ] User has sent `/start` to the bot
- [ ] User has clicked JOIN in the group (not just opened link)
- [ ] User waited 5-10 seconds after joining
- [ ] User's Telegram ID in database matches their actual ID
- [ ] No typos in group username (if using @username)

---

## Still Not Working?

1. **Run the test tool:**
   ```bash
   ./test_telegram_membership.sh
   ```

2. **Share the output** with your developer

3. **Check backend logs:**
   ```bash
   ./monitor_logs.sh backend
   ```

4. **Verify with raw API:**
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getChatMember?chat_id=@groupname&user_id=123456789" | jq '.'
   ```

---

## For Developers

### API Verification Flow

1. User clicks "Verify Me" button
2. Frontend calls `POST /api/tasks/{task_id}/verify`
3. Backend extracts `verification_data.chat_id`
4. Backend calls Telegram Bot API `getChatMember`
5. Backend checks if status in `['creator', 'administrator', 'member', 'restricted']`
6. If yes: Award points, send announcement to group
7. If no: Return error message with status

### Relevant Code

**File:** `app/api.py`  
**Function:** `verify_task()`  
**Line:** ~429-550

**Key Logic:**
```python
if task_type.startswith('telegram_') or task_type == 'telegram' or task.get('platform') == 'telegram':
    chat_id = verification_data.get('chat_id')
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    params = {"chat_id": chat_id, "user_id": telegram_id}
    response = requests.get(url, params=params, timeout=10)
    
    if data.get('ok'):
        member_status = data.get('result', {}).get('status')
        if member_status in ['creator', 'administrator', 'member', 'restricted']:
            verification_success = True
```

### Adding Debug Logging

Already implemented! Check logs with:
```bash
./monitor_logs.sh backend
```

Look for:
```
🔍 Telegram Verification Debug:
   Task ID: xxx
   Chat ID: @xxx
   Response Data: {...}
   Member Status: xxx
```

---

## Related Documentation

- [Telegram Bot Setup Guide](./TELEGRAM_BOT_SETUP_GUIDE.md)
- [Telegram Auth Quick Guide](./TELEGRAM_AUTH_QUICK_GUIDE.md)
- [Quest Types Guide](./QUEST_TYPES_GUIDE.md)
