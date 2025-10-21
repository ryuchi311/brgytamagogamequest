// ==================== QUEST HANDLER INTEGRATION ====================
// Add this to your index.html <script> section
// This integrates with the new modular quest handlers

/**
 * Get quest type information based on platform and verification method
 * Supports all 5 quest handler types: Telegram, Twitter, YouTube, Social Media, Website
 */
function getQuestTypeInfo(task) {
    const platform = task.platform?.toLowerCase() || '';
    const verificationData = task.verification_data || {};
    const method = verificationData.method || '';
    
    // ==================== TELEGRAM QUEST ====================
    if (platform === 'telegram' && method === 'telegram_membership') {
        return {
            type: 'telegram',
            handler: 'TelegramQuestHandler',
            emoji: '📱',
            color: 'blue',
            colorHex: '#3b82f6',
            buttonText: 'Join & Verify',
            needsCode: false,
            instant: true,
            verificationMethod: 'Automatic membership check'
        };
    }
    
    // ==================== TWITTER QUEST ====================
    if (platform === 'twitter' && method === 'twitter_action') {
        const actionType = verificationData.action_type || 'follow';
        const actionEmojis = {
            'follow': '👤',
            'like': '❤️',
            'retweet': '🔄',
            'tweet': '✍️'
        };
        
        return {
            type: 'twitter',
            handler: 'TwitterQuestHandler',
            emoji: '🐦',
            color: 'sky',
            colorHex: '#0ea5e9',
            buttonText: `${actionType.charAt(0).toUpperCase() + actionType.slice(1)} & Submit`,
            needsCode: false,
            instant: false,
            actionType: actionType,
            actionEmoji: actionEmojis[actionType] || '🐦',
            verificationMethod: 'Manual admin review'
        };
    }
    
    // ==================== YOUTUBE QUEST ====================
    if (platform === 'youtube' && method === 'youtube_code') {
        return {
            type: 'youtube',
            handler: 'YouTubeQuestHandler',
            emoji: '🎥',
            color: 'red',
            colorHex: '#ef4444',
            buttonText: 'Watch & Enter Code',
            needsCode: true,
            instant: true,
            hint: verificationData.hint || 'Find the code in the video',
            caseSensitive: verificationData.case_sensitive !== false,
            verificationMethod: 'Instant code verification'
        };
    }
    
    // ==================== SOCIAL MEDIA QUEST ====================
    if (method === 'social_media_action' || 
        ['discord', 'instagram', 'tiktok', 'facebook', 'linkedin', 'reddit', 
         'twitch', 'medium', 'github', 'gitlab', 'steam', 'spotify'].includes(platform)) {
        
        const platformEmojis = {
            'discord': '💬',
            'instagram': '📸',
            'tiktok': '🎵',
            'facebook': '👥',
            'linkedin': '💼',
            'reddit': '🤖',
            'twitch': '🎮',
            'medium': '✍️',
            'github': '💻',
            'gitlab': '🦊',
            'steam': '🎮',
            'spotify': '🎧'
        };
        
        return {
            type: 'social_media',
            handler: 'SocialMediaQuestHandler',
            emoji: platformEmojis[platform] || '🌐',
            color: 'purple',
            colorHex: '#a855f7',
            buttonText: 'Complete & Submit',
            needsCode: false,
            instant: false,
            platform: platform,
            actionDescription: verificationData.action_description || 'Complete the action',
            verificationMethod: 'Manual admin review'
        };
    }
    
    // ==================== WEBSITE QUEST ====================
    if (platform === 'website' || ['auto_complete', 'timer_based', 'manual'].includes(method)) {
        let buttonText = 'Visit & Claim';
        let instant = true;
        let subType = 'auto';
        
        if (method === 'timer_based') {
            const timer = verificationData.timer_seconds || 30;
            buttonText = `Visit (${timer}s timer)`;
            instant = false;
            subType = 'timer';
        } else if (method === 'manual') {
            buttonText = 'Complete & Submit';
            instant = false;
            subType = 'manual';
        }
        
        return {
            type: 'website',
            handler: 'WebsiteLinkQuestHandler',
            emoji: '🌐',
            color: 'green',
            colorHex: '#22c55e',
            buttonText: buttonText,
            needsCode: false,
            instant: instant,
            method: method || 'auto_complete',
            subType: subType,
            timer: verificationData.timer_seconds || 30,
            verificationMethod: instant ? 'Instant auto-complete' : 
                              (subType === 'timer' ? 'Timer-based' : 'Manual review')
        };
    }
    
    // ==================== FALLBACK ====================
    return {
        type: 'general',
        handler: 'UnknownHandler',
        emoji: '🎯',
        color: 'gray',
        colorHex: '#6b7280',
        buttonText: 'Complete Quest',
        needsCode: false,
        instant: false,
        verificationMethod: 'Unknown'
    };
}

/**
 * Render a quest card with proper styling and badges
 */
function renderQuestCard(task, index) {
    const questInfo = getQuestTypeInfo(task);
    const isCompleted = task.completed || false;
    const isBonus = task.is_bonus || false;
    
    return `
        <div class="quest-card bg-gray-900/60 border-2 border-${questInfo.color}-500/30 rounded-xl p-4 
                    hover:border-${questInfo.color}-500 hover:shadow-lg hover:shadow-${questInfo.color}-500/20 
                    transition-all cursor-pointer ${isCompleted ? 'opacity-60' : ''}"
             onclick="${isCompleted ? '' : `showTaskDetail(${index})`}">
            
            <!-- Header -->
            <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3">
                    <div class="text-3xl">${questInfo.emoji}</div>
                    <div>
                        <h3 class="font-bold text-white text-lg">${task.title}</h3>
                        <p class="text-xs text-${questInfo.color}-400 font-semibold">
                            ${task.platform.toUpperCase()} ${isBonus ? '🌟' : ''}
                        </p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-brand-gold font-bold text-xl">+${task.points_reward}</div>
                    <div class="text-xs text-brand-gold/70">XP</div>
                </div>
            </div>
            
            <!-- Description -->
            <p class="text-sm text-gray-400 mb-3 line-clamp-2">
                ${task.description || 'Complete this quest to earn points!'}
            </p>
            
            <!-- Badges -->
            <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex gap-2 flex-wrap">
                    ${questInfo.instant 
                        ? '<span class="text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded-full font-semibold">⚡ Instant</span>'
                        : '<span class="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded-full font-semibold">⏳ Review</span>'}
                    
                    ${questInfo.needsCode 
                        ? '<span class="text-xs px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full font-semibold">🔑 Code</span>' 
                        : ''}
                    
                    ${isBonus 
                        ? '<span class="text-xs px-2 py-1 bg-yellow-500/20 text-yellow-300 rounded-full font-semibold">🌟 Bonus</span>' 
                        : ''}
                    
                    ${questInfo.subType === 'timer' 
                        ? `<span class="text-xs px-2 py-1 bg-purple-500/20 text-purple-400 rounded-full font-semibold">⏱️ ${questInfo.timer}s</span>` 
                        : ''}
                </div>
                
                <div class="text-sm font-bold text-${questInfo.color}-400">
                    ${isCompleted ? '✅ Done' : 'Start →'}
                </div>
            </div>
        </div>
    `;
}

/**
 * Show quest detail modal with type-specific UI
 */
function showTaskDetail(taskIndex) {
    const task = window.tasksData[taskIndex];
    if (!task) return;
    
    const questInfo = getQuestTypeInfo(task);
    
    // Store current task
    window.currentTask = task;
    window.currentTaskId = task.id;
    window.currentTaskUrl = task.url;
    window.currentQuestInfo = questInfo;
    
    // Update modal content
    document.getElementById('modalTitle').textContent = task.title;
    document.getElementById('modalDescription').textContent = task.description || 'Complete this quest to earn points!';
    document.getElementById('modalEmoji').textContent = questInfo.emoji;
    document.getElementById('modalPlatform').textContent = task.platform.toUpperCase();
    document.getElementById('modalPoints').textContent = `+${task.points_reward} XP`;
    
    // Update handler info
    const handlerInfo = document.getElementById('modalHandlerInfo');
    if (handlerInfo) {
        handlerInfo.innerHTML = `
            <div class="text-xs text-gray-500">
                <span class="font-semibold">Handler:</span> ${questInfo.handler}<br>
                <span class="font-semibold">Method:</span> ${questInfo.verificationMethod}
            </div>
        `;
    }
    
    // Update button with dynamic color
    const completeBtn = document.getElementById('completeTaskBtn');
    completeBtn.textContent = questInfo.buttonText;
    completeBtn.className = `w-full py-4 px-6 bg-${questInfo.color}-600 hover:bg-${questInfo.color}-700 
                            text-white font-bold rounded-lg transition-all transform hover:scale-105`;
    
    // Show/hide code input for YouTube quests
    const codeSection = document.getElementById('codeInputSection');
    const codeInput = document.getElementById('verificationCode');
    const codeHint = document.getElementById('codeHint');
    
    if (questInfo.needsCode) {
        codeSection.classList.remove('hidden');
        codeInput.value = '';
        codeInput.placeholder = questInfo.caseSensitive 
            ? 'Enter code (case-sensitive)' 
            : 'Enter code (not case-sensitive)';
        
        if (questInfo.hint) {
            codeHint.textContent = `💡 Hint: ${questInfo.hint}`;
            codeHint.classList.remove('hidden');
        } else {
            codeHint.classList.add('hidden');
        }
    } else {
        codeSection.classList.add('hidden');
    }
    
    // Update verification badge
    const verificationBadge = document.getElementById('verificationBadge');
    if (questInfo.instant) {
        verificationBadge.textContent = '⚡ Instant Verification';
        verificationBadge.className = 'inline-block px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold';
    } else {
        verificationBadge.textContent = '⏳ Manual Verification';
        verificationBadge.className = 'inline-block px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm font-semibold';
    }
    
    // Show action-specific info
    const actionInfo = document.getElementById('modalActionInfo');
    if (actionInfo) {
        let infoHtml = '';
        
        if (questInfo.type === 'twitter') {
            infoHtml = `<div class="text-sm text-gray-400 mb-4">
                ${questInfo.actionEmoji} <strong>Action:</strong> ${questInfo.actionType.toUpperCase()}
            </div>`;
        } else if (questInfo.type === 'social_media') {
            infoHtml = `<div class="text-sm text-gray-400 mb-4">
                ${questInfo.emoji} <strong>Platform:</strong> ${questInfo.platform.toUpperCase()}<br>
                <strong>Action:</strong> ${questInfo.actionDescription}
            </div>`;
        } else if (questInfo.type === 'website' && questInfo.subType === 'timer') {
            infoHtml = `<div class="text-sm text-yellow-400 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
                ⏱️ <strong>Timer Quest:</strong> You must wait ${questInfo.timer} seconds after visiting the website before claiming XP.
            </div>`;
        }
        
        actionInfo.innerHTML = infoHtml;
    }
    
    // Show modal
    document.getElementById('taskModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    
    console.log('📋 Quest Detail:', {
        title: task.title,
        type: questInfo.type,
        handler: questInfo.handler,
        instant: questInfo.instant,
        needsCode: questInfo.needsCode
    });
}

/**
 * Close quest detail modal
 */
function closeTaskModal() {
    document.getElementById('taskModal').classList.add('hidden');
    document.body.style.overflow = '';
    
    // Clear stored data
    window.currentTask = null;
    window.currentTaskId = null;
    window.currentTaskUrl = null;
    window.currentQuestInfo = null;
    
    // Clear code input
    const codeInput = document.getElementById('verificationCode');
    if (codeInput) codeInput.value = '';
}

/**
 * Main quest completion router
 * Routes to the appropriate handler based on quest type
 */
async function completeTask() {
    if (!window.currentTaskId || !window.currentQuestInfo) {
        console.error('❌ No task selected');
        return;
    }
    
    const questType = window.currentQuestInfo.type;
    
    console.log('🎯 Starting quest completion:', {
        type: questType,
        handler: window.currentQuestInfo.handler,
        taskId: window.currentTaskId
    });
    
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
        console.error('❌ Quest completion error:', error);
        showAlert('❌ Error completing quest. Please try again.', 'error');
    }
}

// ==================== QUEST TYPE HANDLERS ====================

/**
 * Complete Telegram Quest
 * Handler: TelegramQuestHandler
 * Verification: Automatic membership check
 */
async function completeTelegramQuest() {
    console.log('📱 Telegram Quest - Opening channel...');
    
    // Open Telegram link
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    // Show loading
    showAlert('⏳ Please join the channel, then come back to verify...', 'info');
    
    // Wait for user to join
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Verify via Telegram bot (bot will check membership)
    // In production, this would trigger the TelegramQuestHandler on the bot
    console.log('📱 Verifying Telegram membership...');
    
    // For now, redirect to bot for verification
    // The bot's TelegramQuestHandler will handle the actual verification
    showAlert('✅ Please verify in the Telegram bot by clicking the "Verify Membership" button!', 'success');
    closeTaskModal();
}

/**
 * Complete Twitter Quest
 * Handler: TwitterQuestHandler
 * Verification: Manual admin review
 */
async function completeTwitterQuest() {
    console.log('🐦 Twitter Quest - Opening Twitter...');
    
    // Open Twitter link
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    // Show submission message
    showAlert(`⏳ Complete the ${window.currentQuestInfo.actionType} action on Twitter, then submit for verification in the bot!`, 'info');
    closeTaskModal();
}

/**
 * Complete YouTube Quest
 * Handler: YouTubeQuestHandler
 * Verification: Instant code check
 */
async function completeYouTubeQuest() {
    const codeInput = document.getElementById('verificationCode');
    const code = codeInput.value.trim();
    
    if (!code) {
        showAlert('⚠️ Please enter the verification code from the video!', 'warning');
        return;
    }
    
    console.log('🎥 YouTube Quest - Opening video...');
    
    // Open YouTube link
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    // Show verification message
    showAlert(`🔑 Code "${code}" submitted! Please verify in the Telegram bot.`, 'info');
    closeTaskModal();
}

/**
 * Complete Social Media Quest
 * Handler: SocialMediaQuestHandler
 * Verification: Manual admin review
 */
async function completeSocialMediaQuest() {
    console.log(`💬 Social Media Quest (${window.currentQuestInfo.platform}) - Opening link...`);
    
    // Open link
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    // Show submission message
    showAlert(`⏳ Complete the action on ${window.currentQuestInfo.platform.toUpperCase()}, then submit for verification in the bot!`, 'info');
    closeTaskModal();
}

/**
 * Complete Website Quest
 * Handler: WebsiteLinkQuestHandler
 * Verification: Auto/Timer/Manual based on method
 */
async function completeWebsiteQuest() {
    const method = window.currentQuestInfo.method;
    const subType = window.currentQuestInfo.subType;
    
    console.log(`🌐 Website Quest (${subType}) - Opening website...`);
    
    // Open website
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    if (subType === 'auto') {
        // Auto-complete mode - instant claim via bot
        showAlert('✅ Website opened! Please claim your XP in the Telegram bot.', 'success');
    } else if (subType === 'timer') {
        // Timer mode - user must wait
        showAlert(`⏱️ Website opened! Please wait ${window.currentQuestInfo.timer} seconds before claiming in the bot.`, 'info');
    } else {
        // Manual mode - admin verification
        showAlert('⏳ Complete the action on the website, then submit for verification in the bot!', 'info');
    }
    
    closeTaskModal();
}

/**
 * Complete General/Unknown Quest
 * Fallback handler
 */
async function completeGeneralQuest() {
    console.log('🎯 General Quest - Opening link...');
    
    if (window.currentTaskUrl) {
        window.open(window.currentTaskUrl, '_blank');
    }
    
    showAlert('✅ Link opened! Please complete in the Telegram bot.', 'info');
    closeTaskModal();
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    const colors = {
        success: 'bg-green-500/20 text-green-400 border-green-500',
        error: 'bg-red-500/20 text-red-400 border-red-500',
        warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
        info: 'bg-blue-500/20 text-blue-400 border-blue-500'
    };
    
    const color = colors[type] || colors.info;
    
    const alert = document.createElement('div');
    alert.className = `${color} border-2 rounded-lg p-4 mb-4 animate-fade-in`;
    alert.textContent = message;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

console.log('✅ Quest Handler Integration Loaded!');
console.log('📋 Supported Quest Types: Telegram, Twitter, YouTube, Social Media, Website');
