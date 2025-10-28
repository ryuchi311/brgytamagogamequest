#!/bin/bash

# Telegram Membership Verification Tester
# Helps diagnose "not yet a member" issues

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Telegram Membership Verification Tester"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Load environment
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
echo "🤖 Checking bot information..."
BOT_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe")
BOT_OK=$(echo $BOT_INFO | jq -r '.ok')

if [ "$BOT_OK" != "true" ]; then
    echo "❌ Bot token is invalid!"
    echo "Response: $BOT_INFO"
    exit 1
fi

BOT_USERNAME=$(echo $BOT_INFO | jq -r '.result.username')
BOT_ID=$(echo $BOT_INFO | jq -r '.result.id')
echo "✅ Bot: @$BOT_USERNAME (ID: $BOT_ID)"
echo ""

# Method 1: Get from task ID
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Choose verification method:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Test by Task ID (gets chat_id from database)"
echo "2. Test manually (enter chat_id and user_id)"
echo ""
read -p "Enter choice (1 or 2): " METHOD

if [ "$METHOD" == "1" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Fetching tasks from API..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TASKS=$(curl -s "http://localhost:8000/api/tasks")
    
    # Display telegram_group tasks
    echo ""
    echo "Available Telegram Group Quests:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$TASKS" | jq -r '.[] | select(.task_type == "telegram_group") | "\(.id). \(.title) - Chat ID: \(.verification_data.chat_id // "N/A")"'
    echo ""
    
    read -p "Enter Task ID: " TASK_ID
    read -p "Enter User Telegram ID: " USER_ID
    
    # Get task details
    TASK=$(echo "$TASKS" | jq ".[] | select(.id == $TASK_ID)")
    CHAT_ID=$(echo "$TASK" | jq -r '.verification_data.chat_id')
    CHAT_NAME=$(echo "$TASK" | jq -r '.verification_data.chat_name // "Unknown"')
    
    if [ "$CHAT_ID" == "null" ] || [ -z "$CHAT_ID" ]; then
        echo "❌ Chat ID not found in task verification_data!"
        echo "Task data: $TASK"
        exit 1
    fi
    
else
    echo ""
    read -p "Enter Group Chat ID (e.g., @username or -1001234567890): " CHAT_ID
    read -p "Enter User's Telegram ID (numeric): " USER_ID
    CHAT_NAME="the group"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Configuration:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Chat ID: $CHAT_ID"
echo "Chat Name: $CHAT_NAME"
echo "User ID: $USER_ID"
echo ""

# Step 1: Check if chat exists
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Verifying chat exists and bot has access..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

CHAT_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChat?chat_id=${CHAT_ID}")
CHAT_OK=$(echo $CHAT_INFO | jq -r '.ok')

if [ "$CHAT_OK" == "true" ]; then
    CHAT_TITLE=$(echo $CHAT_INFO | jq -r '.result.title')
    CHAT_TYPE=$(echo $CHAT_INFO | jq -r '.result.type')
    CHAT_USERNAME=$(echo $CHAT_INFO | jq -r '.result.username // "N/A"')
    echo "✅ Chat found!"
    echo "   Title: $CHAT_TITLE"
    echo "   Type: $CHAT_TYPE"
    echo "   Username: @$CHAT_USERNAME"
else
    ERROR_DESC=$(echo $CHAT_INFO | jq -r '.description')
    echo "❌ Cannot access chat!"
    echo "   Error: $ERROR_DESC"
    echo ""
    echo "💡 Possible reasons:"
    echo "   1. Bot is not added to the group/channel"
    echo "   2. Chat ID is incorrect"
    echo "   3. For channels, bot needs admin privileges"
    echo ""
    echo "🔧 Solutions:"
    echo "   1. Add @$BOT_USERNAME to the group/channel"
    echo "   2. Verify the chat_id in quest verification_data"
    echo "   3. If it's a channel, make the bot an admin"
    exit 1
fi

echo ""

# Step 2: Check bot membership
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Checking if bot is a member..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

BOT_MEMBER=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChatMember?chat_id=${CHAT_ID}&user_id=${BOT_ID}")
BOT_MEMBER_OK=$(echo $BOT_MEMBER | jq -r '.ok')

if [ "$BOT_MEMBER_OK" == "true" ]; then
    BOT_STATUS=$(echo $BOT_MEMBER | jq -r '.result.status')
    echo "✅ Bot is a member!"
    echo "   Status: $BOT_STATUS"
else
    echo "❌ Bot is not a member!"
    echo "   Add @$BOT_USERNAME to the group first"
    exit 1
fi

echo ""

# Step 3: Check user membership
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Checking user membership..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

USER_MEMBER=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getChatMember?chat_id=${CHAT_ID}&user_id=${USER_ID}")

echo "📡 Full API Response:"
echo "$USER_MEMBER" | jq '.'
echo ""

USER_OK=$(echo $USER_MEMBER | jq -r '.ok')

if [ "$USER_OK" == "true" ]; then
    USER_STATUS=$(echo $USER_MEMBER | jq -r '.result.status')
    USER_FIRST_NAME=$(echo $USER_MEMBER | jq -r '.result.user.first_name')
    USER_USERNAME=$(echo $USER_MEMBER | jq -r '.result.user.username // "N/A"')
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Results:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "User: $USER_FIRST_NAME (@$USER_USERNAME)"
    echo "Status: $USER_STATUS"
    echo ""
    
    case $USER_STATUS in
        "creator"|"administrator"|"member"|"restricted")
            echo "✅ VERIFICATION SHOULD PASS"
            echo "   User is a valid member with status: $USER_STATUS"
            ;;
        "left")
            echo "❌ VERIFICATION WILL FAIL"
            echo "   User has left the group"
            echo "   → User needs to rejoin $CHAT_NAME"
            ;;
        "kicked")
            echo "❌ VERIFICATION WILL FAIL"
            echo "   User has been banned from the group"
            echo "   → User needs to be unbanned first"
            ;;
        *)
            echo "⚠️  UNKNOWN STATUS: $USER_STATUS"
            echo "   This might cause verification issues"
            ;;
    esac
else
    ERROR_CODE=$(echo $USER_MEMBER | jq -r '.error_code')
    ERROR_DESC=$(echo $USER_MEMBER | jq -r '.description')
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ API ERROR"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Error Code: $ERROR_CODE"
    echo "Description: $ERROR_DESC"
    echo ""
    
    case $ERROR_CODE in
        400)
            echo "💡 This usually means:"
            echo "   - Chat ID format is wrong"
            echo "   - User ID is incorrect"
            echo "   - Bot lacks permission to check members"
            ;;
        403)
            echo "💡 This means bot is not in the group!"
            echo "   Solution: Add @$BOT_USERNAME to $CHAT_NAME"
            ;;
        *)
            echo "💡 Unexpected error occurred"
            ;;
    esac
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Debugging Tips:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Verify Chat ID format:"
echo "   - Public group: @username"
echo "   - Private group: -1001234567890 (starts with -100)"
echo "   - Supergroup: -1234567890 (negative number)"
echo ""
echo "2. Get correct Chat ID:"
echo "   - Forward message from group to @userinfobot"
echo "   - Or use @RawDataBot in the group"
echo ""
echo "3. Get user's Telegram ID:"
echo "   - User sends /start to @userinfobot"
echo "   - Or check in your database"
echo ""
echo "4. Common issues:"
echo "   - User has privacy settings preventing bot from seeing membership"
echo "   - Bot was removed from the group"
echo "   - Wrong chat_id stored in verification_data"
echo "   - User actually hasn't joined yet"
echo ""
