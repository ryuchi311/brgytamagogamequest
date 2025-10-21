"""
Social Media Quest Handler
Handles Discord, Instagram, TikTok, and other social media platform quests
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class SocialMediaQuestHandler:
    """
    Handler for general social media platform quests
    
    Configuration:
    - Supports Discord, Instagram, TikTok, Facebook, LinkedIn, etc.
    - Manual verification by admin
    - Flexible for any social media platform
    """
    
    # ==================== CONFIGURATION ====================
    
    # Quest detection settings
    PLATFORM = 'social_media'
    TASK_TYPE = 'social'
    
    # Verification settings
    VERIFICATION_REQUIRED = True
    VERIFICATION_METHOD = 'social_media_action'
    
    # Supported social media platforms
    SUPPORTED_PLATFORMS = [
        'discord', 'instagram', 'tiktok', 'facebook', 
        'linkedin', 'reddit', 'twitch', 'medium',
        'github', 'gitlab', 'steam', 'spotify'
    ]
    
    # Platform emojis
    PLATFORM_EMOJIS = {
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
    }
    
    # ==================== INITIALIZATION ====================
    
    def __init__(self, bot_application, api_client):
        """
        Initialize Social Media quest handler
        
        Args:
            bot_application: Telegram bot application instance
            api_client: API client for database operations
        """
        self.bot = bot_application
        self.api_client = api_client
        logger.info("✅ SocialMediaQuestHandler initialized")
    
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
        verification_method = task.get('verification_data', {}).get('method', '')
        
        return (
            platform in SocialMediaQuestHandler.SUPPORTED_PLATFORMS or
            verification_method == SocialMediaQuestHandler.VERIFICATION_METHOD
        )
    
    # ==================== DISPLAY ====================
    
    async def show_quest(self, query, task: dict):
        """
        Display social media quest to user
        
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
        description = task.get('description', 'Complete social media action')
        points = task['points_reward']
        is_bonus = task.get('is_bonus', False)
        url = task.get('url', '')
        platform = task.get('platform', 'social_media')
        
        # Extract verification data
        verification_data = task.get('verification_data', {})
        action_description = verification_data.get('action_description', 'Complete the action')
        
        # Get platform emoji
        emoji = self.PLATFORM_EMOJIS.get(platform.lower(), '🌐')
        
        # Build message
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        message = f"""{bonus_tag}{emoji} *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

📱 **Platform:** {platform.title()}

🔔 **How to Complete:**
1. Click "Open {platform.title()}" button below
2. {action_description}
3. Return here and click "Submit Verification"
4. Admin will verify and award XP 🎁

⏳ *Verification may take a few minutes*
"""
        
        # Build keyboard
        keyboard = []
        
        # Add platform button
        if url:
            keyboard.append([InlineKeyboardButton(f"{emoji} Open {platform.title()}", url=url)])
        
        # Add submit button
        keyboard.append([InlineKeyboardButton("✅ Submit Verification", callback_data=f"submit_social_{task['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back to Quests", callback_data="view_tasks")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"{emoji} Displayed {platform} quest {task['id']} to user {user.id}")
    
    # ==================== SUBMISSION ====================
    
    async def handle_submission(self, query, task_id: str):
        """
        Handle social media verification submission
        
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
        
        platform = task.get('platform', 'social_media')
        emoji = self.PLATFORM_EMOJIS.get(platform.lower(), '🌐')
        
        # Submit verification request
        result = self.api_client.submit_verification(
            user_id=db_user['id'],
            task_id=task_id,
            verification_data={
                'platform': platform,
                'telegram_id': user.id,
                'telegram_username': user.username or '',
                'user_profile': db_user
            }
        )
        
        if result and 'error' not in result:
            message = f"""✅ *Verification Submitted!*

Your {platform.title()} quest verification has been submitted.

**Status:** ⏳ Pending Review

An admin will verify your action and award {task['points_reward']} XP soon.

You'll receive a notification when verified! 🔔

Continue with other quests while waiting! 🚀
"""
            
            keyboard = [[InlineKeyboardButton("✨ View More Quests", callback_data="view_tasks")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"📨 {platform} verification submitted for user {user.id}, task {task_id}")
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
    
    # ==================== ADMIN VERIFICATION ====================
    
    async def notify_verification_result(self, user_telegram_id: int, task: dict, approved: bool):
        """
        Notify user about verification result
        
        Args:
            user_telegram_id: Telegram ID of the user
            task: Task data
            approved: Whether verification was approved
        """
        platform = task.get('platform', 'social_media')
        emoji = self.PLATFORM_EMOJIS.get(platform.lower(), '🌐')
        
        try:
            if approved:
                message = f"""✅ *Quest Verified!*

🎉 Your {platform.title()} quest has been verified!

**Quest:** {task['title']}
**Reward:** +{task['points_reward']} XP

Keep up the great work! 🚀
"""
            else:
                message = f"""❌ *Verification Failed*

Your {platform.title()} quest verification was not approved.

**Quest:** {task['title']}

**Possible reasons:**
• Action not completed
• Wrong account/profile
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
            
            logger.info(f"📨 Sent {platform} verification result to user {user_telegram_id}: {'Approved' if approved else 'Rejected'}")
        except Exception as e:
            logger.error(f"Failed to send verification result: {e}")
    
    # ==================== HELPER METHODS ====================
    
    @staticmethod
    def get_platform_info(platform: str) -> dict:
        """
        Get platform information
        
        Args:
            platform: Platform name
            
        Returns:
            dict: Platform information
        """
        platform_info = {
            'discord': {
                'name': 'Discord',
                'emoji': '💬',
                'typical_actions': ['Join server', 'React to message', 'Send message in channel']
            },
            'instagram': {
                'name': 'Instagram',
                'emoji': '📸',
                'typical_actions': ['Follow account', 'Like post', 'Comment on post', 'Share story']
            },
            'tiktok': {
                'name': 'TikTok',
                'emoji': '🎵',
                'typical_actions': ['Follow account', 'Like video', 'Comment', 'Share video']
            },
            'facebook': {
                'name': 'Facebook',
                'emoji': '👥',
                'typical_actions': ['Like page', 'Share post', 'Join group']
            },
            'linkedin': {
                'name': 'LinkedIn',
                'emoji': '💼',
                'typical_actions': ['Follow company', 'Connect', 'Endorse skill']
            },
            'reddit': {
                'name': 'Reddit',
                'emoji': '🤖',
                'typical_actions': ['Join subreddit', 'Upvote post', 'Comment']
            },
            'github': {
                'name': 'GitHub',
                'emoji': '💻',
                'typical_actions': ['Star repository', 'Fork repo', 'Follow account']
            }
        }
        
        return platform_info.get(platform.lower(), {
            'name': platform.title(),
            'emoji': '🌐',
            'typical_actions': ['Complete the specified action']
        })
    
    # ==================== CONFIGURATION GUIDE ====================
    
    @staticmethod
    def get_config_guide() -> str:
        """
        Get configuration guide for admins
        
        Returns:
            str: Configuration guide
        """
        return """
🌐 SOCIAL MEDIA QUEST CONFIGURATION GUIDE

When creating a social media quest in admin panel:

Required Fields:
  • Title: Name of the quest
  • Description: What users should do
  • Points: Reward amount
  • Platform: discord|instagram|tiktok|facebook|linkedin|reddit|etc
  • URL: Direct link to profile/server/group
  
Verification Data (JSON):
  {
    "method": "social_media_action",
    "action_description": "Join our Discord server",
    "verification_instructions": "Check member list"
  }

Examples:

1. DISCORD Quest:
   Title: "Join Our Discord"
   Platform: discord
   URL: https://discord.gg/yourinvite
   Verification Data:
   {
     "method": "social_media_action",
     "action_description": "Join the Discord server and introduce yourself"
   }

2. INSTAGRAM Quest:
   Title: "Follow on Instagram"
   Platform: instagram
   URL: https://instagram.com/youraccount
   Verification Data:
   {
     "method": "social_media_action",
     "action_description": "Follow our Instagram account"
   }

3. GITHUB Quest:
   Title: "Star Our Repository"
   Platform: github
   URL: https://github.com/user/repo
   Verification Data:
   {
     "method": "social_media_action",
     "action_description": "Star the GitHub repository"
   }

Supported Platforms:
  ✅ Discord (server join, roles)
  ✅ Instagram (follow, like, comment)
  ✅ TikTok (follow, like, share)
  ✅ Facebook (like page, join group)
  ✅ LinkedIn (follow, connect)
  ✅ Reddit (join subreddit, upvote)
  ✅ GitHub (star, fork, follow)
  ✅ And many more!

Important Notes:
  ⚠️ Verification is MANUAL - admin must approve
  ⚠️ Provide clear instructions in description
  ✅ Flexible for any social media platform
  📧 Users get notified of verification result
"""
