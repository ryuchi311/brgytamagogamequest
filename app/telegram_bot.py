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
        # Build the application but don't initialize handlers yet
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        # Initialize API client
        self.api_client = BotAPIClient()
    
    def setup_handlers(self):
        """Register all command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tasks", self.tasks_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        self.application.add_handler(CommandHandler("rewards", self.rewards_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Handler for video verification codes (must be after commands, before catch-all)
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.verify_video_code_handler
        ))
    
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
            welcome_message = f"""🎉 Welcome, {user.first_name}!

You've been registered successfully!

🎮 **Ready to Start Your Quest Journey?**

Use the buttons below to explore, or tap the **Menu Button** (≡) to open our Gaming Quest Hub mini app for the full experience!

✨ In the mini app you can:
• View all available quests
• Track your XP in real-time
• See the leaderboard
• Claim rewards instantly
• Get a better gaming experience!

Let's start earning XP! 🚀"""
        else:
            welcome_message = f"""👋 Welcome back, {user.first_name}!

💎 **Current XP:** {db_user['points']} points

🎮 **Quick Actions:**
Use the buttons below, or tap the **Menu Button** (≡) to open the Gaming Quest Hub for the full experience!

Keep up the great work! 🔥"""
        
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
🎮 **Gaming Quest Hub - Help Guide**

**🚀 Getting Started:**
This is a Telegram Mini App! For the best experience, tap the **Menu Button** (≡) to open the full Gaming Quest Hub.

**🤖 Bot Commands:**
/start - Start the bot and see main menu
/help - Show this help message
/tasks - View available tasks
/profile - View your profile and points
/leaderboard - View top users
/rewards - Browse available rewards

**🎯 How it works:**
1. Complete quests to earn XP points
2. Each quest has different requirements (follow, like, watch, etc.)
3. Verify your completion in the app
4. Earn XP and climb the leaderboard!
5. Spend XP on exclusive rewards

**📱 Two Ways to Play:**

1️⃣ **Mini App (Recommended)**
   • Tap the Menu Button (≡)
   • Full gaming interface
   • Real-time updates
   • Better quest tracking

2️⃣ **Bot Commands**
   • Use commands in this chat
   • Quick access to info
   • Basic features

**✨ Quest Types:**
• 📱 Social Media (Follow, Like, Share)
• 📺 YouTube (Watch, Subscribe)
• 🐦 Twitter/X (Follow, Retweet)
• ✈️ Telegram (Join channels/groups)
• 🎁 Daily Bonuses

**💎 XP & Rewards:**
• Earn XP by completing quests
• Spend XP on rewards
• Compete for top spots
• Track progress in real-time

**🔐 Your Account:**
Your Telegram account IS your login - no passwords needed! Your progress is automatically saved.

Happy questing! �
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
        elif data.startswith("claim_auto_"):
            task_id = data.split("_")[2]
            await self.claim_auto_quest_points(query, task_id)
        elif data.startswith("telegram_verify_"):
            task_id = data.split("_")[2]
            await self.verify_telegram_membership(query, task_id)
        elif data.startswith("twitter_verify_"):
            task_id = data.split("_")[2]
            await self.start_twitter_verification(query, task_id)
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
        
        # Check if this is a YouTube video quest with verification
        is_video_quest = (task.get('platform') == 'youtube' and 
                         task.get('verification_data') and 
                         task['verification_data'].get('method') == 'time_delay_code')
        
        if is_video_quest:
            await self.start_video_quest(query, task)
            return
        
        # Check if this is a Telegram quest that can be auto-verified
        is_telegram_quest = (task.get('platform') == 'telegram' and 
                            task.get('verification_data') and 
                            task['verification_data'].get('method') == 'telegram_membership')
        
        if is_telegram_quest:
            await self.start_telegram_quest(query, task)
            return
        
        # Check if this is an auto-complete website link quest (no verification needed)
        is_auto_link_quest = (task.get('task_type') == 'link' and 
                              task.get('platform') == 'website' and 
                              not task.get('verification_required'))
        
        if is_auto_link_quest:
            await self.start_auto_link_quest(query, task)
            return
        
        # Check if this is a Twitter quest that can be auto-verified
        is_twitter_quest = task.get('platform') == 'twitter'
        
        bonus_tag = "🌟 BONUS TASK\n" if task['is_bonus'] else ""
        message = f"""
{bonus_tag}📋 *{task['title']}*

**Description:** {task['description']}
**Reward:** {task['points_reward']} points 💰
**Platform:** {task['platform'] or 'N/A'}
"""
        
        if task['url']:
            message += f"\n🔗 [Click here to complete]({task['url']})"
        
        # For Twitter tasks, offer auto-verification
        if is_twitter_quest:
            message += "\n\n🔍 *Auto-Verification Available!*\nClick 'Verify Twitter' to automatically check if you completed this task."
            keyboard = [
                [InlineKeyboardButton("🐦 Verify Twitter", callback_data=f"twitter_verify_{task_id}")],
                [InlineKeyboardButton("✅ Manual Verification", callback_data=f"complete_task_{task_id}")],
                [InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]
            ]
        else:
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
    
    async def start_video_quest(self, query, task):
        """Start a YouTube video quest with time delay + code verification"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        # Start video view tracking
        result = BotAPIClient.start_video_view(db_user['id'], task['id'])
        
        if not result or 'error' in result:
            await query.edit_message_text("❌ Error starting video quest. Please try again.")
            return
        
        # Get verification data
        verification_data = task['verification_data']
        min_watch_time = verification_data.get('min_watch_time_seconds', 120)
        code_timestamp = verification_data.get('code_timestamp', 'during the video')
        
        bonus_tag = "🌟 BONUS TASK\n" if task['is_bonus'] else ""
        message = f"""
{bonus_tag}🎬 *{task['title']}*

**Description:** {task['description']}
**Reward:** {task['points_reward']} points 💰

📺 *How to Complete:*
1. Watch the video for at least {min_watch_time // 60} minutes
2. Look for the secret code at {code_timestamp}
3. Send me the code to complete the quest

⚠️ *Important:*
• You have 3 attempts to enter the correct code
• The timer has started - watch carefully!

{task['url'] if task.get('url') else 'No URL provided'}
"""
        
        keyboard = [[InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
        # Store task_id in user context for code verification
        if 'user_data' not in query._bot.__dict__:
            query._bot.user_data = {}
        if user.id not in query._bot.user_data:
            query._bot.user_data[user.id] = {}
        query._bot.user_data[user.id]['active_video_task'] = task['id']
    
    async def start_telegram_quest(self, query, task):
        """Start a Telegram membership quest with auto-verification"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        # Get verification data
        verification_data = task.get('verification_data', {})
        chat_id = verification_data.get('chat_id')
        chat_name = verification_data.get('chat_name', 'the group/channel')
        invite_link = verification_data.get('invite_link') or task.get('url')
        action_type = verification_data.get('type', 'join_group')
        
        bonus_tag = "🌟 BONUS TASK\n" if task.get('is_bonus') else ""
        
        # Determine emoji based on action type
        emoji = "✈️" if action_type == 'join_group' else "📢"
        action_text = "Join the group" if action_type == 'join_group' else "Join the channel"
        
        message = f"""
{bonus_tag}{emoji} *{task['title']}*

**Description:** {task['description']}
**Reward:** {task['points_reward']} points 💰

📱 *How to Complete:*
1. {action_text}: {chat_name}
2. Click "✅ Verify Membership" below
3. Bot will automatically check if you're a member

⚠️ *Important:*
• You must actually join to get verified
• Already a member? Just verify!
• Verification is instant!
"""
        
        keyboard = []
        
        # Add join button if invite link is available
        if invite_link:
            keyboard.append([InlineKeyboardButton(f"{emoji} {action_text.title()}", url=invite_link)])
        
        # Add verify button
        keyboard.append([InlineKeyboardButton("✅ Verify Membership", callback_data=f"telegram_verify_{task['id']}")])
        keyboard.append([InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def verify_telegram_membership(self, query, task_id: str):
        """Verify if user is a member of the Telegram group/channel"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        # Get task details
        task = BotAPIClient.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("❌ Task not found.")
            return
        
        verification_data = task.get('verification_data', {})
        chat_id = verification_data.get('chat_id')
        
        if not chat_id:
            await query.edit_message_text("❌ Quest configuration error: No chat ID specified.")
            return
        
        # Show checking message
        await query.edit_message_text("🔍 Checking membership status...")
        
        try:
            # Check if user is a member of the chat
            chat_member = await self.application.bot.get_chat_member(chat_id, user.id)
            
            # Valid member statuses: creator, administrator, member
            # Exclude: left, kicked, restricted (if can't send messages)
            is_member = chat_member.status in ['creator', 'administrator', 'member']
            
            if is_member:
                # Complete the task
                result = BotAPIClient.complete_task(db_user['id'], task_id)
                
                if result and 'error' not in result:
                    message = f"""
✅ *Verification Successful!*

🎉 You're a member! Quest completed!
💰 You earned {task['points_reward']} points!

Keep completing quests to earn more! 🚀
"""
                    # Create notification
                    BotAPIClient.create_notification(
                        db_user['id'],
                        "Quest Completed!",
                        f"You earned {task['points_reward']} points for completing '{task['title']}'",
                        "task_verified"
                    )
                else:
                    message = "❌ Error completing quest. You may have already completed it or there was a server issue."
            else:
                message = f"""
❌ *Not a Member Yet*

You need to join the group/channel first!

Status: {chat_member.status}

Please:
1. Join the group/channel
2. Come back and click "Verify Membership" again
"""
        
        except Exception as e:
            logger.error(f"Error verifying Telegram membership: {e}")
            message = f"""
❌ *Verification Failed*

Could not verify membership. This could be because:
• The bot is not an admin in that group/channel
• Invalid chat ID configuration
• The group/channel is private

Please contact an admin or try manual verification.

Error: {str(e)[:100]}
"""
        
        keyboard = [[InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def start_auto_link_quest(self, query, task):
        """Handle auto-complete website link quests - instant reward!"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        url = task.get('url', 'No URL provided')
        
        bonus_tag = "🌟 BONUS TASK\n" if task.get('is_bonus', False) else ""
        message = f"""
{bonus_tag}🔗 *{task['title']}*

**Description:** {task['description']}
**Reward:** {task['points_reward']} points 💰

🚀 *INSTANT REWARD QUEST!*

Simply click the button below to visit the website.
You'll get your points automatically! 🎁

No verification needed - just click and earn! 💸
"""
        
        keyboard = [
            [InlineKeyboardButton("🌐 Visit Website & Get Points!", url=url, callback_data=f"auto_complete_{task['id']}")],
            [InlineKeyboardButton("✅ I Visited - Claim Points", callback_data=f"claim_auto_{task['id']}")],
            [InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def claim_auto_quest_points(self, query, task_id: str):
        """Claim points for auto-complete quest (instant reward, no verification)"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        task = BotAPIClient.get_task_by_id(task_id)
        
        if not task:
            await query.edit_message_text("Task not found.")
            return
        
        # Complete the task instantly (no verification needed)
        result = BotAPIClient.complete_task(db_user['id'], task_id)
        
        if result and 'error' not in result:
            message = f"""
🎉 *Quest Completed!*

💰 You earned {task['points_reward']} points!

Thank you for visiting! Keep completing quests! 🚀
"""
            # Create notification
            BotAPIClient.create_notification(
                db_user['id'],
                "Quest Completed!",
                f"You earned {task['points_reward']} points for visiting '{task['title']}'",
                "task_completed"
            )
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Server error'
            if 'already completed' in error_msg.lower():
                message = "ℹ️ You've already completed this quest!"
            else:
                message = f"❌ Error completing quest: {error_msg}"
        
        keyboard = [[InlineKeyboardButton("« Back to Tasks", callback_data="view_tasks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def verify_video_code_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video verification code submissions OR Twitter username"""
        user = update.effective_user
        text_input = update.message.text.strip()
        
        # Check if user has an active Twitter verification
        if (hasattr(context.bot, 'user_data') and 
            user.id in context.bot.user_data and 
            'twitter_task_id' in context.bot.user_data[user.id]):
            # Handle Twitter username
            await self.handle_twitter_username(update, context)
            return
        
        # Check if user has an active video quest
        if (not hasattr(context.bot, 'user_data') or 
            user.id not in context.bot.user_data or 
            'active_video_task' not in context.bot.user_data[user.id]):
            # Not in any verification mode, ignore
            return
        
        # Handle video code
        code = text_input        
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start to register first.")
            return
        
        # Verify the code
        result = BotAPIClient.verify_video_code(db_user['id'], code)
        
        if not result:
            await update.message.reply_text("❌ Error verifying code. Please try again.")
            return
        
        if result.get('success'):
            task = result.get('task', {})
            time_watched = result.get('time_watched_seconds', 0)
            
            message = f"""
🎉 *Quest Completed!*

Congratulations! You've successfully completed the video quest!

**Task:** {task.get('title', 'Video Quest')}
**Points Earned:** {task.get('points_reward', 0)} points 💰
**Time Watched:** {time_watched // 60}m {time_watched % 60}s

Keep completing quests to climb the leaderboard! 🏆
"""
            
            # Clear active video task
            del context.bot.user_data[user.id]['active_video_task']
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        elif result.get('error') == 'too_soon':
            min_time = result.get('min_watch_time_seconds', 120)
            time_watched = result.get('time_watched_seconds', 0)
            time_remaining = min_time - time_watched
            
            message = f"""
⏱️ *Please watch more of the video!*

You need to watch at least {min_time // 60} minutes.
Time watched: {time_watched // 60}m {time_watched % 60}s
Time remaining: {time_remaining // 60}m {time_remaining % 60}s

Come back and send the code after watching more! 📺
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            
        elif result.get('error') == 'wrong_code':
            attempts_left = result.get('attempts_left', 0)
            
            if attempts_left > 0:
                message = f"""
❌ *Incorrect code!*

That's not the right code. Please try again.
Attempts remaining: {attempts_left}

Make sure you're entering the exact code shown in the video! 🔍
"""
            else:
                message = """
🚫 *Quest Failed*

You've used all 3 attempts with incorrect codes.
Please try again with a different quest or watch the video again.
"""
                # Clear active video task
                if user.id in context.bot.user_data:
                    context.bot.user_data[user.id].pop('active_video_task', None)
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        elif result.get('error') == 'max_attempts':
            message = """
🚫 *Maximum Attempts Reached*

You've already used all 3 attempts for this quest.
Please try a different quest.
"""
            # Clear active video task
            if user.id in context.bot.user_data:
                context.bot.user_data[user.id].pop('active_video_task', None)
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        else:
            await update.message.reply_text("❌ Error verifying code. Please try again.")
    
    async def start_twitter_verification(self, query, task_id: str):
        """Start Twitter verification flow - ask for username"""
        user = query.from_user
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        
        if not db_user:
            await query.edit_message_text("Please use /start to register first.")
            return
        
        task = BotAPIClient.get_task_by_id(task_id)
        if not task:
            await query.edit_message_text("Task not found.")
            return
        
        # Store task_id in user context
        if 'user_data' not in query._bot.__dict__:
            query._bot.user_data = {}
        if user.id not in query._bot.user_data:
            query._bot.user_data[user.id] = {}
        query._bot.user_data[user.id]['twitter_task_id'] = task_id
        query._bot.user_data[user.id]['twitter_task_url'] = task.get('url', '')
        
        # Determine verification type from task
        task_title = task['title'].lower()
        task_desc = task['description'].lower()
        
        if 'follow' in task_title or 'follow' in task_desc:
            verification_type = 'follow'
        elif 'like' in task_title or 'like' in task_desc:
            verification_type = 'like'
        elif 'retweet' in task_title or 'retweet' in task_desc:
            verification_type = 'retweet'
        else:
            verification_type = 'follow'  # Default
        
        query._bot.user_data[user.id]['twitter_verification_type'] = verification_type
        
        message = f"""
🐦 *Twitter Verification*

**Quest:** {task['title']}
**Reward:** {task['points_reward']} points 💰

📋 *Steps:*
1. Complete the Twitter action: {task.get('url', 'See task description')}
2. Send me your Twitter username (e.g., @YourHandle)
3. I'll verify automatically!

⚡ *Please send your Twitter username now:*
"""
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    async def handle_twitter_username(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Twitter username submission for verification"""
        user = update.effective_user
        username_input = update.message.text.strip()
        
        # Check if user has active Twitter verification
        if (not hasattr(context.bot, 'user_data') or 
            user.id not in context.bot.user_data or 
            'twitter_task_id' not in context.bot.user_data[user.id]):
            # Not in Twitter verification mode
            return
        
        db_user = BotAPIClient.get_user_by_telegram_id(user.id)
        if not db_user:
            await update.message.reply_text("Please use /start to register first.")
            return
        
        task_id = context.bot.user_data[user.id]['twitter_task_id']
        task_url = context.bot.user_data[user.id].get('twitter_task_url', '')
        verification_type = context.bot.user_data[user.id].get('twitter_verification_type', 'follow')
        
        # Extract tweet ID if it's a like/retweet task
        tweet_id = None
        if verification_type in ['like', 'retweet'] and task_url:
            # Extract tweet ID from URL
            from app.twitter_client import twitter_client
            tweet_id = twitter_client.extract_tweet_id(task_url)
        
        # Send "verifying" message
        verifying_msg = await update.message.reply_text("🔍 Verifying your Twitter account... Please wait.")
        
        # Call verification API
        result = None
        if verification_type == 'follow':
            result = BotAPIClient.verify_twitter_follow(db_user['id'], task_id, username_input)
        elif verification_type == 'like' and tweet_id:
            result = BotAPIClient.verify_twitter_like(db_user['id'], task_id, username_input, tweet_id)
        elif verification_type == 'retweet' and tweet_id:
            result = BotAPIClient.verify_twitter_retweet(db_user['id'], task_id, username_input, tweet_id)
        else:
            await verifying_msg.edit_text("❌ Could not determine verification type. Please use manual verification.")
            return
        
        # Delete "verifying" message
        await verifying_msg.delete()
        
        if not result:
            await update.message.reply_text("❌ Error connecting to Twitter API. Please try manual verification.")
            # Clear Twitter task from context
            context.bot.user_data[user.id].pop('twitter_task_id', None)
            return
        
        # Check if API unavailable (rate limit)
        if result.get('fallback_to_manual'):
            message = f"""
⚠️ *Twitter API Limit Reached*

Our monthly Twitter verification limit has been reached.
Your task has been submitted for manual verification by our team.

You'll be notified once it's reviewed! 📧
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            # Clear Twitter task from context
            context.bot.user_data[user.id].pop('twitter_task_id', None)
            return
        
        if result.get('success') and result.get('verified'):
            # Success!
            points_earned = result.get('points_earned', 0)
            message = f"""
🎉 *Twitter Quest Completed!*

Congratulations! Your Twitter {verification_type} has been verified!

**Points Earned:** {points_earned} XP 💰

Keep completing quests to climb the leaderboard! 🏆
"""
            # Clear Twitter task from context
            context.bot.user_data[user.id].pop('twitter_task_id', None)
            context.bot.user_data[user.id].pop('twitter_task_url', None)
            context.bot.user_data[user.id].pop('twitter_verification_type', None)
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        elif result.get('already_completed'):
            await update.message.reply_text("✅ You've already completed this quest!")
            # Clear Twitter task from context
            context.bot.user_data[user.id].pop('twitter_task_id', None)
            
        else:
            # Not verified
            error_message = result.get('message', 'Verification failed')
            message = f"""
❌ *Verification Failed*

{error_message}

💡 *Make sure you:*
1. Completed the Twitter action
2. Your account is public (not private)
3. Entered the correct username

You can try again or use manual verification.
"""
            await update.message.reply_text(message, parse_mode='Markdown')
    
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
        # Setup handlers before running
        self.setup_handlers()
        # Start polling
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        logger.info("Initializing Telegram Bot...")
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
