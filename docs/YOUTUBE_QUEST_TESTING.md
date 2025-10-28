# 🧪 YouTube Quest Testing Guide

## Quick Test Procedure

### Setup (Do Once)
1. Login to Admin Panel
2. Create a test YouTube quest:
   - **Title:** "Test Video Quest"
   - **URL:** Any YouTube video URL
   - **Verification Code:** `GAMING2024`
   - **Points:** 100
   - **Method:** video_code
3. Save and activate quest

---

## Test Scenarios

### ✅ Test 1: No Code Entered (Should FAIL)

**Steps:**
1. Open web app as regular user
2. Click on "Test Video Quest"
3. Modal opens showing code input field
4. **DO NOT** enter any code
5. Click "Complete Quest" button

**Expected Result:**
- ⚠️ Alert: "Please enter the verification code from the video!"
- Quest modal stays open
- Quest NOT marked as complete
- No XP awarded
- ✅ **PASS if blocked**

---

### ✅ Test 2: Wrong Code Entered (Should FAIL)

**Steps:**
1. Open web app as regular user
2. Click on "Test Video Quest"
3. Modal opens showing code input field
4. Enter: `WRONGCODE`
5. Click "Complete Quest" button

**Expected Result:**
- ❌ Error message: "Incorrect verification code. Watch the video carefully!"
- Quest NOT marked as complete
- No XP awarded
- Code input field remains visible
- ✅ **PASS if rejected**

---

### ✅ Test 3: Correct Code Entered (Should SUCCEED)

**Steps:**
1. Open web app as regular user
2. Click on "Test Video Quest"
3. Modal opens showing code input field
4. Enter: `GAMING2024` (correct code)
5. Click "Complete Quest" button

**Expected Result:**
- ✅ Success message: "Video quest completed! Code verified."
- Quest marked as complete
- 100 XP awarded to user
- Quest disappears from available quests
- User's total XP increases
- ✅ **PASS if completed**

---

### ✅ Test 4: Case Insensitive (Should SUCCEED)

**Steps:**
1. Open web app as regular user
2. Click on another YouTube quest
3. Enter code in different case: `gaming2024` (lowercase)
4. Click "Complete Quest" button

**Expected Result:**
- ✅ Success message
- Quest completed (case-insensitive matching)
- XP awarded
- ✅ **PASS if accepted**

---

### ✅ Test 5: Duplicate Completion (Should FAIL)

**Steps:**
1. Complete a YouTube quest successfully
2. Try to complete the SAME quest again
3. Enter correct code again

**Expected Result:**
- ❌ Error: "Task already completed" or quest not available
- No additional XP awarded
- ✅ **PASS if prevented**

---

## Browser Console Check

Open browser console (F12) and check for:

### ✅ Code Input Field Shows
```javascript
// Should see code input section
document.getElementById('codeInputSection').classList
// Should NOT contain 'hidden'
```

### ✅ Request Includes Code
```javascript
// In Network tab, check /api/verify request body:
{
  "telegram_id": 123456789,
  "task_id": "task-uuid",
  "verification_code": "GAMING2024"  // ← Should be present
}
```

### ✅ Response Validation
```javascript
// Success response:
{
  "success": true,
  "message": "✅ Video quest completed! Code verified.",
  "points_earned": 100,
  "new_total": 500
}

// Error response (wrong code):
{
  "success": false,
  "message": "❌ Incorrect verification code...",
  "requires_code": true
}
```

---

## Backend Logs Check

Check server logs for proper validation:

### ✅ Correct Flow
```
INFO: YouTube quest verification
INFO: Task type: youtube
INFO: Method: video_code
INFO: Code provided: GAMING2024
INFO: Code matches! Completing quest
INFO: User awarded 100 XP
```

### ✅ Error Flow (Wrong Code)
```
INFO: YouTube quest verification
INFO: Task type: youtube
INFO: Method: video_code
INFO: Code provided: WRONGCODE
WARNING: Code mismatch! Expected: GAMING2024, Got: WRONGCODE
INFO: Returning error to user
```

---

## Database Verification

### Check user_tasks Table
```sql
SELECT * FROM user_tasks 
WHERE task_id = 'your-task-id' 
  AND user_id = 'your-user-id';
```

**Expected:**
- `status`: 'completed' (only if code was correct)
- `points_earned`: 100
- `completed_at`: timestamp

### Check users Table
```sql
SELECT points FROM users WHERE id = 'your-user-id';
```

**Expected:**
- Points increased by quest reward (only if completed)

---

## Common Issues & Solutions

### Issue: Code input field not showing
**Cause:** Task type or method mismatch
**Fix:** Check `verification_data.method` is `video_code` or `youtube_code`

### Issue: Quest completes without code
**Cause:** Old backend code still running
**Fix:** Restart API server to load new code

### Issue: Always shows "wrong code"
**Cause:** Code field name mismatch
**Fix:** Check quest uses `verification_code` not `code`

### Issue: Case sensitive validation
**Cause:** Missing .upper() conversion
**Fix:** Verify backend uses case-insensitive comparison

---

## Success Criteria

All tests must pass:
- [x] Test 1: Blocks submission without code
- [x] Test 2: Rejects wrong code
- [x] Test 3: Accepts correct code
- [x] Test 4: Case insensitive
- [x] Test 5: Prevents duplicate completion

**If all pass → YouTube verification is working correctly! ✅**

---

## Quick Verification Commands

```bash
# Check API is running
curl http://localhost:8000/health

# Test with correct code
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "task_id": "your-task-id",
    "verification_code": "GAMING2024"
  }'

# Test with wrong code
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "task_id": "your-task-id",
    "verification_code": "WRONGCODE"
  }'
```

---

**Status:** Ready for testing! 🎮
