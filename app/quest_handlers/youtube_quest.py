"""
YouTube Quest Handler
Handles YouTube video watch + verification code quests
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class YouTubeQuestHandler:
    """
    Handler for YouTube video watch quests
    
    Configuration:
    - User watches YouTube video
    - Video contains a verification code
    - User submits the code to complete quest
    - Instant verification
    """
    
    # ==================== CONFIGURATION ====================
    
    # Quest detection settings
    PLATFORM = 'youtube'
    TASK_TYPE = 'social'
    
    # Verification settings
    VERIFICATION_REQUIRED = True
    VERIFICATION_METHOD = 'youtube_code'
    
    # Code validation
    MAX_CODE_LENGTH = 50
    MIN_CODE_LENGTH = 3
    
    # ==================== INITIALIZATION ====================
    
    def __init__(self, bot_application, api_client):
        """
        Initialize YouTube quest handler
        
        Args:
            bot_application: Telegram bot application instance
            api_client: API client for database operations
        """
        self.bot = bot_application
        self.api_client = api_client
        logger.info("✅ YouTubeQuestHandler initialized")
    
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
            task.get('platform') == YouTubeQuestHandler.PLATFORM and
            task.get('verification_data', {}).get('method') == YouTubeQuestHandler.VERIFICATION_METHOD
        )
    
    # ==================== DISPLAY ====================
    
    async def show_quest(self, query, task: dict):
        """
        Display YouTube quest to user
        
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
        description = task.get('description', 'Watch YouTube video and find the code')
        points = task['points_reward']
        is_bonus = task.get('is_bonus', False)
        url = task.get('url', '')
        
        # Extract verification data
        verification_data = task.get('verification_data', {})
        video_id = verification_data.get('video_id', '')
        hint = verification_data.get('hint', '')
        
        # Build message
        bonus_tag = "🌟 **BONUS QUEST**\n\n" if is_bonus else ""
        hint_text = f"\n💡 **Hint:** {hint}" if hint else ""
        
        message = f"""{bonus_tag}🎥 *{title}*

📝 **Description:**
{description}

💰 **Reward:** {points} XP

🔔 **How to Complete:**
1. Click "Watch Video" button below
2. Watch the video carefully
3. Find the verification code in the video
4. Return here and click "Submit Code"
5. Enter the code
6. Get your XP instantly! 🎁{hint_text}

⚡ *Instant verification!*
"""
        
        # Build keyboard
        keyboard = []
        
        # Add watch video button
        if url:
            keyboard.append([InlineKeyboardButton("🎥 Watch Video", url=url)])
        elif video_id:
            keyboard.append([InlineKeyboardButton("🎥 Watch Video", url=f"https://youtube.com/watch?v={video_id}")])
        
        # Add submit code button
        keyboard.append([InlineKeyboardButton("✅ Submit Code", callback_data=f"submit_youtube_{task['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("« Back to Quests", callback_data="view_tasks")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"🎥 Displayed YouTube quest {task['id']} to user {user.id}")
    
    # ==================== CODE SUBMISSION ====================
    
    async def prompt_code_submission(self, query, task_id: str):
        """
        Prompt user to enter verification code
        
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
        
        # Show code submission prompt
        message = f"""🔑 *Enter Verification Code*

Please type the verification code you found in the video.

**Quest:** {task['title']}
**Reward:** {task['points_reward']} XP

Type the code in the chat now.

⚠️ *Note:* Code is case-sensitive!
"""
        
        keyboard = [[InlineKeyboardButton("« Cancel", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Store pending verification
        # In a real implementation, you'd use a state manager or database
        # For now, we'll use callback data
        logger.info(f"🔑 Prompted code submission for user {user.id}, task {task_id}")
    
    # ==================== VERIFICATION ====================
    
    async def verify_code(self, message, task_id: str, submitted_code: str):
        """
        Verify the submitted code
        
        Args:
            message: Telegram message containing the code
            task_id: ID of the task
            submitted_code: Code submitted by user
        """
        user = message.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await message.reply_text("❌ Please use /start to register first.")
            return
        
        # Get task
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await message.reply_text("❌ Quest not found.")
            return
        
        # Get verification data
        verification_data = task.get('verification_data', {})
        correct_code = verification_data.get('verification_code', '')
        case_sensitive = verification_data.get('case_sensitive', True)
        
        # Validate code
        if not correct_code:
            await message.reply_text("❌ Quest configuration error. Please contact an admin.")
            return
        
        # Validate submitted code
        if not submitted_code or len(submitted_code) < self.MIN_CODE_LENGTH:
            await message.reply_text(f"❌ Code is too short. Minimum {self.MIN_CODE_LENGTH} characters.")
            return
        
        if len(submitted_code) > self.MAX_CODE_LENGTH:
            await message.reply_text(f"❌ Code is too long. Maximum {self.MAX_CODE_LENGTH} characters.")
            return
        
        # Compare codes
        if case_sensitive:
            is_correct = submitted_code == correct_code
        else:
            is_correct = submitted_code.lower() == correct_code.lower()
        
        if is_correct:
            # Code is correct - complete quest
            await self._handle_correct_code(message, db_user, task)
        else:
            # Code is incorrect
            await self._handle_incorrect_code(message, task, submitted_code)
    
    async def _handle_correct_code(self, message, user: dict, task: dict):
        """Handle correct code submission"""
        # Complete the task
        result = self.api_client.complete_task(user['id'], task['id'])
        
        if result and 'error' not in result:
            response = f"""✅ *Correct Code!*

🎉 Quest Completed!

You earned **{task['points_reward']} XP**!

Thank you for watching! 🚀

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
            
            await message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ User {user['telegram_id']} completed YouTube quest {task['id']}")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Server error'
            
            if 'already completed' in error_msg.lower():
                response = "ℹ️ *Already Completed*\n\nYou've already completed this quest!"
            else:
                response = f"❌ *Error*\n\n{error_msg}"
            
            await message.reply_text(response, parse_mode='Markdown')
    
    async def _handle_incorrect_code(self, message, task: dict, submitted_code: str):
        """Handle incorrect code submission"""
        verification_data = task.get('verification_data', {})
        attempts_allowed = verification_data.get('max_attempts', 3)
        
        response = f"""❌ *Incorrect Code*

The code '{submitted_code}' is not correct.

**Tips:**
• Make sure you watched the entire video
• Code might be at the beginning, middle, or end
• Check if code is case-sensitive
• Look carefully in video description or comments

Try again! You can submit as many times as needed.
"""
        
        keyboard = [
            [InlineKeyboardButton("🎥 Watch Again", url=task.get('url', ''))],
            [InlineKeyboardButton("🔄 Try Again", callback_data=f"submit_youtube_{task['id']}")],
            [InlineKeyboardButton("« Back", callback_data="view_tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        logger.info(f"❌ Incorrect code submitted for task {task['id']}: '{submitted_code}'")
    
    # ==================== CONFIGURATION GUIDE ====================
    
    @staticmethod
    def get_config_guide() -> str:
        """
        Get configuration guide for admins
        
        Returns:
            str: Configuration guide
        """
        return """
🎥 YOUTUBE QUEST CONFIGURATION GUIDE

When creating a YouTube quest in admin panel:

Required Fields:
  • Title: Name of the quest
  • Description: Instructions for users
  • Points: Reward amount
  • Platform: youtube
  • URL: Full YouTube video URL
  
Verification Data (JSON):
  {
    "method": "youtube_code",
    "video_id": "dQw4w9WgXcQ",
    "verification_code": "SECRET123",
    "case_sensitive": true,
    "max_attempts": 3,
    "hint": "Look in the description"  (optional)
  }

Example:
  Title: "Watch Our Tutorial"
  Description: "Watch the video and find the secret code"
  Points: 150
  Platform: youtube
  URL: https://youtube.com/watch?v=dQw4w9WgXcQ
  Verification Data:
  {
    "method": "youtube_code",
    "video_id": "dQw4w9WgXcQ",
    "verification_code": "QUEST2024",
    "case_sensitive": true,
    "hint": "Check the first 30 seconds"
  }

Code Placement Tips:
  1. Display code as text overlay in video
  2. Show code in video description
  3. Hide code in thumbnail/intro/outro
  4. Mention code verbally
  5. Show code in comments (pin it)

Important Notes:
  ⚠️ Code should be easy to read but not too obvious
  ⚠️ Default: case-sensitive (can disable)
  ✅ Verification is automatic and instant
  ✅ Unlimited attempts by default
  💡 Add hints to help users find the code
"""
