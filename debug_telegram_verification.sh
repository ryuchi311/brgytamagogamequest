#!/bin/bash

# Telegram Verification Debug - Real-time Test
# This helps diagnose why verification might be failing

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Telegram Verification Debugger"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment
source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

echo "✅ Bot Token: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo ""

# Get bot info
echo "🤖 Getting bot information..."
BOT_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
BOT_USERNAME=$(echo $BOT_INFO | jq -r '.result.username')
echo "✅ Bot: @$BOT_USERNAME"
echo ""

# Prompt for inputs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Please provide the following information:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Enter the Group Chat ID (e.g., @tamagowarriors or -1001234567890): " CHAT_ID
read -p "Enter the User's Telegram ID (numeric, e.g., 7988161711): " USER_ID

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing getChatMember API..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Chat ID: $CHAT_ID"
echo "User ID: $USER_ID"
echo ""

# Test getChatMember
RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChatMember?chat_id=${CHAT_ID}&user_id=${USER_ID}")

echo "📡 API Response:"
echo "$RESPONSE" | jq '.'
echo ""

# Parse response
OK=$(echo $RESPONSE | jq -r '.ok')

if [ "$OK" = "true" ]; then
    STATUS=$(echo $RESPONSE | jq -r '.result.status')
    USER_NAME=$(echo $RESPONSE | jq -r '.result.user.first_name')
    USERNAME=$(echo $RESPONSE | jq -r '.result.user.username')
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ API Call Successful"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "👤 User: $USER_NAME (@$USERNAME)"
    echo "📊 Status: $STATUS"
    echo ""
    
    case $STATUS in
        "creator")
            echo "✅ User is the GROUP CREATOR"
            echo "✅ Verification should PASS"
            ;;
        "administrator")
            echo "✅ User is a GROUP ADMIN"
            echo "✅ Verification should PASS"
            ;;
        "member")
            echo "✅ User is a GROUP MEMBER"
            echo "✅ Verification should PASS"
            ;;
        "restricted")
            echo "⚠️  User is RESTRICTED but still in group"
            echo "✅ Verification should PASS"
            ;;
        "left")
            echo "❌ User has LEFT the group"
            echo "❌ Verification should FAIL"
            echo ""
            echo "Solution: User needs to join the group first"
            ;;
        "kicked")
            echo "❌ User was KICKED/BANNED from group"
            echo "❌ Verification should FAIL"
            echo ""
            echo "Solution: Admin needs to unban user, then user can rejoin"
            ;;
        *)
            echo "❓ Unknown status: $STATUS"
            ;;
    esac
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Backend Code Check:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Valid statuses for verification:"
    echo "  • creator ✅"
    echo "  • administrator ✅"
    echo "  • member ✅"
    echo "  • restricted ✅"
    echo ""
    
    if [[ "$STATUS" =~ ^(creator|administrator|member|restricted)$ ]]; then
        echo "✅ This user's status ($STATUS) should PASS verification"
    else
        echo "❌ This user's status ($STATUS) will FAIL verification"
    fi
    
else
    ERROR_CODE=$(echo $RESPONSE | jq -r '.error_code')
    ERROR_DESC=$(echo $RESPONSE | jq -r '.description')
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ API Call Failed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Error Code: $ERROR_CODE"
    echo "Error: $ERROR_DESC"
    echo ""
    
    case $ERROR_CODE in
        400)
            echo "Common causes:"
            echo "  1. Invalid chat_id format"
            echo "  2. Invalid user_id format"
            echo ""
            echo "Solutions:"
            echo "  • For public groups: Use @groupusername"
            echo "  • For private groups: Use -1001234567890"
            echo "  • For supergroups: Must start with -100"
            echo "  • User ID must be numeric only"
            ;;
        403)
            echo "Common causes:"
            echo "  1. Bot is not in the group"
            echo "  2. Bot doesn't have permission to see members"
            echo ""
            echo "Solutions:"
            echo "  • Add @$BOT_USERNAME to the group"
            echo "  • Give bot 'Read Messages' permission"
            ;;
        404)
            echo "Common causes:"
            echo "  1. Chat/group not found"
            echo "  2. Wrong chat_id"
            echo ""
            echo "Solutions:"
            echo "  • Double-check the chat_id"
            echo "  • Make sure bot is in the group"
            ;;
        *)
            echo "See: https://core.telegram.org/bots/api#error-codes"
            ;;
    esac
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Troubleshooting Tips:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If verification is failing in the app:"
echo ""
echo "1. Check backend logs:"
echo "   tail -f backend.log | grep 'Telegram Verification'"
echo ""
echo "2. Verify chat_id in database:"
echo "   SELECT id, title, verification_data FROM tasks WHERE platform='telegram';"
echo ""
echo "3. Test with this script using the exact same:"
echo "   • chat_id from the quest"
echo "   • user_id from Telegram (should match telegram_id in users table)"
echo ""
echo "4. Common issues:"
echo "   • chat_id format wrong (@username vs -1001234567890)"
echo "   • Bot not added to the group"
echo "   • User hasn't actually joined yet"
echo "   • User joined but then left"
echo ""
echo "5. If test passes but app fails:"
echo "   • Check if correct telegram_id is being sent"
echo "   • Verify verification_data in quest has correct chat_id"
echo "   • Check backend logs for exact error message"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
