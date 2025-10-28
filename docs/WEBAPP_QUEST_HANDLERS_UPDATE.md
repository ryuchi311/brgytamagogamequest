# 🌐 WEB APP QUEST HANDLERS UPDATE

**Complete Guide for Updating Web App to Support Modular Quest Handlers**

---

## 📋 Overview

This guide shows how to update the frontend web app to properly display and handle all 5 quest types with the new modular backend handlers.

---

## 🎯 Quest Types Supported

| Quest Type | Platform | Handler | Verification |
|------------|----------|---------|--------------|
| Telegram | `telegram` | TelegramQuestHandler | Automatic |
| Twitter | `twitter` | TwitterQuestHandler | Manual |
| YouTube | `youtube` | YouTubeQuestHandler | Code verification |
| Social Media | Various | SocialMediaQuestHandler | Manual |
| Website | `website` | WebsiteLinkQuestHandler | Auto/Timer/Manual |

---

## 🔧 Frontend Updates Needed

### 1. Quest Detection & Display

The frontend needs to detect quest type and show appropriate UI:

```javascript
function getQuestTypeInfo(task) {
    const platform = task.platform?.toLowerCase() || '';
    const verificationData = task.verification_data || {};
    const method = verificationData.method || '';
    
    // Telegram Quest
    if (platform === 'telegram' && method === 'telegram_membership') {
        return {
            type: 'telegram',
            emoji: '📱',
            color: 'blue',
            buttonText: 'Join & Verify',
            needsCode: false,
            instant: true
        };
    }
    
    // Twitter Quest
    if (platform === 'twitter' && method === 'twitter_action') {
        const actionType = verificationData.action_type || 'follow';
        return {
            type: 'twitter',
            emoji: '🐦',
            color: 'sky',
            buttonText: `${actionType.charAt(0).toUpperCase() + actionType.slice(1)} & Submit`,
            needsCode: false,
            instant: false,
            actionType: actionType
        };
    }
    
    // YouTube Quest
    if (platform === 'youtube' && method === 'youtube_code') {
        return {
            type: 'youtube',
            emoji: '🎥',
            color: 'red',
            buttonText: 'Watch & Enter Code',
            needsCode: true,
            instant: true,
            hint: verificationData.hint || 'Find the code in the video'
        };
    }
    
    // Social Media Quest
    if (verificationData.method === 'social_media_action') {
        const platformEmojis = {
            'discord': '💬',
            'instagram': '📸',
            'tiktok': '🎵',
            'facebook': '👥',
            'linkedin': '💼',
            'reddit': '🤖',
            'github': '💻'
        };
        
        return {
            type: 'social_media',
            emoji: platformEmojis[platform] || '🌐',
            color: 'purple',
            buttonText: 'Complete & Submit',
            needsCode: false,
            instant: false,
            platform: platform
        };
    }
    
    // Website Quest
    if (platform === 'website' || method === 'auto_complete' || 
        method === 'timer_based' || method === 'manual') {
        
        let buttonText = 'Visit & Claim';
        let instant = true;
        
        if (method === 'timer_based') {
            const timer = verificationData.timer_seconds || 30;
            buttonText = `Visit (${timer}s)`;
            instant = false;
        } else if (method === 'manual') {
            buttonText = 'Complete & Submit';
            instant = false;
        }
        
        return {
            type: 'website',
            emoji: '🌐',
            color: 'green',
            buttonText: buttonText,
            needsCode: false,
            instant: instant,
            method: method,
            timer: verificationData.timer_seconds
        };
    }
    
    // Fallback
    return {
        type: 'general',
        emoji: '🎯',
        color: 'gray',
        buttonText: 'Complete Quest',
        needsCode: false,
        instant: false
    };
}
```

---

### 2. Quest Modal Display

Update the modal to show quest-specific information:

```javascript
function showTaskDetail(taskIndex) {
    const task = window.tasksData[taskIndex];
    if (!task) return;
    
    const questInfo = getQuestTypeInfo(task);
    
    // Store current task
    currentTask = task;
    currentTaskId = task.id;
    currentTaskUrl = task.url;
    currentQuestInfo = questInfo;
    
    // Update modal content
    document.getElementById('modalTitle').textContent = task.title;
    document.getElementById('modalDescription').textContent = task.description || 'Complete this quest to earn points!';
    document.getElementById('modalEmoji').textContent = questInfo.emoji;
    document.getElementById('modalPlatform').textContent = task.platform.toUpperCase();
    document.getElementById('modalPoints').textContent = `+${task.points_reward} XP`;
    
    // Update button
    const completeBtn = document.getElementById('completeTaskBtn');
    completeBtn.textContent = questInfo.buttonText;
    completeBtn.className = `w-full py-4 px-6 bg-${questInfo.color}-600 hover:bg-${questInfo.color}-700 text-white font-bold rounded-lg transition-all`;
    
    // Show/hide code input
    const codeSection = document.getElementById('codeInputSection');
    if (questInfo.needsCode) {
        codeSection.classList.remove('hidden');
        if (questInfo.hint) {
            document.getElementById('codeHint').textContent = questInfo.hint;
            document.getElementById('codeHint').classList.remove('hidden');
        }
    } else {
        codeSection.classList.add('hidden');
    }
    
    // Show verification type badge
    const verificationBadge = document.getElementById('verificationBadge');
    if (questInfo.instant) {
        verificationBadge.textContent = '⚡ Instant Verification';
        verificationBadge.className = 'inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm';
    } else {
        verificationBadge.textContent = '⏳ Manual Verification';
        verificationBadge.className = 'inline-block px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm';
    }
    
    // Show modal
    document.getElementById('taskModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}
```

---

### 3. Quest Completion Logic

Handle different completion flows:

```javascript
async function completeTask() {
    if (!currentTaskId || !currentQuestInfo) return;
    
    const questType = currentQuestInfo.type;
    
    try {
        switch (questType) {
            case 'telegram':
                await completeTelegramQuest();
                break;
            case 'twitter':
                await completeTwitterQuest();
                break;
            case 'youtube':
                await completeYouTubeQuest();
                break;
            case 'social_media':
                await completeSocialMediaQuest();
                break;
            case 'website':
                await completeWebsiteQuest();
                break;
            default:
                await completeGeneralQuest();
        }
    } catch (error) {
        console.error('Quest completion error:', error);
        showAlert('❌ Error completing quest. Please try again.', 'error');
    }
}

// Telegram Quest - Instant verification
async function completeTelegramQuest() {
    // Open Telegram link
    if (currentTaskUrl) {
        window.open(currentTaskUrl, '_blank');
    }
    
    // Wait a moment for user to join
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Verify membership via bot
    const response = await fetch(`${API_URL}/verify-telegram`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telegram_id: TELEGRAM_ID,
            task_id: currentTaskId
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        showAlert(`✅ Quest completed! +${currentTask.points_reward} XP`, 'success');
        closeTaskModal();
        await loadUserData();
    } else {
        showAlert(result.message || '❌ Please join the channel first!', 'error');
    }
}

// Twitter Quest - Manual verification
async function completeTwitterQuest() {
    // Open Twitter link
    if (currentTaskUrl) {
        window.open(currentTaskUrl, '_blank');
    }
    
    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Submit for verification
    const response = await fetch(`${API_URL}/submit-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telegram_id: TELEGRAM_ID,
            task_id: currentTaskId,
            platform: 'twitter'
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        showAlert('✅ Submitted for verification! Admin will review soon.', 'success');
        closeTaskModal();
    } else {
        showAlert(result.message || '❌ Submission failed', 'error');
    }
}

// YouTube Quest - Code verification
async function completeYouTubeQuest() {
    const code = document.getElementById('verificationCode').value.trim();
    
    if (!code) {
        showAlert('⚠️ Please enter the verification code from the video!', 'warning');
        return;
    }
    
    // Open YouTube link
    if (currentTaskUrl) {
        window.open(currentTaskUrl, '_blank');
    }
    
    // Verify code
    const response = await fetch(`${API_URL}/verify-youtube-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telegram_id: TELEGRAM_ID,
            task_id: currentTaskId,
            code: code
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        showAlert(`✅ Correct code! +${currentTask.points_reward} XP`, 'success');
        closeTaskModal();
        await loadUserData();
    } else {
        showAlert('❌ Incorrect code. Watch the video carefully!', 'error');
    }
}

// Social Media Quest - Manual verification
async function completeSocialMediaQuest() {
    // Open link
    if (currentTaskUrl) {
        window.open(currentTaskUrl, '_blank');
    }
    
    // Wait a moment
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Submit for verification
    const response = await fetch(`${API_URL}/submit-verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            telegram_id: TELEGRAM_ID,
            task_id: currentTaskId,
            platform: currentTask.platform
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        showAlert('✅ Submitted for verification! Admin will review soon.', 'success');
        closeTaskModal();
    } else {
        showAlert(result.message || '❌ Submission failed', 'error');
    }
}

// Website Quest - Auto/Timer/Manual
async function completeWebsiteQuest() {
    const method = currentQuestInfo.method;
    
    // Open website
    if (currentTaskUrl) {
        window.open(currentTaskUrl, '_blank');
    }
    
    if (method === 'auto_complete') {
        // Auto-complete - instant claim
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const response = await fetch(`${API_URL}/complete-task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                telegram_id: TELEGRAM_ID,
                task_id: currentTaskId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`✅ Quest completed! +${currentTask.points_reward} XP`, 'success');
            closeTaskModal();
            await loadUserData();
        }
    } else if (method === 'timer_based') {
        // Timer-based - show countdown
        const timer = currentQuestInfo.timer || 30;
        showTimerCountdown(timer);
    } else {
        // Manual verification
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const response = await fetch(`${API_URL}/submit-verification`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                telegram_id: TELEGRAM_ID,
                task_id: currentTaskId,
                platform: 'website'
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('✅ Submitted for verification!', 'success');
            closeTaskModal();
        }
    }
}

// Timer countdown for website quests
function showTimerCountdown(seconds) {
    let remaining = seconds;
    const completeBtn = document.getElementById('completeTaskBtn');
    const originalText = completeBtn.textContent;
    
    completeBtn.disabled = true;
    
    const interval = setInterval(() => {
        remaining--;
        completeBtn.textContent = `⏱️ Please wait ${remaining}s...`;
        
        if (remaining <= 0) {
            clearInterval(interval);
            completeBtn.disabled = false;
            completeBtn.textContent = '🎁 Claim XP';
            
            // Enable claiming
            completeBtn.onclick = async () => {
                const response = await fetch(`${API_URL}/complete-task`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        telegram_id: TELEGRAM_ID,
                        task_id: currentTaskId
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAlert(`✅ Quest completed! +${currentTask.points_reward} XP`, 'success');
                    closeTaskModal();
                    await loadUserData();
                }
            };
        }
    }, 1000);
}
```

---

### 4. Quest Card Display

Update quest cards to show quest type badges:

```javascript
function renderQuestCard(task, index) {
    const questInfo = getQuestTypeInfo(task);
    const isCompleted = task.completed || false;
    
    return `
        <div class="quest-card bg-gray-900/60 border-2 border-${questInfo.color}-500/30 rounded-xl p-4 hover:border-${questInfo.color}-500 transition-all cursor-pointer"
             onclick="showTaskDetail(${index})">
            
            <!-- Header -->
            <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3">
                    <div class="text-3xl">${questInfo.emoji}</div>
                    <div>
                        <h3 class="font-bold text-white">${task.title}</h3>
                        <p class="text-xs text-${questInfo.color}-400">${task.platform.toUpperCase()}</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-brand-gold font-bold">+${task.points_reward} XP</div>
                    ${task.is_bonus ? '<div class="text-xs text-yellow-400">🌟 BONUS</div>' : ''}
                </div>
            </div>
            
            <!-- Description -->
            <p class="text-sm text-gray-400 mb-3 line-clamp-2">${task.description || 'Complete this quest to earn points!'}</p>
            
            <!-- Footer -->
            <div class="flex items-center justify-between">
                <div class="flex gap-2">
                    ${questInfo.instant 
                        ? '<span class="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded-full">⚡ Instant</span>'
                        : '<span class="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded-full">⏳ Review</span>'}
                    ${questInfo.needsCode 
                        ? '<span class="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full">🔑 Code</span>' 
                        : ''}
                </div>
                <div class="text-sm font-bold text-${questInfo.color}-400">
                    ${isCompleted ? '✅ Completed' : 'Start →'}
                </div>
            </div>
        </div>
    `;
}
```

---

### 5. Filter Quests by Type

Add filtering functionality:

```javascript
function filterQuestsByType(type) {
    const filteredTasks = window.tasksData.filter(task => {
        const questInfo = getQuestTypeInfo(task);
        return type === 'all' || questInfo.type === type;
    });
    
    renderQuestList(filteredTasks);
}

// Filter buttons
function renderFilterButtons() {
    return `
        <div class="flex gap-2 overflow-x-auto pb-2 mb-4">
            <button onclick="filterQuestsByType('all')" class="filter-btn active">
                🎯 All
            </button>
            <button onclick="filterQuestsByType('telegram')" class="filter-btn">
                📱 Telegram
            </button>
            <button onclick="filterQuestsByType('twitter')" class="filter-btn">
                🐦 Twitter
            </button>
            <button onclick="filterQuestsByType('youtube')" class="filter-btn">
                🎥 YouTube
            </button>
            <button onclick="filterQuestsByType('social_media')" class="filter-btn">
                💬 Social
            </button>
            <button onclick="filterQuestsByType('website')" class="filter-btn">
                🌐 Website
            </button>
        </div>
    `;
}
```

---

## 📄 Updated HTML Structure

### Quest Modal

```html
<div id="taskModal" class="fixed inset-0 bg-black/90 z-50 hidden flex items-center justify-center p-4">
    <div class="bg-gray-900 border-2 border-blue-500/50 rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        
        <!-- Header -->
        <div class="p-6 border-b border-gray-800">
            <div class="flex items-start justify-between mb-4">
                <div class="flex items-center gap-3">
                    <div class="text-4xl" id="modalEmoji">🎯</div>
                    <div>
                        <h2 class="text-2xl font-bold gaming-title" id="modalTitle">Quest Title</h2>
                        <p class="text-sm text-gray-400" id="modalPlatform">PLATFORM</p>
                    </div>
                </div>
                <button onclick="closeTaskModal()" class="text-gray-400 hover:text-white">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <div class="flex items-center gap-3">
                <div class="text-brand-gold font-bold text-xl" id="modalPoints">+0 XP</div>
                <div id="verificationBadge" class="inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
                    ⚡ Instant Verification
                </div>
            </div>
        </div>
        
        <!-- Body -->
        <div class="p-6">
            <p class="text-gray-300 mb-6" id="modalDescription">Quest description</p>
            
            <!-- Code Input Section (for YouTube quests) -->
            <div id="codeInputSection" class="hidden mb-6">
                <label class="block text-sm font-bold mb-2">Verification Code</label>
                <input type="text" id="verificationCode" 
                       placeholder="Enter code from video"
                       class="w-full px-4 py-3 bg-gray-800 border-2 border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none">
                <p id="codeHint" class="text-xs text-gray-500 mt-1 hidden">Hint: Look in the video description</p>
            </div>
            
            <!-- Complete Button -->
            <button id="completeTaskBtn" onclick="completeTask()" 
                    class="w-full py-4 px-6 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-all">
                Complete Quest
            </button>
        </div>
    </div>
</div>
```

---

## 🎨 Updated Styling

Add quest-type specific colors:

```css
/* Quest type colors */
.quest-telegram { border-color: rgb(59 130 246 / 0.3); }
.quest-twitter { border-color: rgb(14 165 233 / 0.3); }
.quest-youtube { border-color: rgb(239 68 68 / 0.3); }
.quest-social { border-color: rgb(168 85 247 / 0.3); }
.quest-website { border-color: rgb(34 197 94 / 0.3); }

/* Filter buttons */
.filter-btn {
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    background: rgba(55, 65, 81, 0.3);
    color: rgb(156, 163, 175);
    font-weight: 600;
    transition: all 0.3s;
    white-space: nowrap;
}

.filter-btn.active {
    background: rgba(59, 130, 246, 0.2);
    color: rgb(96, 165, 250);
    border: 1px solid rgba(59, 130, 246, 0.5);
}

.filter-btn:hover {
    background: rgba(75, 85, 99, 0.5);
    color: white;
}
```

---

## ✅ Summary

### Frontend Changes

1. ✅ **Quest Type Detection** - `getQuestTypeInfo()` function
2. ✅ **Quest Display** - Updated `showTaskDetail()` with type-specific UI
3. ✅ **Quest Completion** - Separate handlers for each type
4. ✅ **Quest Cards** - Type badges and color coding
5. ✅ **Quest Filtering** - Filter by platform/type
6. ✅ **Timer Support** - Countdown for website quests
7. ✅ **Code Input** - YouTube code verification

### Benefits

- ✅ Clear visual distinction between quest types
- ✅ Appropriate UI for each verification method
- ✅ Better user experience with instant feedback
- ✅ Support for all 5 quest handler types
- ✅ Filtering and organization
- ✅ Responsive and mobile-friendly

---

## 🚀 Next Steps

1. Update `index.html` with new JavaScript functions
2. Test each quest type completion flow
3. Verify API endpoints match backend handlers
4. Update admin panel for quest creation
5. Deploy and test on production

---

**Status:** ✅ Web app update guide complete!
