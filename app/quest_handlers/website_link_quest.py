"""
Website Link Quest Handler
Handles simple website visit quests with timer-based XP claiming
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time

logger = logging.getLogger(__name__)


class WebsiteLinkQuestHandler:
    """
    Handler for website link visit quests
    
    Configuration:
    - User visits website link
    - Timer counts down (optional)
    - User claims XP after visiting
    - No API authentication required for users
    - Can be auto-complete or manual verification
    """
    
    # ==================== CONFIGURATION ====================
    
    # Quest detection settings
    PLATFORM = 'website'
    TASK_TYPE = 'visit'
    
    # Verification settings
    VERIFICATION_REQUIRED = False  # Can be disabled for auto-complete
    VERIFICATION_METHODS = ['auto_complete', 'timer_based', 'manual']
    
    # Timer settings (seconds)
    DEFAULT_TIMER = 30
    MIN_TIMER = 5
    MAX_TIMER = 300
    
    # ==================== INITIALIZATION ====================
    
    def __init__(self, bot_application, api_client):
        """
        Initialize Website Link quest handler
        
        Args:
            bot_application: Telegram bot application instance
            api_client: API client for database operations
        """
        self.bot = bot_application
        self.api_client = api_client
        logger.info("✅ WebsiteLinkQuestHandler initialized")
    
    # ==================== DETECTION ====================
    
    @staticmethod
    def can_handle(task: dict) -> bool:
        """
        Check if this handler can process the task
        
        Args:
            task: Task dictionary from database
            
        Returns:
            bool: True if this handler can process the task
        """
        platform = task.get('platform', '').lower()
        task_type = task.get('task_type', '').lower()
        verification_method = task.get('verification_data', {}).get('method', '')
        
        return (
            platform == WebsiteLinkQuestHandler.PLATFORM or
            task_type == WebsiteLinkQuestHandler.TASK_TYPE or
            verification_method in WebsiteLinkQuestHandler.VERIFICATION_METHODS
        )
    
    # ==================== DISPLAY ====================
    
    async def show_quest(self, query, task: dict):
        """
        Display website link quest to user
        
        Args:
            query: Telegram callback query
            task: Task data from database
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Please use /start to register first.")
            return
        
        # Extract quest data
        title = task['title']
        description = task.get('description', 'Visit the website')
        points = task['points_reward']
        is_bonus = task.get('is_bonus', False)
        url = task.get('url', '')
        
        # Extract verification data
        verification_data = task.get('verification_data', {})
        method = verification_data.get('method', 'auto_complete')
        timer_seconds = verification_data.get('timer_seconds', self.DEFAULT_TIMER)
        
        # Build message based on verification method
        if method == 'auto_complete':
            message = self._build_auto_complete_message(title, description, points, url, is_bonus)
        elif method == 'timer_based':
            message = self._build_timer_message(title, description, points, url, timer_seconds, is_bonus)
        else:
            message = self._build_manual_message(title, description, points, url, is_bonus)
        
        # Build keyboard
        keyboard = self._build_keyboard(task, url, method)
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"🌐 Displayed website quest {task['id']} to user {user.id} (method: {method})")
    
    def _build_auto_complete_message(self, title: str, description: str, points: int, url: str, is_bonus: bool) -> str:
        """Build message for auto-complete mode"""
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        return f"""{bonus_tag}🌐 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

🔔 **How to Complete:**
1. Click "Visit Website" button below
2. Check out the website
3. Return here
4. Click "Claim XP" button
5. Get your {points} XP instantly! 🎁

⚡ *Auto-complete mode - No verification needed!*
"""
    
    def _build_timer_message(self, title: str, description: str, points: int, url: str, timer: int, is_bonus: bool) -> str:
        """Build message for timer-based mode"""
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        return f"""{bonus_tag}🌐 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

⏱️ **Timer:** {timer} seconds

🔔 **How to Complete:**
1. Click "Visit Website" button below
2. Explore the website for at least {timer} seconds
3. Return here after the timer expires
4. Click "Claim XP" button
5. Get your {points} XP! 🎁

⏳ *Timer starts when you click "Visit Website"*
"""
    
    def _build_manual_message(self, title: str, description: str, points: int, url: str, is_bonus: bool) -> str:
        """Build message for manual verification mode"""
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        return f"""{bonus_tag}🌐 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

🔔 **How to Complete:**
1. Click "Visit Website" button below
2. Complete the required action on the website
3. Return here and click "Submit Verification"
4. Admin will verify and award XP 🎁

⏳ *Manual verification by admin*
"""
    
    def _build_keyboard(self, task: dict, url: str, method: str) -> list:
        """Build inline keyboard based on verification method"""
        keyboard = []
        
        # Add visit website button
        if url:
            keyboard.append([InlineKeyboardButton("🌐 Visit Website", url=url)])
        
        # Add action button based on method
        if method == 'auto_complete':
            keyboard.append([InlineKeyboardButton("🎁 Claim XP", callback_data=f"claim_website_{task['id']}")])
        elif method == 'timer_based':
            keyboard.append([InlineKeyboardButton("⏱️ Start Timer & Visit", callback_data=f"start_timer_{task['id']}")])
        else:  # manual
            keyboard.append([InlineKeyboardButton("✅ Submit Verification", callback_data=f"submit_website_{task['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back to Quests", callback_data="view_tasks")])
        
        return keyboard
    
    # ==================== AUTO-COMPLETE MODE ====================
    
    async def handle_auto_claim(self, query, task_id: str):
        """
        Handle auto-complete XP claim
        
        Args:
            query: Telegram callback query
            task_id: ID of the task
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Please use /start to register first.")
            return
        
        # Get task
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("❌ Quest not found.")
            return
        
        # Complete the task
        result = self.api_client.complete_task(db_user['id'], task_id)
        
        if result and 'error' not in result:
            message = f"""✅ *XP Claimed!*

🎉 You earned **{task['points_reward']} XP**!

Thank you for visiting! 🚀

Continue completing quests to earn more XP!
"""
            
            # Create notification
            try:
                self.api_client.create_notification(
                    db_user['id'],
                    "Quest Completed!",
                    f"You earned {task['points_reward']} XP for completing '{task['title']}'",
                    "task_completed"
                )
            except Exception as e:
                logger.error(f"Failed to create notification: {e}")
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ User {user.id} completed website quest {task_id} (auto-claim)")
        else:
            await self._handle_claim_error(query, result)
    
    # ==================== TIMER MODE ====================
    
    async def handle_timer_start(self, query, task_id: str):
        """
        Handle timer start for timer-based quests
        
        Args:
            query: Telegram callback query
            task_id: ID of the task
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Please use /start to register first.")
            return
        
        # Get task
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("❌ Quest not found.")
            return
        
        # Get timer duration
        verification_data = task.get('verification_data', {})
        timer_seconds = verification_data.get('timer_seconds', self.DEFAULT_TIMER)
        
        # Store timer start time
        start_time = int(time.time())
        
        # In a real implementation, you'd store this in database
        # For now, we'll calculate the claim time
        claim_time = start_time + timer_seconds
        
        message = f"""⏱️ *Timer Started!*

**Quest:** {task['title']}
**Timer:** {timer_seconds} seconds

🌐 Please visit the website now.

You can claim your {task['points_reward']} XP after **{timer_seconds} seconds**.

Come back in {timer_seconds} seconds and click "Claim XP"! ⏰
"""
        
        keyboard = [
            [InlineKeyboardButton("🌐 Visit Website", url=task.get('url', ''))],
            [InlineKeyboardButton("🎁 Claim XP", callback_data=f"claim_timer_{task_id}_{claim_time}")],
            [InlineKeyboardButton("« Back", callback_data="view_tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"⏱️ Timer started for user {user.id}, task {task_id} ({timer_seconds}s)")
    
    async def handle_timer_claim(self, query, task_id: str, claim_time: int):
        """
        Handle XP claim after timer expires
        
        Args:
            query: Telegram callback query
            task_id: ID of the task
            claim_time: Unix timestamp when claim becomes available
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Please use /start to register first.")
            return
        
        # Check if timer has expired
        current_time = int(time.time())
        
        if current_time < claim_time:
            remaining = claim_time - current_time
            message = f"""⏳ *Timer Not Expired Yet*

Please wait **{remaining} seconds** more.

Come back when the timer is done! ⏰
"""
            
            await query.answer(message, show_alert=True)
            return
        
        # Timer expired - complete the task
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("❌ Quest not found.")
            return
        
        result = self.api_client.complete_task(db_user['id'], task_id)
        
        if result and 'error' not in result:
            message = f"""✅ *Timer Complete!*

🎉 You earned **{task['points_reward']} XP**!

Thank you for taking the time to visit! 🚀

Continue completing quests to earn more XP!
"""
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ User {user.id} completed website quest {task_id} (timer)")
        else:
            await self._handle_claim_error(query, result)
    
    # ==================== MANUAL VERIFICATION MODE ====================
    
    async def handle_manual_submission(self, query, task_id: str):
        """
        Handle manual verification submission
        
        Args:
            query: Telegram callback query
            task_id: ID of the task
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Please use /start to register first.")
            return
        
        # Get task
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("❌ Quest not found.")
            return
        
        # Submit verification request
        result = self.api_client.submit_verification(
            user_id=db_user['id'],
            task_id=task_id,
            verification_data={
                'platform': 'website',
                'url': task.get('url', ''),
                'telegram_id': user.id,
                'telegram_username': user.username or ''
            }
        )
        
        if result and 'error' not in result:
            message = f"""✅ *Verification Submitted!*

Your website visit verification has been submitted.

**Status:** ⏳ Pending Review

An admin will verify and award {task['points_reward']} XP soon.

You'll receive a notification when verified! 🔔
"""
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"📨 Website verification submitted for user {user.id}, task {task_id}")
        else:
            await self._handle_claim_error(query, result)
    
    # ==================== ERROR HANDLING ====================
    
    async def _handle_claim_error(self, query, result):
        """Handle claim/submission errors"""
        error_msg = result.get('error', 'Unknown error') if result else 'Server error'
        
        if 'already completed' in error_msg.lower():
            message = "ℹ️ *Already Completed*\n\nYou've already completed this quest!"
        elif 'already submitted' in error_msg.lower():
            message = "ℹ️ *Already Submitted*\n\nYou've already submitted this quest for verification!"
        else:
            message = f"❌ *Error*\n\n{error_msg}"
        
        keyboard = [[InlineKeyboardButton("« Back", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ==================== CONFIGURATION GUIDE ====================
    
    @staticmethod
    def get_config_guide() -> str:
        """
        Get configuration guide for admins
        
        Returns:
            str: Configuration guide
        """
        return """
🌐 WEBSITE LINK QUEST CONFIGURATION GUIDE

When creating a website link quest in admin panel:

Required Fields:
  • Title: Name of the quest
  • Description: What users should do
  • Points: Reward amount
  • Platform: website
  • URL: Full website URL to visit
  
Verification Data (JSON):
Choose ONE of three methods:

1. AUTO-COMPLETE (Instant, no verification):
   {
     "method": "auto_complete"
   }

2. TIMER-BASED (User must wait X seconds):
   {
     "method": "timer_based",
     "timer_seconds": 30
   }

3. MANUAL (Admin verification required):
   {
     "method": "manual",
     "verification_instructions": "Check analytics"
   }

Examples:

1. AUTO-COMPLETE Quest:
   Title: "Visit Our Website"
   Description: "Check out our homepage"
   Points: 50
   Platform: website
   URL: https://example.com
   Verification Data: {"method": "auto_complete"}
   
2. TIMER Quest:
   Title: "Explore Our Blog"
   Description: "Spend 1 minute reading our latest post"
   Points: 100
   Platform: website
   URL: https://example.com/blog
   Verification Data: {"method": "timer_based", "timer_seconds": 60}
   
3. MANUAL Quest:
   Title: "Sign Up on Website"
   Description: "Create an account on our platform"
   Points: 200
   Platform: website
   URL: https://example.com/signup
   Verification Data: {"method": "manual"}

Method Comparison:
  🟢 AUTO-COMPLETE: Instant, trust-based, high completion rate
  🟡 TIMER-BASED: Ensures minimum engagement time
  🔴 MANUAL: Most secure, requires admin work

Important Notes:
  ⚡ Auto-complete = No verification needed!
  ⏱️ Timer = Fair balance between speed and engagement
  ✅ Manual = Maximum control and verification
  🎯 Choose based on quest importance and trust level
"""
