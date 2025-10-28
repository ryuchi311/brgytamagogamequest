#!/usr/bin/env python3
"""
Telegram Bot - Group Management Commands
Manages groups via bot commands in Telegram
"""

import os
import sys
import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler
)
from dotenv import load_dotenv

# Load environment
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUPS_FILE = 'telegramgroups.json'

# Conversation states
ADD_GROUP_CHAT_ID = 1

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Management
# ============================================================================

def load_groups():
    """Load groups from JSON file"""
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"groups": []}

def save_groups(data):
    """Save groups to JSON file"""
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_chat_info(bot_token, chat_id):
    """Get chat information from Telegram API"""
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    params = {"chat_id": chat_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return data.get('result'), None
        else:
            return None, data.get('description', 'Unknown error')
    except Exception as e:
        return None, str(e)

# ============================================================================
# Bot Commands
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""
👋 Welcome {user.first_name}!

🤖 **Telegram Group Manager Bot**

I can help you manage your Telegram groups for Quest Hub!

**Commands:**
/addgroup - Add a new group to the database
/listgroups - List all registered groups
/removegroup - Remove a group
/exportconfig - Export quest configurations
/help - Show this help message

**Quick Start:**
1. Add me to your Telegram group
2. Use /addgroup to register it
3. Use /exportconfig to get quest JSON
4. Create quests with the generated config!

Let's get started! 🚀
    """
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 **Help - Bot Commands**

**Group Management:**
• `/addgroup` - Add a group to database
  Example: Send this in the group you want to add

• `/listgroups` - View all registered groups
  Shows: title, chat_id, members, etc.

• `/removegroup` - Remove a group
  Choose from list of registered groups

• `/exportconfig` - Export quest configurations
  Get ready-to-use JSON for creating quests

**How to Add a Group:**
1. Add this bot to your group
2. In the group, send: `/addgroup`
3. Bot will fetch and save group info
4. Done! ✅

**How to Get Quest Config:**
1. Use `/exportconfig`
2. Copy the JSON output
3. Use it to create a quest
4. Users can join and verify!

**Supported Group Types:**
• Public groups (@username)
• Private groups (numeric ID)
• Supergroups
• Channels (requires admin)

Need more help? Contact admin! 💬
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addgroup command"""
    chat = update.effective_chat
    
    # Check if this is a group
    if chat.type not in ['group', 'supergroup', 'channel']:
        await update.message.reply_text(
            "⚠️ This command must be used in a group/channel!\n\n"
            "Steps:\n"
            "1. Add me to your group\n"
            "2. In the group, send: /addgroup\n"
            "3. I'll register the group!"
        )
        return
    
    # Get chat info
    chat_info, error = get_chat_info(TELEGRAM_BOT_TOKEN, chat.id)
    
    if error:
        await update.message.reply_text(
            f"❌ Error fetching group info:\n{error}\n\n"
            "Make sure I have permission to read group information!"
        )
        return
    
    # Load existing groups
    data = load_groups()
    
    # Check if already exists
    existing = None
    for group in data['groups']:
        if group['id'] == chat.id:
            existing = group
            break
    
    # Prepare group data
    group_data = {
        "id": chat.id,
        "title": chat.title,
        "username": chat.username if chat.username else None,
        "chat_id": f"@{chat.username}" if chat.username else str(chat.id),
        "type": chat.type,
        "description": chat.description if hasattr(chat, 'description') else None,
        "member_count": await update.effective_chat.get_member_count() if chat.type != 'channel' else None,
        "added_at": datetime.now().isoformat() if not existing else existing['added_at'],
        "updated_at": datetime.now().isoformat(),
        "invite_link": chat_info.get('invite_link'),
        "notes": existing['notes'] if existing else ""
    }
    
    # Add or update
    if existing:
        data['groups'].remove(existing)
        action = "updated"
    else:
        action = "added"
    
    data['groups'].append(group_data)
    save_groups(data)
    
    # Success message
    member_text = f"👥 Members: {group_data['member_count']}\n" if group_data['member_count'] else ""
    username_text = f"🔗 Username: @{chat.username}\n" if chat.username else ""
    
    success_text = f"""
✅ **Group {action.capitalize()} Successfully!**

📋 **Group Info:**
📌 Title: {group_data['title']}
🆔 ID: `{group_data['id']}`
{username_text}🏷️ Type: {group_data['type']}
{member_text}
**Use in quests:**
`"chat_id": "{group_data['chat_id']}"`

Use /exportconfig to get full quest JSON!
    """
    
    await update.message.reply_text(success_text, parse_mode='Markdown')

async def listgroups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listgroups command"""
    data = load_groups()
    
    if not data['groups']:
        await update.message.reply_text(
            "📭 **No groups registered yet!**\n\n"
            "To add a group:\n"
            "1. Add me to the group\n"
            "2. In the group, send: /addgroup"
        )
        return
    
    # Build list
    groups_text = f"📋 **Registered Groups ({len(data['groups'])})**\n\n"
    
    for i, group in enumerate(data['groups'], 1):
        username_text = f"@{group['username']}" if group.get('username') else "Private"
        member_text = f" • {group['member_count']} members" if group.get('member_count') else ""
        
        groups_text += f"**{i}. {group['title']}**\n"
        groups_text += f"   🆔 `{group['chat_id']}`\n"
        groups_text += f"   🔗 {username_text}{member_text}\n"
        groups_text += f"   📅 Added: {group['added_at'][:10]}\n\n"
    
    groups_text += "\nUse /exportconfig to get quest configurations!"
    
    await update.message.reply_text(groups_text, parse_mode='Markdown')

async def removegroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removegroup command"""
    data = load_groups()
    
    if not data['groups']:
        await update.message.reply_text("📭 No groups to remove!")
        return
    
    # Create inline keyboard with groups
    keyboard = []
    for i, group in enumerate(data['groups']):
        keyboard.append([
            InlineKeyboardButton(
                f"{group['title']} ({group['chat_id']})",
                callback_data=f"remove_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="remove_cancel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🗑️ **Remove Group**\n\nSelect a group to remove:",
        reply_markup=reply_markup
    )

async def exportconfig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /exportconfig command"""
    data = load_groups()
    
    if not data['groups']:
        await update.message.reply_text(
            "📭 **No groups to export!**\n\n"
            "Add groups first using /addgroup"
        )
        return
    
    # Build export message
    export_text = "📤 **Quest Configurations**\n\n"
    export_text += "Copy and use these to create quests:\n\n"
    export_text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for group in data['groups']:
        config = {
            "platform": "telegram",
            "task_type": "telegram_join_group",
            "title": f"Join {group['title']}",
            "description": "Join our community on Telegram",
            "points_reward": 100,
            "verification_data": {
                "chat_id": group['chat_id'],
                "chat_name": group['title'],
                "method": "api"
            }
        }
        
        # Add URL if available
        if group.get('invite_link'):
            config['url'] = group['invite_link']
        elif group.get('username'):
            config['url'] = f"https://t.me/{group['username']}"
        
        export_text += f"**// {group['title']}**\n"
        export_text += f"```json\n{json.dumps(config, indent=2)}\n```\n\n"
    
    # Send in chunks if too long
    if len(export_text) > 4000:
        # Send groups one by one
        for group in data['groups']:
            config = {
                "platform": "telegram",
                "task_type": "telegram_join_group",
                "title": f"Join {group['title']}",
                "description": "Join our community on Telegram",
                "url": group.get('invite_link') or f"https://t.me/{group.get('username', '')}",
                "points_reward": 100,
                "verification_data": {
                    "chat_id": group['chat_id'],
                    "chat_name": group['title'],
                    "method": "api"
                }
            }
            
            msg = f"**{group['title']}**\n```json\n{json.dumps(config, indent=2)}\n```"
            await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text(export_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split('_')
    action = data_parts[0]
    
    if action == "remove":
        if data_parts[1] == "cancel":
            await query.edit_message_text("❌ Cancelled")
            return
        
        # Remove group
        index = int(data_parts[1])
        data = load_groups()
        
        if 0 <= index < len(data['groups']):
            removed = data['groups'].pop(index)
            save_groups(data)
            
            await query.edit_message_text(
                f"✅ **Removed Group**\n\n"
                f"Group: {removed['title']}\n"
                f"Chat ID: `{removed['chat_id']}`"
            )
        else:
            await query.edit_message_text("❌ Invalid selection")

# ============================================================================
# Admin Commands
# ============================================================================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    data = load_groups()
    
    total_groups = len(data['groups'])
    public_groups = sum(1 for g in data['groups'] if g.get('username'))
    private_groups = total_groups - public_groups
    
    total_members = sum(g.get('member_count', 0) for g in data['groups'] if g.get('member_count'))
    
    stats_text = f"""
📊 **Bot Statistics**

📋 Total Groups: {total_groups}
🌐 Public Groups: {public_groups}
🔒 Private Groups: {private_groups}
👥 Total Members: {total_members}

📁 Storage: {GROUPS_FILE}
🤖 Bot: @{context.bot.username}
    """
    
    await update.message.reply_text(stats_text)

# ============================================================================
# Main
# ============================================================================

def main():
    """Run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addgroup", addgroup))
    application.add_handler(CommandHandler("listgroups", listgroups))
    application.add_handler(CommandHandler("removegroup", removegroup))
    application.add_handler(CommandHandler("exportconfig", exportconfig))
    application.add_handler(CommandHandler("stats", stats))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start bot
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 Telegram Group Manager Bot")
    print(f"   Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Bot is running...")
    print("   Press Ctrl+C to stop")
    print("")
    print("Commands:")
    print("  /start - Welcome message")
    print("  /addgroup - Add group (use in group)")
    print("  /listgroups - List all groups")
    print("  /removegroup - Remove a group")
    print("  /exportconfig - Export quest configs")
    print("  /stats - Show statistics")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
