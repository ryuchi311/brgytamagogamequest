#!/bin/bash

# Test Telegram Group Announcement Feature
# This script helps you test if the bot can send announcements to your group

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Telegram Group Announcement - Test Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment variables
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ Bot Token loaded: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo ""

# Get bot info
echo "📡 Getting bot information..."
BOT_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
BOT_OK=$(echo $BOT_INFO | jq -r '.ok')

if [ "$BOT_OK" = "true" ]; then
    BOT_NAME=$(echo $BOT_INFO | jq -r '.result.first_name')
    BOT_USERNAME=$(echo $BOT_INFO | jq -r '.result.username')
    echo "✅ Bot: $BOT_NAME (@$BOT_USERNAME)"
else
    echo "❌ Failed to get bot info"
    echo "$BOT_INFO"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Setup Instructions:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Add @$BOT_USERNAME to your Telegram group"
echo "2. Make sure the bot has permission to send messages"
echo "3. Get your group's Chat ID"
echo ""
echo "To get Chat ID:"
echo "  - Send a message to your group"
echo "  - Visit: https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN:0:20}.../getUpdates"
echo "  - Look for 'chat':{'id': -1001234567890}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Prompt for chat ID
read -p "Enter your group Chat ID (e.g., -1001234567890 or @username): " CHAT_ID

if [ -z "$CHAT_ID" ]; then
    echo "❌ Chat ID cannot be empty"
    exit 1
fi

echo ""
echo "🧪 Testing announcement in: $CHAT_ID"
echo ""

# Test message
TEST_MESSAGE="🎉 **Test Announcement**

✅ John Doe (@johndoe) has successfully verified and joined the **Brgy Tamago Quest Hub**!

🎮 Congratulations and welcome to the community! 🚀
💎 Points earned: 100

_This is a test message. The bot is working correctly!_"

# Send test announcement
echo "📤 Sending test announcement..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "{
        \"chat_id\": \"$CHAT_ID\",
        \"text\": \"$TEST_MESSAGE\",
        \"parse_mode\": \"Markdown\"
    }")

# Check response
SUCCESS=$(echo $RESPONSE | jq -r '.ok')

echo ""
if [ "$SUCCESS" = "true" ]; then
    MESSAGE_ID=$(echo $RESPONSE | jq -r '.result.message_id')
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ SUCCESS! Test announcement sent!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "✅ Message ID: $MESSAGE_ID"
    echo "✅ Check your Telegram group for the test message"
    echo ""
    echo "🎉 Your bot can now send announcements when users join!"
    echo ""
    echo "Next steps:"
    echo "1. Create a Telegram quest in your Quest Hub"
    echo "2. Set the chat_id to: $CHAT_ID"
    echo "3. When users complete the quest, they'll get an announcement!"
else
    ERROR_CODE=$(echo $RESPONSE | jq -r '.error_code')
    ERROR_DESC=$(echo $RESPONSE | jq -r '.description')
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ FAILED to send announcement"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Error Code: $ERROR_CODE"
    echo "Error: $ERROR_DESC"
    echo ""
    echo "Common issues:"
    echo ""
    echo "1. 'Chat not found' or 'Bot was blocked by the user'"
    echo "   → Add @$BOT_USERNAME to your group first"
    echo ""
    echo "2. 'Bot is not a member of the group'"
    echo "   → Make sure the bot is in the group"
    echo ""
    echo "3. 'Not enough rights to send messages'"
    echo "   → Give the bot permission to send messages"
    echo ""
    echo "4. 'Chat_id is invalid'"
    echo "   → Double-check your Chat ID format"
    echo "   → Use -100 prefix for supergroups"
    echo "   → Or use @username for public groups"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
