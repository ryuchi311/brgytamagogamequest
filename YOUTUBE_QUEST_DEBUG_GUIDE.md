# YouTube Quest Debug Guide

## 🔍 Investigation Complete - Comprehensive Debugging Added

I've added **extensive console logging** throughout the entire YouTube quest workflow to identify exactly where the code input box issue is occurring.

## 📋 Testing Instructions

### 1. Open Browser Console
- Open the web app in your browser
- Press `F12` or `Right-click → Inspect`
- Go to the **Console** tab

### 2. Start a YouTube Quest
- Click on any YouTube quest from the quest list
- Watch the console output

### 3. Monitor the Flow

You should see console messages at each step:

#### **Step 1: Page Load**
```
📄 SHOW QUEST DETAIL PAGE
   Task: {object details}
   Points: 1000
   Task type: youtube
   🔧 Generating dynamic content...
```

#### **Step 2: Content Generation**
```
📦 GENERATE QUEST CONTENT
   Task type: youtube
   🎬 Generating YouTube quest content
   ✅ YouTube content rendered, watch time set to: 30
   🔍 Code input section verification: <div id="codeInputSection">...
   Code input section exists: true
```

#### **Step 3: Click "Watch Video" Button**
```
🎥 START YOUTUBE QUEST
Current task URL: https://youtube.com/...
Required watch time: 30
✅ Opened video in new tab
Watch button found: <button id="watchVideoBtn">
✅ Timer displayed
Watch task element found: <div data-task-id="watch">
🚀 Starting timer...
```

#### **Step 4: Timer Running**
```
🎬 START TIMER - Required time: 30
📊 Timer config: {elapsed: 0, totalTime: 30}
⏱️ Timer: 5/30 seconds (25 remaining)
⏱️ Timer: 10/30 seconds (20 remaining)
⏱️ Timer: 15/30 seconds (15 remaining)
...
```

#### **Step 5: Timer Complete (CRITICAL)**
```
✅ TIMER COMPLETE! Calling unlockCodeInput...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔓 UNLOCK CODE INPUT CALLED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ Watch task element: <div>
   ✅ Watch task marked complete
2️⃣ Submit task element: <div>
   Lock overlay: <div class="task-lock">
   ✅ Lock overlay removed
   ✅ Submit task unlocked
3️⃣ Looking for code input section...
   Code input section element: <div id="codeInputSection">
   Element exists: true
   Element parent: <div id="questDynamicContent">
   Element classes: hidden mb-4
   Element current display: 
   Element computed display: none
   🔧 Removing hidden class...
   🔧 Setting display to block...
   🔧 Setting visibility...
   ✅ Code input section should now be visible!
   Final display: block
   Final computed display: block
   📜 Scrolling to code input...
   Input field: <input id="verificationCodeInput">
   ✅ Input field focused
4️⃣ Watch button: <button>
   ✅ Watch button hidden
5️⃣ Timer status element: <span>
   ✅ Timer status updated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 UNLOCK CODE INPUT FINISHED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 What to Look For

### ✅ If Everything Works:
All console logs should appear in order, and you should see:
- `Element exists: true`
- `Final display: block`
- `Final computed display: block`
- The code input box should appear on screen

### ❌ If Code Input Doesn't Appear:

Look for these indicators in the console:

1. **Element Not Found**
   ```
   ❌❌❌ CODE INPUT SECTION NOT FOUND! ❌❌❌
   🔍 Searching for ALL elements with codeInput in ID:
   ```
   → The HTML wasn't generated properly

2. **Element Exists But Hidden**
   ```
   Element exists: true
   Final computed display: none  ← PROBLEM HERE
   ```
   → CSS is overriding the display

3. **No Logs After Timer Complete**
   ```
   ⏱️ Timer: 30/30 seconds (0 remaining)
   (nothing happens)
   ```
   → unlockCodeInput() is not being called

## 📊 Report Back

Please run through the YouTube quest and **copy-paste the entire console output** here. This will show us exactly where the flow is breaking.

## 🎯 Expected Behavior

After timer completes, you should see:
1. **Green box appears** with heading "✅ Timer complete! You can now submit."
2. **Large input field** with placeholder "Enter the code from video"
3. **Green button** saying "Submit Code & Claim Reward"
4. The page **auto-scrolls** to bring the input into view
5. The input field is **auto-focused** (cursor blinking)

## 🚀 Quick Test

For faster testing, you can temporarily reduce the timer to 5 seconds:

1. Open frontend/index.html
2. Find line ~1979 (in generateQuestContent)
3. Change:
   ```javascript
   requiredWatchTime = verificationData.min_watch_time || verificationData.min_watch_time_seconds || 30;
   ```
   To:
   ```javascript
   requiredWatchTime = 5; // Quick test
   ```

This will make the timer only 5 seconds instead of 30, so you can test faster.

---

**The debugging system is now active.** Every function in the YouTube quest flow will log detailed information to help us find the exact point of failure.
