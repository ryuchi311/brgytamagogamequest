"""
Simplified Telegram Bot - Notification Only
Pure notification bot for quest and reward announcements + basic verification
"""
import os
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from dotenv import load_dotenv
from app.bot_api_client import BotAPIClient

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.com")


class NotificationBot:
    """
    Simplified Telegram Bot - Notification Only
    
    Features:
    - User registration (/start)
    - Notifications about new quests
    - Notifications about new rewards
    - Basic bot verification (Telegram membership check)
    - Redirect users to web app for all interactions
    """
    
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.api_client = BotAPIClient()
        logger.info("✅ Notification Bot initialized")
    
    def setup_handlers(self):
        """Register minimal handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Callback handler for verification only
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("✅ Bot handlers registered")
    
    # ==================== COMMAND HANDLERS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Register user and show web app link"""
        user = update.effective_user
        
        # Get or create user in database
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            # Create new user
            user_data = {
                "telegram_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
            db_user = BotAPIClient.create_user(user_data)
            
            message = f"""🎉 **Welcome to Gaming Quest Hub!**

✅ You're registered, {user.first_name}!

🎮 **Start Your Journey:**
Visit our web app to view quests, earn XP, and claim rewards!

👇 Click the button below to get started:
"""
            logger.info(f"✅ New user registered: {user.id} ({user.username})")
        else:
            message = f"""👋 **Welcome back, {user.first_name}!**

💎 Current XP: **{db_user['points']} points**
🏆 Total Earned: **{db_user.get('total_earned_points', 0)} points**

🎮 **Continue Your Quest:**
Visit the web app to complete quests and earn more XP!

👇 Use the button below:
"""
            logger.info(f"✅ User returned: {user.id} ({user.username})")
        
        # Create inline keyboard with web app button
        keyboard = [
            [InlineKeyboardButton("🎮 Open Gaming Quest Hub", url=f"{WEBAPP_URL}?user_id={user.id}")],
            [InlineKeyboardButton("📊 View My Profile", url=f"{WEBAPP_URL}/profile?user_id={user.id}")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """📖 **Gaming Quest Hub Bot**

This bot sends you notifications about:
• 🆕 New quests available
• 🎁 New rewards added
• ✅ Quest completion confirmations
• 🏆 Achievement unlocks

**How to Use:**
1. Use /start to register
2. Visit the web app to view and complete quests
3. Receive notifications here when new content is added
4. Complete quests on the web app to earn XP

**Commands:**
/start - Register and get web app link
/help - Show this help message

**Need Support?**
Visit the web app and contact an admin.
"""
        
        keyboard = [
            [InlineKeyboardButton("🎮 Open Web App", url=f"{WEBAPP_URL}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ==================== CALLBACK HANDLER ====================
    
    async def button_callback(self, query):
        """Handle button callbacks - Mainly for verification"""
        data = query.data
        
        if data == "help":
            await self.show_help(query)
        elif data.startswith("verify_telegram_"):
            # Telegram membership verification
            task_id = data.replace("verify_telegram_", "")
            await self.verify_telegram_membership(query, task_id)
        else:
            # Unknown callback - redirect to web app
            await query.edit_message_text(
                "⚠️ This action requires the web app.\n\n"
                "Please visit the Gaming Quest Hub to continue.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎮 Open Web App", url=WEBAPP_URL)
                ]])
            )
    
    async def show_help(self, query):
        """Show help message from callback"""
        message = """📖 **Gaming Quest Hub Bot**

This bot sends you notifications about:
• 🆕 New quests available
• 🎁 New rewards added
• ✅ Quest completion confirmations
• 🏆 Achievement unlocks

**How to Use:**
Visit the web app to complete quests and earn XP!
"""
        
        keyboard = [
            [InlineKeyboardButton("🎮 Open Web App", url=WEBAPP_URL)],
            [InlineKeyboardButton("« Back", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    # ==================== VERIFICATION METHODS ====================
    
    async def verify_telegram_membership(self, query, task_id: str):
        """
        Verify if user is a member of specified Telegram group/channel
        This is the ONLY verification the bot handles
        """
        user = query.from_user
        db_user = self.api_client.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text(
                "❌ Please use /start to register first."
            )
            return
        
        # Get task details
        task = self.api_client.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text(
                "❌ Quest not found."
            )
            return
        
        # Check if it's a Telegram quest
        if task.get('platform') != 'telegram':
            await query.edit_message_text(
                "⚠️ This verification is only for Telegram quests.\n\n"
                "Please complete other quests on the web app.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎮 Open Web App", url=WEBAPP_URL)
                ]])
            )
            return
        
        # Get channel/group info from verification_data
        verification_data = task.get('verification_data', {})
        channel_username = verification_data.get('channel_username')
        
        if not channel_username:
            await query.edit_message_text(
                "❌ Invalid quest configuration. Please contact an admin."
            )
            return
        
        try:
            # Check if user is member
            chat_member = await self.application.bot.get_chat_member(
                chat_id=f"@{channel_username}",
                user_id=user.id
            )
            
            # Check membership status
            is_member = chat_member.status in ['member', 'administrator', 'creator']
            
            if is_member:
                # Complete the task
                result = self.api_client.complete_task(db_user['id'], task_id)
                
                if result and 'error' not in result:
                    await query.edit_message_text(
                        f"✅ **Quest Completed!**\n\n"
                        f"You earned **{task['points_reward']} XP**!\n\n"
                        f"Continue your journey on the web app to complete more quests!",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🎮 View More Quests", url=WEBAPP_URL)
                        ]]),
                        parse_mode='Markdown'
                    )
                    
                    # Create notification
                    self.api_client.create_notification(
                        db_user['id'],
                        "Quest Completed!",
                        f"You earned {task['points_reward']} XP for completing '{task['title']}'",
                        "task_completed"
                    )
                    
                    logger.info(f"✅ User {user.id} completed Telegram quest {task_id}")
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'Server error'
                    if 'already completed' in error_msg.lower():
                        await query.edit_message_text(
                            "ℹ️ You've already completed this quest!"
                        )
                    else:
                        await query.edit_message_text(
                            f"❌ Error: {error_msg}\n\nPlease try again or contact support."
                        )
            else:
                # Not a member
                join_url = task.get('url', f"https://t.me/{channel_username}")
                await query.edit_message_text(
                    f"❌ **Not Verified**\n\n"
                    f"You must join the Telegram group/channel first.\n\n"
                    f"After joining, click 'Verify' again.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📱 Join Now", url=join_url)],
                        [InlineKeyboardButton("✅ Verify Again", callback_data=f"verify_telegram_{task_id}")]
                    ]),
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"❌ Error verifying Telegram membership: {e}")
            await query.edit_message_text(
                "❌ Could not verify membership. Please try again later or contact support."
            )
    
    # ==================== NOTIFICATION METHODS ====================
    
    async def send_new_quest_notification(self, user_telegram_id: int, quest_data: dict):
        """
        Send notification about new quest to user
        Called by API when new quest is created
        """
        try:
            message = f"""🆕 **New Quest Available!**

📋 **{quest_data['title']}**
{quest_data.get('description', 'Complete this quest to earn XP!')}

💰 Reward: **{quest_data['points_reward']} XP**
🏷️ Type: {quest_data.get('task_type', 'Unknown')}

Complete this quest on the web app now!
"""
            
            keyboard = [[
                InlineKeyboardButton("🎮 View Quest", url=f"{WEBAPP_URL}/quests/{quest_data['id']}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent new quest notification to user {user_telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification to {user_telegram_id}: {e}")
            return False
    
    async def send_new_reward_notification(self, user_telegram_id: int, reward_data: dict):
        """
        Send notification about new reward to user
        Called by API when new reward is added
        """
        try:
            message = f"""🎁 **New Reward Available!**

✨ **{reward_data['title']}**
{reward_data.get('description', 'Check out this new reward!')}

💎 Cost: **{reward_data['points_cost']} XP**
📦 Available: {reward_data.get('quantity_available', 'Unlimited')}

Claim this reward on the web app!
"""
            
            keyboard = [[
                InlineKeyboardButton("🎁 View Rewards", url=f"{WEBAPP_URL}/rewards")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent new reward notification to user {user_telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification to {user_telegram_id}: {e}")
            return False
    
    async def send_quest_completed_notification(self, user_telegram_id: int, quest_title: str, points: int):
        """
        Send notification when quest is completed
        Called by API after admin approval or auto-completion
        """
        try:
            message = f"""✅ **Quest Completed!**

🎉 You earned **{points} XP** for completing:
📋 {quest_title}

Keep completing quests to earn more XP!
"""
            
            keyboard = [[
                InlineKeyboardButton("🎮 View More Quests", url=f"{WEBAPP_URL}/quests")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Sent quest completion notification to user {user_telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification to {user_telegram_id}: {e}")
            return False
    
    # ==================== BOT LIFECYCLE ====================
    
    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting Notification Bot...")
        self.setup_handlers()
        logger.info("✅ Bot is running and ready to send notifications!")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main function to run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    bot = NotificationBot()
    bot.run()


if __name__ == "__main__":
    main()
