"""
Telegram Quest Handler
Handles Telegram group/channel membership verification
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class TelegramQuestHandler:
    """
    Handler for Telegram membership quests
    
    Configuration:
    - Automatically verifies Telegram group/channel membership
    - Awards points instantly if user is a member
    - Shows "Join" button if not a member
    """
    
    # ==================== CONFIGURATION ====================
    
    # Quest detection settings
    PLATFORM = 'telegram'
    TASK_TYPE = 'social'
    
    # Verification settings
    VERIFICATION_REQUIRED = True
    VERIFICATION_METHOD = 'telegram_membership'
    
    # Valid membership statuses
    VALID_MEMBER_STATUSES = ['member', 'administrator', 'creator']
    
    # ==================== INITIALIZATION ====================
    
    def __init__(self, bot_application, api_client):
        """
        Initialize Telegram quest handler
        
        Args:
            bot_application: Telegram bot application instance
            api_client: API client for database operations
        """
        self.bot = bot_application
        self.api_client = api_client
        logger.info("✅ TelegramQuestHandler initialized")
    
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
            task.get('platform') == TelegramQuestHandler.PLATFORM and
            task.get('verification_data', {}).get('method') == TelegramQuestHandler.VERIFICATION_METHOD
        )
    
    # ==================== DISPLAY ====================
    
    async def show_quest(self, query, task: dict):
        """
        Display Telegram quest to user
        
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
        description = task.get('description', 'Join our Telegram group/channel')
        points = task['points_reward']
        is_bonus = task.get('is_bonus', False)
        url = task.get('url', '')
        
        # Extract verification data
        verification_data = task.get('verification_data', {})
        channel_username = verification_data.get('channel_username', '')
        
        # Build message
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        
        message = f"""{bonus_tag}📱 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

🔔 **How to Complete:**
1. Click "Join Channel" button below
2. Join the Telegram group/channel
3. Click "Verify Membership" button
4. Get your XP instantly! 🎁

⚡ *Instant verification!*
"""
        
        # Build keyboard
        keyboard = []
        
        # Add join button if URL provided
        if url:
            keyboard.append([InlineKeyboardButton("📱 Join Channel/Group", url=url)])
        elif channel_username:
            keyboard.append([InlineKeyboardButton("📱 Join Channel/Group", url=f"https://t.me/{channel_username}")])
        
        # Add verify button
        keyboard.append([InlineKeyboardButton("✅ Verify Membership", callback_data=f"verify_telegram_{task['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back to Quests", callback_data="view_tasks")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"📱 Displayed Telegram quest {task['id']} to user {user.id}")
    
    # ==================== VERIFICATION ====================
    
    async def verify_membership(self, query, task_id: str):
        """
        Verify if user is a member of the Telegram group/channel
        
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
        
        # Get channel info
        verification_data = task.get('verification_data', {})
        channel_username = verification_data.get('channel_username', '')
        
        if not channel_username:
            await query.edit_message_text(
                "❌ Invalid quest configuration. Please contact an admin."
            )
            return
        
        try:
            # Check membership
            chat_member = await self.bot.bot.get_chat_member(
                chat_id=f"@{channel_username}",
                user_id=user.id
            )
            
            # Verify membership status
            is_member = chat_member.status in self.VALID_MEMBER_STATUSES
            
            if is_member:
                # User is a member - complete quest
                await self._handle_success(query, db_user, task)
            else:
                # Not a member yet
                await self._handle_not_member(query, task, channel_username)
                
        except Exception as e:
            logger.error(f"❌ Error verifying Telegram membership: {e}")
            await self._handle_error(query, task, str(e))
    
    async def _handle_success(self, query, user: dict, task: dict):
        """Handle successful verification"""
        # Complete the task
        result = self.api_client.complete_task(user['id'], task['id'])
        
        if result and 'error' not in result:
            message = f"""✅ *Quest Completed!*

🎉 You earned **{task['points_reward']} XP**!

Thank you for joining! 🚀

Continue completing quests to earn more XP!
"""
            
            # Create notification
            try:
                self.api_client.create_notification(
                    user['id'],
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
            
            logger.info(f"✅ User {user['telegram_id']} completed Telegram quest {task['id']}")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Server error'
            
            if 'already completed' in error_msg.lower():
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
    
    async def _handle_not_member(self, query, task: dict, channel_username: str):
        """Handle case where user is not a member yet"""
        url = task.get('url', f"https://t.me/{channel_username}")
        
        message = f"""❌ *Not Verified*

You are not a member of the channel/group yet.

**Steps:**
1. Click "Join Now" button below
2. Join the channel/group
3. Return here
4. Click "Verify Again"

Then you'll get your {task['points_reward']} XP! 🎁
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Join Now", url=url)],
            [InlineKeyboardButton("🔄 Verify Again", callback_data=f"verify_telegram_{task['id']}")],
            [InlineKeyboardButton("« Back", callback_data="view_tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _handle_error(self, query, task: dict, error: str):
        """Handle verification errors"""
        message = f"""❌ *Verification Failed*

Could not verify your membership.

**Possible reasons:**
• Bot is not an admin in the channel/group
• Channel/group username is incorrect
• Technical issue

Please contact an admin or try again later.

Error: {error[:100]}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Try Again", callback_data=f"verify_telegram_{task['id']}")],
            [InlineKeyboardButton("« Back", callback_data="view_tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.error(f"Telegram verification error for task {task['id']}: {error}")
    
    # ==================== CONFIGURATION GUIDE ====================
    
    @staticmethod
    def get_config_guide() -> str:
        """
        Get configuration guide for admins
        
        Returns:
            str: Configuration guide
        """
        return """
📱 TELEGRAM QUEST CONFIGURATION GUIDE

When creating a Telegram quest in admin panel:

Required Fields:
  • Title: Name of the quest
  • Description: What users should do
  • Points: Reward amount
  • Platform: telegram
  • URL: Telegram invite link (e.g., https://t.me/yourchannel)
  
Verification Data (JSON):
  {
    "method": "telegram_membership",
    "channel_username": "yourchannel"  (without @)
  }

Example:
  Title: "Join Our Telegram Channel"
  Description: "Join our official Telegram channel for updates"
  Points: 100
  Platform: telegram
  URL: https://t.me/mychannel
  Verification Data: {"method": "telegram_membership", "channel_username": "mychannel"}

Important Notes:
  ⚠️ Bot must be ADMIN in the channel/group!
  ⚠️ Channel username should NOT include @ symbol
  ⚠️ Public channels only (username required)
  ✅ Verification is automatic and instant
"""
