#!/usr/bin/env python3
"""
Telegram Group Manager Bot
Adds groups to telegramgroups.json for easy quest management
"""

import os
import sys
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GROUPS_FILE = 'telegramgroups.json'

def load_groups():
    """Load existing groups from JSON file"""
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"groups": []}

def save_groups(data):
    """Save groups to JSON file"""
    with open(GROUPS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved to {GROUPS_FILE}")

def get_chat_info(chat_id):
    """Get chat information from Telegram API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChat"
    params = {"chat_id": chat_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return data.get('result')
        else:
            print(f"❌ Error: {data.get('description')}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def get_bot_info():
    """Get bot information"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            return data.get('result')
        return None
    except:
        return None

def add_group_interactive():
    """Interactive mode to add a group"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📝 Add Telegram Group")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    # Get chat_id
    print("Enter the group Chat ID:")
    print("  • For public groups: @groupusername")
    print("  • For private groups: -1001234567890")
    print("  • Or use numeric ID")
    print()
    chat_id = input("Chat ID: ").strip()
    
    if not chat_id:
        print("❌ Chat ID cannot be empty")
        return False
    
    # Get chat info from Telegram
    print()
    print("🔍 Fetching group information from Telegram...")
    chat_info = get_chat_info(chat_id)
    
    if not chat_info:
        print("❌ Failed to get group information")
        print("   Make sure:")
        print("   1. Bot is added to the group")
        print("   2. Chat ID is correct")
        return False
    
    # Extract info
    group_id = chat_info.get('id')
    group_title = chat_info.get('title', 'Unknown Group')
    group_username = chat_info.get('username', '')
    group_type = chat_info.get('type', 'unknown')
    group_description = chat_info.get('description', '')
    member_count = chat_info.get('members_count', 0)
    
    print()
    print("✅ Group found!")
    print(f"   Title: {group_title}")
    print(f"   Type: {group_type}")
    if group_username:
        print(f"   Username: @{group_username}")
    print(f"   ID: {group_id}")
    if member_count > 0:
        print(f"   Members: {member_count}")
    if group_description:
        print(f"   Description: {group_description[:100]}...")
    print()
    
    # Confirm
    confirm = input("Add this group? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return False
    
    # Load existing groups
    data = load_groups()
    
    # Check if already exists
    for group in data['groups']:
        if group['id'] == group_id:
            print(f"⚠️  Group already exists in {GROUPS_FILE}")
            update = input("Update information? (y/n): ").strip().lower()
            if update != 'y':
                return False
            data['groups'].remove(group)
            break
    
    # Add new group
    new_group = {
        "id": group_id,
        "title": group_title,
        "username": group_username if group_username else None,
        "chat_id": f"@{group_username}" if group_username else str(group_id),
        "type": group_type,
        "description": group_description if group_description else None,
        "member_count": member_count if member_count > 0 else None,
        "added_at": datetime.now().isoformat(),
        "invite_link": chat_info.get('invite_link'),
        "notes": ""
    }
    
    data['groups'].append(new_group)
    save_groups(data)
    
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ Group added successfully!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("Use in quest configuration:")
    print(f'  "chat_id": "{new_group["chat_id"]}"')
    print()
    
    return True

def list_groups():
    """List all groups"""
    data = load_groups()
    
    if not data['groups']:
        print("📭 No groups found in telegramgroups.json")
        return
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📋 Telegram Groups ({len(data['groups'])})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    for i, group in enumerate(data['groups'], 1):
        print(f"{i}. {group['title']}")
        print(f"   Chat ID: {group['chat_id']}")
        print(f"   Type: {group['type']}")
        if group.get('username'):
            print(f"   Username: @{group['username']}")
        if group.get('member_count'):
            print(f"   Members: {group['member_count']}")
        if group.get('invite_link'):
            print(f"   Invite Link: {group['invite_link']}")
        if group.get('notes'):
            print(f"   Notes: {group['notes']}")
        print(f"   Added: {group['added_at']}")
        print()

def remove_group_interactive():
    """Remove a group interactively"""
    data = load_groups()
    
    if not data['groups']:
        print("📭 No groups to remove")
        return
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🗑️  Remove Telegram Group")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    for i, group in enumerate(data['groups'], 1):
        print(f"{i}. {group['title']} ({group['chat_id']})")
    
    print()
    choice = input("Enter number to remove (or 'c' to cancel): ").strip()
    
    if choice.lower() == 'c':
        print("❌ Cancelled")
        return
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(data['groups']):
            removed = data['groups'].pop(index)
            save_groups(data)
            print(f"✅ Removed: {removed['title']}")
        else:
            print("❌ Invalid number")
    except ValueError:
        print("❌ Invalid input")

def export_for_quests():
    """Export groups in format ready for quest creation"""
    data = load_groups()
    
    if not data['groups']:
        print("📭 No groups to export")
        return
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📤 Quest Configuration Format")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    for group in data['groups']:
        print(f"// {group['title']}")
        print("{")
        print(f'  "platform": "telegram",')
        print(f'  "task_type": "telegram_join_group",')
        print(f'  "title": "Join {group["title"]}",')
        print(f'  "description": "Join our community on Telegram",')
        if group.get('invite_link'):
            print(f'  "url": "{group["invite_link"]}",')
        elif group.get('username'):
            print(f'  "url": "https://t.me/{group["username"]}",')
        print(f'  "points_reward": 100,')
        print(f'  "verification_data": {{')
        print(f'    "chat_id": "{group["chat_id"]}",')
        print(f'    "chat_name": "{group["title"]}",')
        print(f'    "method": "api"')
        print(f'  }}')
        print("}")
        print()

def main():
    """Main function"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env")
        sys.exit(1)
    
    # Check bot connection
    bot_info = get_bot_info()
    if not bot_info:
        print("❌ Cannot connect to Telegram Bot API")
        print("   Check your TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🤖 Telegram Group Manager")
    print(f"   Bot: {bot_info.get('first_name')} (@{bot_info.get('username')})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    while True:
        print("Options:")
        print("  1. Add group")
        print("  2. List groups")
        print("  3. Remove group")
        print("  4. Export quest configs")
        print("  5. Exit")
        print()
        
        choice = input("Choose option (1-5): ").strip()
        print()
        
        if choice == '1':
            add_group_interactive()
        elif choice == '2':
            list_groups()
        elif choice == '3':
            remove_group_interactive()
        elif choice == '4':
            export_for_quests()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")
        
        print()

if __name__ == '__main__':
    main()
