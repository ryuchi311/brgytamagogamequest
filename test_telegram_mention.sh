#!/bin/bash

# Test Telegram User Mention/Tag Feature
# Verifies that bot can mention users in group announcements

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔔 Telegram User Mention Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment
source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

echo "✅ Bot Token loaded"
echo ""

# Get inputs
read -p "Enter Group Chat ID (e.g., @tamagowarriors): " CHAT_ID
read -p "Enter User's Telegram ID (numeric): " USER_ID
read -p "Enter User's First Name: " FIRST_NAME
read -p "Enter Quest Title: " QUEST_TITLE
read -p "Enter Points Reward: " POINTS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Sending test announcement with user mention..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Build message with user mention (tg://user?id=USER_ID format)
MESSAGE="🎉 **New Member Verified!**

✅ [$FIRST_NAME](tg://user?id=$USER_ID) has successfully completed the quest!

📍 Group: **Brgy Tamago Warriors**
🎮 Quest: **$QUEST_TITLE**
💎 Points earned: **$POINTS XP**

🎊 Welcome to the community! 🚀"

# URL encode the message
ENCODED_MESSAGE=$(echo "$MESSAGE" | jq -sRr @uri)

# Send via Telegram API
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{
    \"chat_id\": \"$CHAT_ID\",
    \"text\": $(echo "$MESSAGE" | jq -Rs .),
    \"parse_mode\": \"Markdown\"
  }")

echo "📡 API Response:"
echo "$RESPONSE" | jq '.'
echo ""

# Check result
OK=$(echo "$RESPONSE" | jq -r '.ok')

if [ "$OK" == "true" ]; then
    MESSAGE_ID=$(echo "$RESPONSE" | jq -r '.result.message_id')
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ SUCCESS!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Message ID: $MESSAGE_ID"
    echo "Chat: $CHAT_ID"
    echo ""
    echo "The user should be mentioned/tagged in the group message!"
    echo "They will receive a notification about being mentioned."
    echo ""
else
    ERROR=$(echo "$RESPONSE" | jq -r '.description')
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ FAILED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Error: $ERROR"
    echo ""
    echo "Common issues:"
    echo "  • Bot not in the group"
    echo "  • Wrong chat_id format"
    echo "  • Bot doesn't have permission to send messages"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "How User Mentions Work:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Format: [Display Name](tg://user?id=USER_ID)"
echo ""
echo "Benefits:"
echo "  ✅ Creates clickable mention"
echo "  ✅ User gets notification"
echo "  ✅ Works even without username"
echo "  ✅ Opens user's profile when clicked"
echo ""
echo "The updated code now mentions users in the specific group"
echo "where they verified their membership!"
echo ""
