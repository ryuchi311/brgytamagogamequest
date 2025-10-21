"""
Twitter Quest Handler
Handles Twitter follow/like/retweet verification
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class TwitterQuestHandler:
    """
    Handler for Twitter quests (follow, like, retweet)
    
    Configuration:
    - Supports follow, like, and retweet actions
    - Manual verification by admin
    - User submits Twitter username for verification
    """
    
    # ==================== CONFIGURATION ====================
    
    # Quest detection settings
    PLATFORM = 'twitter'
    TASK_TYPE = 'social'
    
    # Verification settings
    VERIFICATION_REQUIRED = True
    VERIFICATION_METHOD = 'twitter_action'
    
    # Supported Twitter actions
    SUPPORTED_ACTIONS = ['follow', 'like', 'retweet', 'tweet']
    
    # ==================== INITIALIZATION ====================
    
    def __init__(self, bot_application, api_client):
        """
        Initialize Twitter quest handler
        
        Args:
            bot_application: Telegram bot application instance
            api_client: API client for database operations
        """
        self.bot = bot_application
        self.api_client = api_client
        logger.info("✅ TwitterQuestHandler initialized")
    
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
        return (
            task.get('platform') == TwitterQuestHandler.PLATFORM and
            task.get('verification_data', {}).get('method') == TwitterQuestHandler.VERIFICATION_METHOD
        )
    
    # ==================== DISPLAY ====================
    
    async def show_quest(self, query, task: dict):
        """
        Display Twitter quest to user
        
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
        description = task.get('description', 'Complete Twitter action')
        points = task['points_reward']
        is_bonus = task.get('is_bonus', False)
        url = task.get('url', '')
        
        # Extract verification data
        verification_data = task.get('verification_data', {})
        action_type = verification_data.get('action_type', 'follow')
        target_username = verification_data.get('target_username', '')
        
        # Get action emoji and text
        action_info = self._get_action_info(action_type)
        
        # Build message
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        message = f"""{bonus_tag}🐦 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

{action_info['emoji']} **Action Required:**
{action_info['description']}

🔔 **How to Complete:**
1. Click "{action_info['button']}" button below
2. Complete the action on Twitter
3. Return here and click "Submit Verification"
4. Admin will verify and award XP 🎁

⏳ *Verification may take a few minutes*
"""
        
        # Build keyboard
        keyboard = []
        
        # Add action button
        if url:
            keyboard.append([InlineKeyboardButton(f"{action_info['emoji']} {action_info['button']}", url=url)])
        
        # Add submit button
        keyboard.append([InlineKeyboardButton("✅ Submit Verification", callback_data=f"submit_twitter_{task['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back to Quests", callback_data="view_tasks")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"🐦 Displayed Twitter quest {task['id']} to user {user.id}")
    
    # ==================== SUBMISSION ====================
    
    async def handle_submission(self, query, task_id: str):
        """
        Handle Twitter verification submission
        
        Args:
            query: Telegram callback query
            task_id: ID of the task to verify
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
        
        # Get verification data
        verification_data = task.get('verification_data', {})
        action_type = verification_data.get('action_type', 'follow')
        
        # Submit verification request
        result = self.api_client.submit_verification(
            user_id=db_user['id'],
            task_id=task_id,
            verification_data={
                'platform': 'twitter',
                'action_type': action_type,
                'twitter_username': db_user.get('twitter_username', ''),
                'telegram_id': user.id,
                'telegram_username': user.username or ''
            }
        )
        
        if result and 'error' not in result:
            action_info = self._get_action_info(action_type)
            
            message = f"""✅ *Verification Submitted!*

Your Twitter {action_type} verification has been submitted.

**Status:** ⏳ Pending Review

An admin will verify your action and award {task['points_reward']} XP soon.

You'll receive a notification when verified! 🔔

**What was submitted:**
• Action: {action_info['description']}
• Your Twitter: @{db_user.get('twitter_username', 'Not set')}

Continue with other quests while waiting! 🚀
"""
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"📨 Twitter verification submitted for user {user.id}, task {task_id}")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Server error'
            
            if 'already submitted' in error_msg.lower():
                message = "ℹ️ *Already Submitted*\n\nYou've already submitted this quest for verification!"
            elif 'already completed' in error_msg.lower():
                message = "ℹ️ *Already Completed*\n\nYou've already completed this quest!"
            else:
                message = f"❌ *Error*\n\n{error_msg}"
            
            keyboard = [[InlineKeyboardButton("« Back", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    # ==================== HELPER METHODS ====================
    
    def _get_action_info(self, action_type: str) -> dict:
        """
        Get action information based on action type
        
        Args:
            action_type: Type of Twitter action
            
        Returns:
            dict: Action information (emoji, description, button)
        """
        action_map = {
            'follow': {
                'emoji': '👤',
                'description': 'Follow the Twitter account',
                'button': 'Follow on Twitter'
            },
            'like': {
                'emoji': '❤️',
                'description': 'Like the tweet',
                'button': 'Like Tweet'
            },
            'retweet': {
                'emoji': '🔄',
                'description': 'Retweet the tweet',
                'button': 'Retweet'
            },
            'tweet': {
                'emoji': '✍️',
                'description': 'Post a tweet',
                'button': 'Tweet Now'
            }
        }
        
        return action_map.get(action_type, {
            'emoji': '🐦',
            'description': 'Complete Twitter action',
            'button': 'Open Twitter'
        })
    
    # ==================== ADMIN VERIFICATION ====================
    
    async def notify_verification_result(self, user_telegram_id: int, task: dict, approved: bool):
        """
        Notify user about verification result
        
        Args:
            user_telegram_id: Telegram ID of the user
            task: Task data
            approved: Whether verification was approved
        """
        try:
            if approved:
                message = f"""✅ *Quest Verified!*

🎉 Your Twitter quest has been verified!

**Quest:** {task['title']}
**Reward:** +{task['points_reward']} XP

Keep up the great work! 🚀
"""
            else:
                message = f"""❌ *Verification Failed*

Your Twitter quest verification was not approved.

**Quest:** {task['title']}

**Possible reasons:**
• Action not completed
• Wrong Twitter account
• Action was undone

Please try again or contact support.
"""
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.bot.bot.send_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"📨 Sent verification result to user {user_telegram_id}: {'Approved' if approved else 'Rejected'}")
        except Exception as e:
            logger.error(f"Failed to send verification result: {e}")
    
    # ==================== CONFIGURATION GUIDE ====================
    
    @staticmethod
    def get_config_guide() -> str:
        """
        Get configuration guide for admins
        
        Returns:
            str: Configuration guide
        """
        return """
🐦 TWITTER QUEST CONFIGURATION GUIDE

When creating a Twitter quest in admin panel:

Required Fields:
  • Title: Name of the quest
  • Description: What users should do
  • Points: Reward amount
  • Platform: twitter
  • URL: Direct link to Twitter profile/tweet
  
Verification Data (JSON):
  {
    "method": "twitter_action",
    "action_type": "follow|like|retweet|tweet",
    "target_username": "youraccount",
    "tweet_id": "1234567890"  (for like/retweet only)
  }

Examples:

1. FOLLOW Quest:
   Title: "Follow Us on Twitter"
   Platform: twitter
   URL: https://twitter.com/youraccount
   Verification Data: 
   {
     "method": "twitter_action",
     "action_type": "follow",
     "target_username": "youraccount"
   }

2. LIKE Quest:
   Title: "Like Our Tweet"
   Platform: twitter
   URL: https://twitter.com/youraccount/status/1234567890
   Verification Data:
   {
     "method": "twitter_action",
     "action_type": "like",
     "tweet_id": "1234567890"
   }

3. RETWEET Quest:
   Title: "Retweet Our Announcement"
   Platform: twitter
   URL: https://twitter.com/youraccount/status/1234567890
   Verification Data:
   {
     "method": "twitter_action",
     "action_type": "retweet",
     "tweet_id": "1234567890"
   }

Important Notes:
  ⚠️ Verification is MANUAL - admin must approve
  ⚠️ Users must have Twitter username set in profile
  ✅ Supports follow, like, retweet, tweet actions
  📧 Users get notified of verification result
"""
