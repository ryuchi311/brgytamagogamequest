# 🎮 Quest Types Implementation - Location Guide

## ✅ ALL QUEST TYPES ARE ALREADY IN YOUR ADMIN PANEL!

**File:** `frontend/admin.html` (1654 lines)  
**Status:** ✅ FULLY IMPLEMENTED  
**Access:** http://localhost/admin.html

---

## 📍 Exact Line Numbers in admin.html

### 🎯 Quest Type Selector (Lines 369-393)

```html
<!-- Line 369 -->
<label class="block text-neon-blue gaming-title text-sm mb-3">SELECT QUEST TYPE</label>
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
    
    <!-- Line 371: Twitter Button -->
    <button onclick="selectQuestType('twitter')" data-type="twitter">
        <div class="text-3xl mb-2">🐦</div>
        <div class="text-sm gaming-title">Twitter</div>
    </button>
    
    <!-- Line 375: YouTube Button -->
    <button onclick="selectQuestType('youtube')" data-type="youtube">
        <div class="text-3xl mb-2">📺</div>
        <div class="text-sm gaming-title">YouTube</div>
    </button>
    
    <!-- Line 379: Telegram Button ✅ NEW! -->
    <button onclick="selectQuestType('telegram')" data-type="telegram">
        <div class="text-3xl mb-2">✈️</div>
        <div class="text-sm gaming-title">Telegram</div>
    </button>
    
    <!-- Line 383: Daily Check-in Button ✅ NEW! -->
    <button onclick="selectQuestType('daily')" data-type="daily">
        <div class="text-3xl mb-2">📅</div>
        <div class="text-sm gaming-title">Daily Check-in</div>
    </button>
    
    <!-- Line 387: Manual Button ✅ NEW! -->
    <button onclick="selectQuestType('manual')" data-type="manual">
        <div class="text-3xl mb-2">✍️</div>
        <div class="text-sm gaming-title">Manual</div>
    </button>
</div>
```

---

## 📋 Quest-Specific Configuration Forms

### 🐦 Twitter Form (Lines 413-443)

**Location:** Line 413  
**ID:** `twitterFields`  
**Theme:** Blue border, bg-blue-900/20

**Fields:**
- Action Type dropdown (line 418)
  - Follow Account
  - Like Tweet
  - Retweet
  - Reply to Tweet
- Target Username (line 427)
- Tweet URL (line 433, conditional display)
- Auto-verification notice (line 439)

```html
<!-- Line 413 -->
<div id="twitterFields" class="hidden border-2 border-neon-blue/30 rounded-xl p-5 bg-blue-900/20">
    <h3>🐦 Twitter Quest Configuration</h3>
    
    <select id="twitterActionType">
        <option value="follow">Follow Account</option>
        <option value="like">Like Tweet</option>
        <option value="retweet">Retweet</option>
        <option value="reply">Reply to Tweet</option>
    </select>
    
    <input id="twitterUsername" placeholder="username">
    <input id="twitterTweetUrl" placeholder="https://twitter.com/...">
    
    <div class="p-3 bg-neon-blue/10">
        ⚡ Auto-Verification: Uses Twitter API (Rate limited: 100 checks/day)
    </div>
</div>
```

---

### ✈️ Telegram Form (Lines 445-486) ✅ NEW!

**Location:** Line 445  
**ID:** `telegramFields`  
**Theme:** Cyan border, bg-cyan-900/20

**Fields:**
- Action Type dropdown (line 450)
  - Join Group/Supergroup
  - Subscribe to Channel
- Telegram Link (line 457)
- Group/Channel ID (line 463)
- Chat Name (line 469)
- Bot permission notice (line 475)

```html
<!-- Line 445 -->
<div id="telegramFields" class="hidden border-2 border-cyan-500/30 rounded-xl p-5 bg-cyan-900/20">
    <h3>✈️ Telegram Quest Configuration</h3>
    
    <select id="telegramActionType">
        <option value="join_group">Join Group/Supergroup</option>
        <option value="join_channel">Subscribe to Channel</option>
    </select>
    
    <input id="telegramLink" placeholder="https://t.me/yourgroupname">
    <input id="telegramChatId" placeholder="-1001234567890 or @channelname">
    <input id="telegramChatName" placeholder="My Awesome Channel">
    
    <div class="p-3 bg-cyan-500/10">
        ⚡ Auto-Verification: Bot API checks membership
        ⚠️ Bot must be admin with "See Members" permission
    </div>
</div>
```

---

### 📺 YouTube Form (Lines 488-525) ✅

**Location:** Line 488  
**ID:** `youtubeFields`  
**Theme:** Red border, bg-red-900/20

**Fields:**
- Video URL (line 493)
- Secret Code (line 498)
- Minimum Watch Time in seconds (line 505)
- Max Attempts (line 510)
- Code Hint/Timestamp (line 517)

```html
<!-- Line 488 -->
<div id="youtubeFields" class="hidden border-2 border-red-500/30 rounded-xl p-5 bg-red-900/20">
    <h3>📺 YouTube Video Quest</h3>
    
    <input id="youtubeUrl" placeholder="https://youtube.com/watch?v=...">
    <input id="youtubeSecretCode" placeholder="e.g., QUEST2025">
    
    <input id="youtubeMinWatchTime" type="number" value="120" min="30" max="3600">
    <input id="youtubeMaxAttempts" type="number" value="3" min="1" max="10">
    <input id="youtubeCodeHint" placeholder="e.g., 2:30 or at the end">
    
    <div class="p-3 bg-red-500/10">
        ⚡ How it works: User watches video, enters code shown in video. Watch time is tracked.
    </div>
</div>
```

---

### 📅 Daily Check-in Form (Lines 527-558) ✅ NEW!

**Location:** Line 527  
**ID:** `dailyFields`  
**Theme:** Green border, bg-green-900/20

**Fields:**
- Streak Bonus Type dropdown (line 532)
  - No Bonus
  - Multiply by Streak
  - Milestone Bonuses
- Reset Time in UTC (line 541)
- Require Consecutive Days checkbox (line 547)

```html
<!-- Line 527 -->
<div id="dailyFields" class="hidden border-2 border-neon-green/30 rounded-xl p-5 bg-green-900/20">
    <h3>📅 Daily Check-in Quest</h3>
    
    <select id="dailyStreakBonus">
        <option value="none">No Bonus</option>
        <option value="multiply">Multiply by Streak</option>
        <option value="milestone">Milestone Bonuses</option>
    </select>
    
    <input id="dailyResetTime" type="time" value="00:00">
    <input id="dailyConsecutiveRequired" type="checkbox">
    
    <div class="p-3 bg-neon-green/10">
        ⚡ Auto-Completion: Simple click, server checks date
        📈 Bonus Examples: Day 7 = 7x XP or +100 bonus
    </div>
</div>
```

---

### ✍️ Manual Form (Lines 560-596) ✅ NEW!

**Location:** Line 560  
**ID:** `manualFields`  
**Theme:** Purple border, bg-purple-900/20

**Fields:**
- External URL (line 565)
- Submission Type dropdown (line 571)
  - No submission required
  - Text/Link submission
  - Screenshot upload
  - Code submission
- Detailed Instructions textarea (line 580)

```html
<!-- Line 560 -->
<div id="manualFields" class="hidden border-2 border-neon-purple/30 rounded-xl p-5 bg-purple-900/20">
    <h3>✍️ Manual Verification Quest</h3>
    
    <input id="manualUrl" placeholder="https://example.com (optional)">
    
    <select id="manualSubmissionType">
        <option value="none">No submission required</option>
        <option value="text">Text/Link submission</option>
        <option value="screenshot">Screenshot upload</option>
        <option value="code">Code submission</option>
    </select>
    
    <textarea id="manualInstructions" rows="4" 
        placeholder="1. Visit the website&#10;2. Complete the task&#10;3. Submit proof">
    </textarea>
    
    <div class="p-3 bg-neon-purple/10">
        ⚡ Admin Review Required
        📋 Use for: Website visits, contests, surveys, custom challenges
    </div>
</div>
```

---

## 🔧 JavaScript Functions (Lines 1090-1650)

### selectQuestType() - Line 1536

**Purpose:** Shows/hides appropriate quest form based on selection

```javascript
// Line 1536
function selectQuestType(type) {
    selectedQuestType = type;
    
    // Update button styles (purple for selected)
    document.querySelectorAll('.quest-type-btn').forEach(btn => {
        if (btn.dataset.type === type) {
            btn.classList.add('border-neon-purple', 'bg-neon-purple/20');
        } else {
            btn.classList.remove('border-neon-purple', 'bg-neon-purple/20');
        }
    });
    
    // Show common fields
    document.querySelector('.common-fields').style.display = 'block';
    
    // Hide all specific fields first
    document.querySelectorAll('#twitterFields, #telegramFields, #youtubeFields, #dailyFields, #manualFields')
        .forEach(el => el.classList.add('hidden'));
    
    // Show selected fields
    if (type === 'twitter') {
        document.getElementById('twitterFields').classList.remove('hidden');
    } else if (type === 'telegram') {
        document.getElementById('telegramFields').classList.remove('hidden');
    } else if (type === 'youtube') {
        document.getElementById('youtubeFields').classList.remove('hidden');
    } else if (type === 'daily') {
        document.getElementById('dailyFields').classList.remove('hidden');
    } else if (type === 'manual') {
        document.getElementById('manualFields').classList.remove('hidden');
    }
}
```

---

### submitTask() - Lines 1090-1250

**Purpose:** Validates and submits quest with type-specific configuration

```javascript
// Line 1090
async function submitTask() {
    // ... validation code ...
    
    // Build verification_data based on quest type
    if (selectedQuestType === 'twitter') {
        const action = document.getElementById('twitterActionType').value;
        const username = document.getElementById('twitterUsername').value;
        const tweetUrl = document.getElementById('twitterTweetUrl')?.value;
        
        taskData.task_type = `twitter_${action}`;
        taskData.verification_data = {
            verification_method: 'twitter_api',
            username: username,
            action: action,
            tweet_url: tweetUrl || null,
            tweet_id: extractTweetId(tweetUrl)
        };
    }
    
    else if (selectedQuestType === 'telegram') {
        const action = document.getElementById('telegramActionType').value;
        taskData.task_type = `telegram_${action}`;
        taskData.verification_data = {
            verification_method: 'telegram_membership',
            action_type: action,
            link: document.getElementById('telegramLink').value,
            chat_id: document.getElementById('telegramChatId').value,
            chat_name: document.getElementById('telegramChatName').value
        };
    }
    
    else if (selectedQuestType === 'youtube') {
        taskData.task_type = 'youtube_watch';
        taskData.verification_data = {
            verification_method: 'time_delay_code',
            video_url: document.getElementById('youtubeUrl').value,
            secret_code: document.getElementById('youtubeSecretCode').value,
            min_watch_time: parseInt(document.getElementById('youtubeMinWatchTime').value),
            max_attempts: parseInt(document.getElementById('youtubeMaxAttempts').value),
            code_hint: document.getElementById('youtubeCodeHint').value
        };
    }
    
    else if (selectedQuestType === 'daily') {
        taskData.task_type = 'daily_checkin';
        taskData.verification_data = {
            verification_method: 'daily_checkin',
            streak_bonus: document.getElementById('dailyStreakBonus').value,
            reset_time: document.getElementById('dailyResetTime').value,
            consecutive_required: document.getElementById('dailyConsecutiveRequired').checked
        };
    }
    
    else if (selectedQuestType === 'manual') {
        taskData.task_type = 'manual_review';
        taskData.verification_data = {
            verification_method: 'manual_review',
            url: document.getElementById('manualUrl').value || null,
            submission_type: document.getElementById('manualSubmissionType').value,
            instructions: document.getElementById('manualInstructions').value
        };
    }
    
    // Submit to API
    const response = await fetch(url, { method, headers, body: JSON.stringify(taskData) });
}
```

---

## 🎯 How to Access and Use

### Step 1: Open Admin Panel
```bash
URL: http://localhost/admin.html
Login: admin / changeme123
```

### Step 2: Navigate to Quests Tab
- Click **⚔️ QUESTS** in the top navigation
- You'll see the "MANAGE QUESTS" section
- Click **➕ CREATE QUEST** button

### Step 3: Quest Creation Modal Opens
You'll see the modal with:
- Title: "CREATE NEW QUEST ×"
- **SELECT QUEST TYPE** section with 5 buttons in a responsive grid

### Step 4: Click a Quest Type Button
**What happens when you click each button:**

1. **🐦 Twitter** - Shows blue-themed Twitter form
   - Dropdown with 4 action types
   - Username and optional tweet URL fields
   
2. **📺 YouTube** - Shows red-themed YouTube form
   - Video URL and secret code
   - Watch time and attempt limits
   
3. **✈️ Telegram** - Shows cyan-themed Telegram form
   - Group/channel action selector
   - Link, chat ID, and name fields
   
4. **📅 Daily** - Shows green-themed Daily form
   - Streak bonus configuration
   - Reset time settings
   
5. **✍️ Manual** - Shows purple-themed Manual form
   - Submission type selector
   - Custom instructions field

### Step 5: Fill Quest Details
- Common fields appear for all types:
  - Quest Title
  - Description
  - XP Reward
- Type-specific fields appear below

### Step 6: Submit
- Click **🚀 CREATE QUEST**
- Quest appears in the list immediately
- Status: ✓ ACTIVE (green badge)

---

## 🔍 Visual Changes When Selecting Quest Types

### Button State Changes
```css
/* Default State */
.quest-type-btn {
    border: 2px solid rgba(59, 130, 246, 0.3);  /* Light blue border */
    background: rgba(0, 0, 0, 0.5);
}

/* Selected State (purple highlight) */
.quest-type-btn.selected {
    border: 2px solid #A855F7;  /* Neon purple border */
    background: rgba(168, 85, 247, 0.2);  /* Purple glow */
}

/* Hover State */
.quest-type-btn:hover {
    border: 2px solid #3B82F6;  /* Bright blue */
    transform: scale(1.05);  /* Slight grow */
}
```

### Form Visibility
```javascript
// Initially: All forms hidden
<div id="twitterFields" class="hidden">
<div id="telegramFields" class="hidden">
<div id="youtubeFields" class="hidden">
<div id="dailyFields" class="hidden">
<div id="manualFields" class="hidden">

// After clicking Twitter button:
<div id="twitterFields" class="">  <!-- 'hidden' removed -->
<div id="telegramFields" class="hidden">
// ... others stay hidden
```

---

## 📱 Mobile Responsive Design

### Desktop (≥1024px)
```
[🐦]  [📺]  [✈️]  [📅]  [✍️]
 Twitter YouTube Telegram Daily Manual
```
- All 5 buttons in a row
- Grid: `grid-cols-6` (6 columns, 1 empty)

### Tablet (768px - 1023px)
```
[🐦]  [📺]  [✈️]
 Twitter YouTube Telegram

[📅]  [✍️]
 Daily Manual
```
- Grid: `md:grid-cols-3` (3 columns per row)

### Mobile (<768px)
```
[🐦]  [📺]
Twitter YouTube

[✈️]  [📅]
Telegram Daily

[✍️]
Manual
```
- Grid: `grid-cols-2` (2 columns per row)

---

## ✅ Implementation Status Summary

| Feature | Status | Lines | Details |
|---------|--------|-------|---------|
| Quest Type Selector | ✅ Complete | 369-393 | 5 buttons with emojis |
| Twitter Form | ✅ Complete | 413-443 | 4 action types, API integration |
| Telegram Form | ✅ Complete | 445-486 | 2 action types, Bot API ready |
| YouTube Form | ✅ Complete | 488-525 | Time+code verification |
| Daily Form | ✅ Complete | 527-558 | Streak bonuses, auto-reset |
| Manual Form | ✅ Complete | 560-596 | 4 submission types, flexible |
| selectQuestType() | ✅ Complete | 1536-1600 | Form switching logic |
| submitTask() | ✅ Complete | 1090-1250 | All 5 types handled |
| Mobile Responsive | ✅ Complete | Grid | 2/3/6 column layout |
| Visual Feedback | ✅ Complete | CSS | Purple highlight on select |

---

## 🚀 Everything is Ready!

**You don't need to make any changes!** All quest types are already implemented in your current `frontend/admin.html` file.

Just:
1. Open http://localhost/admin.html
2. Login with admin/changeme123
3. Click ⚔️ QUESTS tab
4. Click ➕ CREATE QUEST
5. **Click any quest type button to see the specialized forms!**

The forms switch instantly when you click different quest type buttons. Try it! 🎮
