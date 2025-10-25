#!/bin/bash

# Telegram Quest Diagnostic Script
# This script helps diagnose why Telegram membership verification is failing

echo "🔍 TELEGRAM QUEST DIAGNOSTIC TOOL"
echo "==================================="
echo ""

# Check .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please create a .env file with TELEGRAM_BOT_TOKEN"
    exit 1
fi

echo "✅ .env file found"

# Load .env
source .env

# Check TELEGRAM_BOT_TOKEN
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ TELEGRAM_BOT_TOKEN found: ${TELEGRAM_BOT_TOKEN:0:15}..."
echo ""

# Test bot connection
echo "📡 Testing bot connection..."
BOT_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")

if echo "$BOT_INFO" | grep -q '"ok":true'; then
    BOT_USERNAME=$(echo "$BOT_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['username'])")
    BOT_NAME=$(echo "$BOT_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['first_name'])")
    echo "✅ Bot is working!"
    echo "   Bot Name: $BOT_NAME"
    echo "   Bot Username: @$BOT_USERNAME"
else
    echo "❌ Bot connection failed!"
    echo "   Response: $BOT_INFO"
    exit 1
fi

echo ""
echo "==================================="
echo "🔧 CHECKLIST FOR TELEGRAM QUESTS"
echo "==================================="
echo ""

echo "1. ✅ Bot token is valid and working"
echo ""

echo "2. Check if bot is in your Telegram group/channel:"
echo "   • Open your Telegram group"
echo "   • Add @$BOT_USERNAME to the group"
echo "   • Make sure bot has permission to see members"
echo ""

echo "3. Get your Chat ID:"
echo "   Method 1: Use @getmyid_bot in Telegram"
echo "   • Add @getmyid_bot to your group"
echo "   • It will show the group chat ID (starts with -100...)"
echo ""
echo "   Method 2: Send a message to the group and check:"
echo "   • curl https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
echo "   • Look for \"chat\":{\"id\":...}"
echo ""

echo "4. Get user's Telegram ID:"
echo "   • User can message @userinfobot"
echo "   • Or use window.Telegram.WebApp.initDataUnsafe.user.id"
echo ""

echo "5. Test getChatMember API directly:"
echo "   Run: python3 test_telegram_getchatmember.py"
echo ""

echo "==================================="
echo "📋 COMMON ISSUES & SOLUTIONS"
echo "==================================="
echo ""

echo "❌ Error: 'Bad Request: chat not found'"
echo "   ➜ Solution: Chat ID is wrong or bot was removed from group"
echo ""

echo "❌ Error: 'Bad Request: user not found'"
echo "   ➜ Solution: User ID is wrong or user never started the bot"
echo ""

echo "❌ Error: 'Bad Request: CHAT_ADMIN_REQUIRED'"
echo "   ➜ Solution: For private channels, bot needs admin permissions"
echo ""

echo "❌ Error: 'Forbidden: bot was blocked by the user'"
echo "   ➜ Solution: User needs to /start the bot first"
echo ""

echo "❌ Status: 'left'"
echo "   ➜ Solution: User left the group, ask them to rejoin"
echo ""

echo "❌ Status: 'kicked'"
echo "   ➜ Solution: User was banned, admin needs to unban"
echo ""

echo "==================================="
echo "🧪 QUICK TEST"
echo "==================================="
echo ""

read -p "Do you want to test getChatMember now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 test_telegram_getchatmember.py
fi

echo ""
echo "==================================="
echo "📝 NEXT STEPS"
echo "==================================="
echo ""
echo "1. Ensure bot is added to your Telegram group"
echo "2. Get the correct chat_id (starts with -100...)"
echo "3. Update your Telegram quest in admin panel with correct chat_id"
echo "4. Ask user to try verification again"
echo "5. Check backend logs for detailed debug output"
echo ""
echo "If issues persist, check the backend terminal for detailed logs!"
echo ""
