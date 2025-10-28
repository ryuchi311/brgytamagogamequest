# Telegram Group Manager 🤖

## Overview

A tool to easily manage Telegram groups for Quest Hub. The bot can fetch group information and store it in `telegramgroups.json` for easy quest creation.

## Features

✅ **Add Groups** - Automatically fetch group details from Telegram  
✅ **Store Details** - Save ID, username, title, members, etc.  
✅ **List Groups** - View all registered groups  
✅ **Remove Groups** - Clean up old groups  
✅ **Export Configs** - Generate quest configurations  

## Quick Start

### Method 1: Using Shell Script (Easiest)
```bash
./manage_groups.sh
```

### Method 2: Using Python Directly
```bash
python3 manage_telegram_groups.py
```

## Usage

### 1. Add a Group

**Requirements:**
- Bot must be added to the target group
- You need the Chat ID

**Steps:**
```bash
./manage_groups.sh

# Choose option 1 (Add group)
# Enter Chat ID:
@tamagowarriors    # For public groups
# or
-1001234567890     # For private groups

# Bot will fetch:
✅ Group title
✅ Group username
✅ Group ID
✅ Member count
✅ Description
✅ Invite link
```

**Example:**
```
Enter the group Chat ID: @tamagowarriors

🔍 Fetching group information from Telegram...

✅ Group found!
   Title: Tamago Warriors
   Type: supergroup
   Username: @tamagowarriors
   ID: -1001234567890
   Members: 150
   Description: Official Tamago Warriors Community

Add this group? (y/n): y

✅ Group added successfully!

Use in quest configuration:
  "chat_id": "@tamagowarriors"
```

### 2. List All Groups

```bash
./manage_groups.sh
# Choose option 2

# Output:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Telegram Groups (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Tamago Warriors
   Chat ID: @tamagowarriors
   Type: supergroup
   Username: @tamagowarriors
   Members: 150
   Invite Link: https://t.me/tamagowarriors
   Added: 2025-10-26T00:15:00

2. VIP Member Group
   Chat ID: -1001234567890
   Type: supergroup
   Members: 50
   Added: 2025-10-26T00:20:00
```

### 3. Remove a Group

```bash
./manage_groups.sh
# Choose option 3

# Select group to remove
1. Tamago Warriors (@tamagowarriors)
2. VIP Member Group (-1001234567890)

Enter number to remove (or 'c' to cancel): 1

✅ Removed: Tamago Warriors
```

### 4. Export Quest Configurations

```bash
./manage_groups.sh
# Choose option 4

# Output ready-to-use quest configs:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📤 Quest Configuration Format
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// Tamago Warriors
{
  "platform": "telegram",
  "task_type": "telegram_join_group",
  "title": "Join Tamago Warriors",
  "description": "Join our community on Telegram",
  "url": "https://t.me/tamagowarriors",
  "points_reward": 100,
  "verification_data": {
    "chat_id": "@tamagowarriors",
    "chat_name": "Tamago Warriors",
    "method": "api"
  }
}
```

## File Structure

### telegramgroups.json

```json
{
  "groups": [
    {
      "id": -1001234567890,
      "title": "Tamago Warriors",
      "username": "tamagowarriors",
      "chat_id": "@tamagowarriors",
      "type": "supergroup",
      "description": "Official community",
      "member_count": 150,
      "added_at": "2025-10-26T00:15:00",
      "invite_link": "https://t.me/tamagowarriors",
      "notes": "Main community group"
    }
  ]
}
```

**Fields:**
- `id` - Numeric group ID
- `title` - Group name
- `username` - Username (without @) if public
- `chat_id` - Chat ID for API calls (@username or -1001234567890)
- `type` - group, supergroup, or channel
- `description` - Group description
- `member_count` - Number of members
- `added_at` - When added to this file
- `invite_link` - Invite link if available
- `notes` - Your custom notes

## How to Get Chat ID

### For Public Groups
Use the username with @ prefix:
```
@tamagowarriors
@btc_trading_group
```

### For Private Groups/Supergroups

**Method 1: Using getUpdates**
1. Add bot to group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Look for: `"chat":{"id":-1001234567890}`

**Method 2: Using Debug Script**
```bash
./debug_telegram_verification.sh
# The script will help you find the Chat ID
```

**Method 3: Using Third-party Bots**
1. Add @userinfobot to your group
2. It will show the Chat ID

## Adding Bot to Groups

**For Groups:**
1. Open Telegram group
2. Click group name → "Add Members"
3. Search for: @bt_taskerbot (or your bot username)
4. Add the bot
5. Bot appears in member list

**For Channels:**
1. Open Telegram channel
2. Click channel name → "Administrators"
3. Click "Add Administrator"
4. Search for: @bt_taskerbot
5. Give "View Messages" permission
6. Add the bot

## Use Cases

### 1. Multiple Community Groups

```json
{
  "groups": [
    {"chat_id": "@tamago_main", "title": "Main Community"},
    {"chat_id": "@tamago_vip", "title": "VIP Members"},
    {"chat_id": "@tamago_news", "title": "Announcements"},
    {"chat_id": "@tamago_trading", "title": "Trading Discussion"}
  ]
}
```

Create quests for each group with different point rewards!

### 2. Tiered Membership System

```json
{
  "groups": [
    {"chat_id": "@tamago_bronze", "title": "Bronze Tier", "points": 50},
    {"chat_id": "@tamago_silver", "title": "Silver Tier", "points": 100},
    {"chat_id": "@tamago_gold", "title": "Gold Tier", "points": 200}
  ]
}
```

### 3. Language-Specific Groups

```json
{
  "groups": [
    {"chat_id": "@tamago_english", "title": "English Community"},
    {"chat_id": "@tamago_filipino", "title": "Filipino Community"},
    {"chat_id": "@tamago_spanish", "title": "Spanish Community"}
  ]
}
```

## Creating Quests from Stored Groups

Once groups are in `telegramgroups.json`, creating quests is easy!

### Manual Method
```bash
# Export configurations
./manage_groups.sh
# Choose option 4
# Copy the JSON output
# Paste into your quest creation form or database
```

### Automated Method (Future)
```bash
# Create quests automatically from telegramgroups.json
./create_quests_from_groups.sh
```

## Troubleshooting

### Bot Can't Fetch Group Info

**Error:** `Failed to get group information`

**Causes:**
1. Bot not in the group
2. Wrong Chat ID format
3. Bot lacks permissions

**Solutions:**
```bash
# 1. Verify bot is in group
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChat?chat_id=@tamagowarriors"

# 2. Test with debug script
./debug_telegram_verification.sh

# 3. Check bot permissions
# Open group → Members → Find bot → Check permissions
```

### Group Already Exists

**Message:** `Group already exists in telegramgroups.json`

**Options:**
- Update: Updates the group information
- Cancel: Keeps existing information

### Invalid Chat ID

**Error:** `Chat not found`

**Solutions:**
- Public groups: Must use `@username` format
- Private groups: Must use numeric ID `-1001234567890`
- Supergroups: ID starts with `-100`
- Regular groups: ID starts with `-`

## File Management

### Backup
```bash
# Create backup before making changes
cp telegramgroups.json telegramgroups.backup.json
```

### Reset
```bash
# Start fresh
rm telegramgroups.json
# File will be recreated when you add first group
```

### Manual Edit
```bash
# Edit directly
nano telegramgroups.json
# or
code telegramgroups.json
```

## Integration with Quest Creation

### In Admin Panel (Future)
1. Go to "Create Quest"
2. Select "Telegram Join Group"
3. Dropdown shows groups from `telegramgroups.json`
4. Auto-fills chat_id, title, invite link
5. You just set the points and description!

### In Database
```sql
-- Example insert using stored group data
INSERT INTO tasks (
  platform, 
  task_type, 
  title, 
  url, 
  points_reward, 
  verification_data
) VALUES (
  'telegram',
  'telegram_join_group',
  'Join Tamago Warriors',
  'https://t.me/tamagowarriors',
  100,
  '{"chat_id": "@tamagowarriors", "chat_name": "Tamago Warriors", "method": "api"}'
);
```

## Best Practices

1. **Add Notes** - Use the `notes` field to remember group purpose
2. **Keep Updated** - Re-run add command to update member counts
3. **Backup** - Keep backup of `telegramgroups.json`
4. **Document** - Add notes about point rewards, tier levels
5. **Organize** - Group similar communities together

## Example Workflows

### Daily Admin Workflow
```bash
# Morning: Check all groups
./manage_groups.sh
# Choose "2. List groups"
# Review member counts

# Add new community group
./manage_groups.sh
# Choose "1. Add group"
# Enter @new_group_name

# Export configs for quest creation
./manage_groups.sh
# Choose "4. Export quest configs"
```

### Quest Creation Workflow
```bash
# 1. List available groups
./manage_groups.sh
# Choose 2

# 2. Export quest configurations
./manage_groups.sh
# Choose 4

# 3. Copy the JSON
# 4. Create quest in admin panel or database
# 5. Test verification works
./debug_telegram_verification.sh
```

## Commands Reference

```bash
# Start manager
./manage_groups.sh

# View stored groups
cat telegramgroups.json | jq '.'

# Count groups
cat telegramgroups.json | jq '.groups | length'

# Find specific group
cat telegramgroups.json | jq '.groups[] | select(.title | contains("Tamago"))'

# Get all chat_ids
cat telegramgroups.json | jq '.groups[].chat_id'
```

## Summary

✅ Easy group management with `./manage_groups.sh`  
✅ Automatic information fetching from Telegram  
✅ Stored in `telegramgroups.json`  
✅ Export quest configurations instantly  
✅ No manual typing of IDs  
✅ Keep track of all community groups  
✅ Update information anytime  

**Managing Telegram groups is now effortless! 🚀**

## Files

- `manage_telegram_groups.py` - Main Python script
- `manage_groups.sh` - Easy shell wrapper
- `telegramgroups.json` - Stores all group data
- `telegramgroups.example.json` - Example file structure

## Quick Commands

```bash
# Add a group
./manage_groups.sh → 1

# List groups
./manage_groups.sh → 2

# Export for quests
./manage_groups.sh → 4

# Remove group
./manage_groups.sh → 3
```

**Start managing your Telegram groups now!** 🎯
