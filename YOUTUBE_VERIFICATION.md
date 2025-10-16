# 🎥 YouTube Video Verification System

## Overview
Methods to verify users actually watched YouTube videos for quests.

---

## ✅ Recommended Implementation: Secret Code Method

### How It Works:
1. Edit your YouTube video to show a secret code at specific timestamp
2. User watches video to find the code
3. User submits code via Telegram bot
4. Bot verifies and awards XP

### Video Setup:
- **Timestamp:** 2:30 (or 80% through video)
- **Display:** Text overlay: "Secret Code: QUEST2024"
- **Duration:** Show for 5-10 seconds
- **Position:** Center of screen, bright color

---

## 📝 Database Schema Addition

Add verification fields to tasks table:

```sql
ALTER TABLE tasks ADD COLUMN verification_method VARCHAR(50);
ALTER TABLE tasks ADD COLUMN verification_data JSONB;

-- Example data:
{
  "method": "secret_code",
  "code": "QUEST2024",
  "timestamp": "2:30"
}

-- Or for quiz:
{
  "method": "quiz",
  "questions": [
    {
      "question": "What color was shown at 1:30?",
      "options": ["Red", "Blue", "Green", "Yellow"],
      "correct": "Blue"
    }
  ]
}
```

---

## 🤖 Bot Implementation

### Update app/telegram_bot.py

Add verification handler:

```python
async def verify_video_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle video verification codes"""
    user_id = update.effective_user.id
    message_text = update.message.text.upper()
    
    # Check if message is a verification code
    try:
        response = await self.api_client.get(f'/tasks?verification_required=true')
        tasks = response.json()
        
        for task in tasks:
            if task.get('verification_data', {}).get('method') == 'secret_code':
                expected_code = task['verification_data']['code'].upper()
                
                if message_text == expected_code:
                    # Complete the task
                    await self.api_client.post(
                        f'/users/{user_id}/tasks/{task["id"]}/complete'
                    )
                    
                    await update.message.reply_text(
                        f"🎉 Correct code!\n\n"
                        f"✅ Quest '{task['title']}' completed!\n"
                        f"💎 +{task['points_reward']} XP earned!",
                        reply_markup=self._main_menu_keyboard()
                    )
                    return
        
        # No matching code found
        await update.message.reply_text(
            "❌ Invalid verification code.\n\n"
            "Watch the YouTube videos in your quests to find secret codes!"
        )
        
    except Exception as e:
        logger.error(f"Error verifying video: {e}")
        await update.message.reply_text("❌ Error verifying code. Try again.")


# Register handler in __init__
self.application.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, 
    self.verify_video_task
))
```

### Update Tasks Command

```python
async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available tasks with verification info"""
    user_id = update.effective_user.id
    
    try:
        response = await self.api_client.get('/tasks')
        tasks = response.json()
        
        if not tasks:
            await update.message.reply_text("No quests available right now.")
            return
        
        message = "⚔️ **AVAILABLE QUESTS** ⚔️\n\n"
        
        for task in tasks:
            verification_info = ""
            if task.get('verification_data'):
                method = task['verification_data'].get('method')
                if method == 'secret_code':
                    verification_info = "\n🔐 Enter the secret code from the video"
                elif method == 'quiz':
                    verification_info = "\n❓ Answer quiz questions after watching"
            
            message += (
                f"{'⭐' if task['is_bonus'] else '📋'} **{task['title']}**\n"
                f"💎 Reward: {task['points_reward']} XP\n"
                f"📝 {task['description']}\n"
                f"{verification_info}\n\n"
            )
        
        keyboard = []
        for task in tasks:
            keyboard.append([
                InlineKeyboardButton(
                    f"{'⭐' if task['is_bonus'] else '📋'} {task['title']}", 
                    callback_data=f"task_{task['id']}"
                )
            ])
        
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        await update.message.reply_text("Error loading quests.")
```

---

## 🎮 Admin Dashboard Integration

### Update frontend/admin.html

Add verification fields to task creation:

```javascript
// In showAddTaskModal()
const verificationSection = `
<div class="mb-4">
    <label class="block text-sm font-bold text-neon-purple mb-2">
        🔐 VERIFICATION METHOD
    </label>
    <select id="taskVerificationMethod" class="w-full bg-black/50 border-2 border-neon-purple/30 rounded-xl px-4 py-3 text-white gaming-body">
        <option value="none">No Verification</option>
        <option value="secret_code">Secret Code (YouTube)</option>
        <option value="quiz">Quiz Questions</option>
        <option value="manual">Manual Admin Review</option>
    </select>
</div>

<div id="secretCodeField" class="mb-4 hidden">
    <label class="block text-sm font-bold text-neon-green mb-2">
        SECRET CODE
    </label>
    <input type="text" id="taskSecretCode" class="w-full bg-black/50 border-2 border-neon-green/30 rounded-xl px-4 py-3 text-white gaming-body" placeholder="e.g., QUEST2024">
    <p class="text-xs text-gray-400 mt-1">Code users must find in the video</p>
</div>

<div id="quizField" class="mb-4 hidden">
    <label class="block text-sm font-bold text-neon-yellow mb-2">
        QUIZ QUESTION
    </label>
    <input type="text" id="quizQuestion" class="w-full bg-black/50 border-2 border-neon-yellow/30 rounded-xl px-4 py-3 text-white gaming-body mb-2" placeholder="What was discussed in the video?">
    <input type="text" id="quizAnswer" class="w-full bg-black/50 border-2 border-neon-yellow/30 rounded-xl px-4 py-3 text-white gaming-body" placeholder="Correct answer">
</div>
`;

// Add to task form
document.getElementById('taskForm').insertAdjacentHTML('beforeend', verificationSection);

// Show/hide fields based on method
document.getElementById('taskVerificationMethod').addEventListener('change', (e) => {
    const method = e.target.value;
    document.getElementById('secretCodeField').classList.toggle('hidden', method !== 'secret_code');
    document.getElementById('quizField').classList.toggle('hidden', method !== 'quiz');
});
```

### Update submitTask() function:

```javascript
async function submitTask(event) {
    event.preventDefault();
    
    const verificationMethod = document.getElementById('taskVerificationMethod').value;
    let verificationData = null;
    
    if (verificationMethod === 'secret_code') {
        verificationData = {
            method: 'secret_code',
            code: document.getElementById('taskSecretCode').value
        };
    } else if (verificationMethod === 'quiz') {
        verificationData = {
            method: 'quiz',
            question: document.getElementById('quizQuestion').value,
            answer: document.getElementById('quizAnswer').value
        };
    }
    
    const taskData = {
        title: document.getElementById('taskTitle').value,
        description: document.getElementById('taskDescription').value,
        task_type: document.getElementById('taskType').value,
        platform: document.getElementById('taskPlatform').value || null,
        url: document.getElementById('taskUrl').value || null,
        points_reward: parseInt(document.getElementById('taskPoints').value),
        is_bonus: document.getElementById('taskBonus').checked,
        verification_required: verificationMethod !== 'none',
        verification_data: verificationData
    };
    
    try {
        const response = await fetch(`${API_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(taskData)
        });
        
        if (response.ok) {
            alert('✅ Quest created successfully!');
            closeModal('taskModal');
            loadTasks();
            document.getElementById('taskForm').reset();
        }
    } catch (error) {
        console.error('Error creating task:', error);
        alert('❌ Failed to create quest');
    }
}
```

---

## 🎯 Alternative: Quiz Method

For quiz-based verification:

```python
# In bot
async def handle_quiz_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quiz answers for video quests"""
    query = update.callback_query
    await query.answer()
    
    # Parse callback data: quiz_<task_id>_<answer>
    _, task_id, user_answer = query.data.split('_')
    
    try:
        response = await self.api_client.get(f'/tasks/{task_id}')
        task = response.json()
        
        verification_data = task.get('verification_data', {})
        correct_answer = verification_data.get('answer', '').lower()
        
        if user_answer.lower() == correct_answer:
            # Complete task
            await self.api_client.post(
                f'/users/{query.from_user.id}/tasks/{task_id}/complete'
            )
            
            await query.edit_message_text(
                f"🎉 Correct answer!\n\n"
                f"✅ Quest '{task['title']}' completed!\n"
                f"💎 +{task['points_reward']} XP earned!"
            )
        else:
            await query.edit_message_text(
                "❌ Wrong answer!\n\n"
                "Watch the video carefully and try again."
            )
            
    except Exception as e:
        logger.error(f"Error handling quiz: {e}")
```

---

## 📊 Analytics Tracking

Track verification success rates:

```sql
-- Add to database
CREATE TABLE verification_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    attempt_data JSONB,
    success BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track metrics
SELECT 
    task_id,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100 as success_rate
FROM verification_attempts
GROUP BY task_id;
```

---

## 🎬 Video Production Tips

### For Secret Code Method:
1. **Timing:** Place code at 75-90% through video
2. **Duration:** Show for 8-10 seconds
3. **Design:** High contrast, large text
4. **Animation:** Fade in/out for visibility
5. **Audio:** Mention "secret code for quest" verbally

### Example Code Styles:
```
🎮 SECRET CODE: QUEST2024 🎮
⚔️ QUEST CODE: GAMING123 ⚔️
💎 LOOT CODE: WATCH2024 💎
```

### Tools:
- **Video editing:** DaVinci Resolve (free)
- **Text overlays:** Canva, Photoshop
- **Animation:** After Effects, Keynote

---

## 🚀 Quick Start

1. **Create Quest with Verification:**
   - Go to Admin Dashboard
   - Click "Add Quest"
   - Set verification method to "Secret Code"
   - Enter code: `QUEST2024`
   - Save quest

2. **Edit Your Video:**
   - Add text overlay at 2:30
   - Show code: `QUEST2024`
   - Display for 8 seconds

3. **Test:**
   - Send `/tasks` in bot
   - Click your video quest
   - Watch video
   - Type `QUEST2024` in chat
   - Should get XP reward!

---

## 📈 Success Metrics

Track these metrics:
- % of users who click link
- % who submit verification
- % who succeed on first try
- Average time to completion
- Verification method preferences

---

## 🔒 Anti-Cheat Measures

1. **Rate Limiting:** Max 3 attempts per task per user
2. **Time Gating:** Must wait 2+ minutes before submitting code
3. **Code Rotation:** Change codes weekly
4. **Unique Codes:** Generate user-specific codes (advanced)
5. **Manual Review:** Flag suspicious instant completions

---

## 🎯 Best Practices

✅ **DO:**
- Make codes easy to read and type
- Place codes where they can't be missed
- Test the flow before launching
- Reward legitimate users quickly
- Provide clear instructions

❌ **DON'T:**
- Make codes too complex
- Hide codes in hard-to-see places
- Require perfect timing
- Punish honest mistakes
- Make verification frustrating

---

**🎥 This system balances ease of use with effective verification!**
