"""
Telegram Bot Implementation
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
    MessageHandler,
    ContextTypes,
    filters
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


class TelegramBot:
    """Telegram Bot Handler"""
    
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tasks", self.tasks_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        self.application.add_handler(CommandHandler("rewards", self.rewards_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
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
            welcome_message = f"🎉 Welcome, {user.first_name}!\n\nYou've been registered successfully. Start completing tasks to earn points!"
        else:
            welcome_message = f"👋 Welcome back, {user.first_name}!\n\nYou have {db_user['points']} points."
        
        keyboard = [
            [InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
            [InlineKeyboardButton("👤 My Profile", callback_data="view_profile")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="view_leaderboard")],
            [InlineKeyboardButton("🎁 Rewards", callback_data="view_rewards")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 *Bot Commands:*

/start - Start the bot and see main menu
/help - Show this help message
/tasks - View available tasks
/profile - View your profile and points
/leaderboard - View top users
/rewards - Browse available rewards

*How it works:*
1. Complete tasks to earn points
2. Accumulate points by completing various activities
3. Redeem points for rewards
4. Compete with others on the leaderboard!

*Task Types:*
• Social Media Follows
• Likes & Shares
• Video Watching
• Bonus Tasks

Happy earning! 💰
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tasks command"""
        tasks = BotAPIClient.get_active_tasks()
        
        if not tasks:
            await update.message.reply_text("No tasks available at the moment. Check back later!")
            return
        
        message = "📋 *Available Tasks:*\n\n"
        keyboard = []
        
        for i, task in enumerate(tasks[:10], 1):
            bonus_tag = "🌟 BONUS " if task['is_bonus'] else ""
            message += f"{i}. {bonus_tag}{task['title']}\n"
            message += f"   💰 Reward: {task['points_reward']} points\n"
            message += f"   📝 {task['description']}\n\n"
            
            keyboard.append([InlineKeyboardButton(
                f"{task['title']}", 
                callback_data=f"task_{task['id']}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        user = update.effective_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await update.message.reply_text("Please use /start to register first.")
            return
        
        message = f"""
👤 *Your Profile*

**Name:** {db_user['first_name']} {db_user['last_name'] or ''}
**Username:** @{db_user['username'] or 'N/A'}
**Current Points:** {db_user['points']} 💰
**Total Earned:** {db_user['total_earned_points']} 💎
**Member Since:** {db_user['created_at'][:10]}

Keep completing tasks to earn more points! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
            [InlineKeyboardButton("🎁 Rewards", callback_data="view_rewards")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def leaderboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /leaderboard command"""
        leaderboard = BotAPIClient.get_leaderboard(limit=10)
        
        if not leaderboard:
            await update.message.reply_text("Leaderboard is empty. Be the first to earn points!")
            return
        
        message = "🏆 *Top 10 Leaderboard*\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        for i, user in enumerate(leaderboard, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            username = user['username'] or user['first_name']
            message += f"{medal} {username}: {user['points']} points\n"
        
        # Check current user's rank
        current_user = update.effective_user
        db_user = BotAPIClient.get_user_by_telegram_id(current_user.id)
        if db_user:
            message += f"\n*Your Points:* {db_user['points']} 💰"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def rewards_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /rewards command"""
        rewards = BotAPIClient.get_active_rewards()
        
        if not rewards:
            await update.message.reply_text("No rewards available at the moment.")
            return
        
        message = "🎁 *Available Rewards:*\n\n"
        keyboard = []
        
        for i, reward in enumerate(rewards[:10], 1):
            available = ""
            if reward['quantity_available']:
                remaining = reward['quantity_available'] - reward['quantity_claimed']
                available = f" ({remaining} left)"
            
            message += f"{i}. {reward['title']}{available}\n"
            message += f"   💰 Cost: {reward['points_cost']} points\n"
            message += f"   📝 {reward['description']}\n\n"
            
            keyboard.append([InlineKeyboardButton(
                f"{reward['title']} - {reward['points_cost']} pts", 
                callback_data=f"reward_{reward['id']}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "view_tasks":
            await self.show_tasks(query)
        elif data == "view_profile":
            await self.show_profile(query)
        elif data == "view_leaderboard":
            await self.show_leaderboard(query)
        elif data == "view_rewards":
            await self.show_rewards(query)
        elif data.startswith("task_"):
            task_id = data.split("_")[1]
            await self.show_task_details(query, task_id)
        elif data.startswith("complete_task_"):
            task_id = data.split("_")[2]
            await self.complete_task(query, task_id)
        elif data.startswith("reward_"):
            reward_id = data.split("_")[1]
            await self.show_reward_details(query, reward_id)
        elif data.startswith("redeem_"):
            reward_id = data.split("_")[1]
            await self.redeem_reward(query, reward_id)
    
    async def show_tasks(self, query):
        """Show tasks list"""
        tasks = BotAPIClient.get_active_tasks()
        
        if not tasks:
            await query.edit_message_text("No tasks available at the moment.")
            return
        
        message = "📋 *Available Tasks:*\n\n"
        keyboard = []
        
        for i, task in enumerate(tasks[:10], 1):
            bonus_tag = "🌟 " if task['is_bonus'] else ""
            message += f"{i}. {bonus_tag}{task['title']} - {task['points_reward']} pts\n"
            
            keyboard.append([InlineKeyboardButton(
                f"{task['title']}", 
                callback_data=f"task_{task['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Menu", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_profile(self, query):
        """Show user profile"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        message = f"""
👤 *Your Profile*

**Name:** {db_user['first_name']} {db_user['last_name'] or ''}
**Current Points:** {db_user['points']} 💰
**Total Earned:** {db_user['total_earned_points']} 💎

Keep earning! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 View Tasks", callback_data="view_tasks")],
            [InlineKeyboardButton("« Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_leaderboard(self, query):
        """Show leaderboard"""
        leaderboard = BotAPIClient.get_leaderboard(limit=10)
        
        message = "🏆 *Top 10 Leaderboard*\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(leaderboard, 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            username = user['username'] or user['first_name']
            message += f"{medal} {username}: {user['points']} pts\n"
        
        keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_rewards(self, query):
        """Show rewards list"""
        rewards = BotAPIClient.get_active_rewards()
        
        message = "🎁 *Available Rewards:*\n\n"
        keyboard = []
        
        for i, reward in enumerate(rewards[:10], 1):
            message += f"{i}. {reward['title']} - {reward['points_cost']} pts\n"
            keyboard.append([InlineKeyboardButton(
                f"{reward['title']}", 
                callback_data=f"reward_{reward['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back to Menu", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_task_details(self, query, task_id: str):
        """Show task details"""
        task = BotAPIClient.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("Task not found.")
            return
        
        bonus_tag = "🌟 BONUS TASK\n" if task['is_bonus'] else ""
        message = f"""
{bonus_tag}📋 *{task['title']}*

**Description:** {task['description']}
**Reward:** {task['points_reward']} points 💰
**Platform:** {task['platform'] or 'N/A'}
"""
        
        if task['url']:
            message += f"\n🔗 [Click here to complete]({task['url']})"
        
        keyboard = [
            [InlineKeyboardButton("✅ Mark as Complete", callback_data=f"complete_task_{task_id}")],
            [InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def complete_task(self, query, task_id: str):
        """Complete a task"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        result = BotAPIClient.complete_task(db_user['id'], task_id)
        
        if result and 'error' not in result:
            task = BotAPIClient.get_task_by_id(task_id)
            if task['verification_required']:
                message = "✅ Task submitted! Waiting for verification."
            else:
                message = f"🎉 Task completed! You earned {task['points_reward']} points!"
                
                # Create notification
                BotAPIClient.create_notification(
                    db_user['id'],
                    "Task Completed!",
                    f"You earned {task['points_reward']} points for completing '{task['title']}'",
                    "task_verified"
                )
        else:
            message = "❌ Error completing task. Please try again."
        
        keyboard = [[InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    
    async def show_reward_details(self, query, reward_id: str):
        """Show reward details"""
        reward = BotAPIClient.get_active_rewards()
        reward = next((r for r in reward if r['id'] == reward_id), None)
        
        if not reward:
            await query.edit_message_text("Reward not found.")
            return
        
        available = ""
        if reward['quantity_available']:
            remaining = reward['quantity_available'] - reward['quantity_claimed']
            available = f"\n**Available:** {remaining} left"
        
        message = f"""
🎁 *{reward['title']}*

**Description:** {reward['description']}
**Cost:** {reward['points_cost']} points 💰{available}
**Type:** {reward['reward_type']}
        """
        
        keyboard = [
            [InlineKeyboardButton("🎁 Redeem Now", callback_data=f"redeem_{reward_id}")],
            [InlineKeyboardButton("« Back to Rewards", callback_data="view_rewards")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def redeem_reward(self, query, reward_id: str):
        """Redeem a reward"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        result = BotAPIClient.redeem_reward(db_user['id'], reward_id)
        
        if 'error' in result:
            message = f"❌ {result['error']}"
        else:
            message = f"🎉 Reward redeemed successfully!\n\n**Your Code:** `{result['redemption_code']}`\n\nSave this code for future use!"
            
            # Create notification
            BotAPIClient.create_notification(
                db_user['id'],
                "Reward Redeemed!",
                f"Your redemption code: {result['redemption_code']}",
                "reward_available"
            )
        
        keyboard = [[InlineKeyboardButton("« Back to Rewards", callback_data="view_rewards")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
