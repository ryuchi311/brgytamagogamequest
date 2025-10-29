#!/bin/bash

# Test Script for Telegram Username Verification Feature
# This script tests the new username input modal and verification flow

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Telegram Username Verification - Test Suite                ║"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

# Check required variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ Environment loaded"
echo ""

# Function to test API endpoint
test_username_verification() {
    local telegram_id=$1
    local task_id=$2
    local username=$3
    local test_name=$4
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 Test: $test_name"
    echo "   Telegram ID: $telegram_id"
    echo "   Username: @$username"
    echo "   Task ID: $task_id"
    echo ""
    
    response=$(curl -s -X POST http://localhost:8000/complete-task \
        -H "Content-Type: application/json" \
        -d "{
            \"telegram_id\": \"$telegram_id\",
            \"task_id\": $task_id,
            \"telegram_username\": \"$username\"
        }")
    
    echo "📥 Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo ""
}

# Function to check if services are running
check_services() {
    echo "🔍 Checking if services are running..."
    echo ""
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is running (port 8000)"
    else
        echo "❌ Backend API is NOT running!"
        echo "   Run: ./start.sh"
        return 1
    fi
    
    # Check frontend
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "✅ Frontend is running (port 8080)"
    else
        echo "⚠️  Frontend might not be running (port 8080)"
    fi
    
    echo ""
    return 0
}

# Function to display manual testing instructions
show_manual_test_instructions() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   Manual Testing Instructions                                 ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "1️⃣  Open the Quest Hub:"
    echo "   → http://localhost:8080"
    echo ""
    echo "2️⃣  Login with a test Telegram account"
    echo ""
    echo "3️⃣  Select a Telegram Group quest"
    echo ""
    echo "4️⃣  Click 'Join Now' button"
    echo "   → Opens Telegram group link"
    echo ""
    echo "5️⃣  Join the group in Telegram"
    echo ""
    echo "6️⃣  Return to Quest Hub and click 'Verify Me'"
    echo "   → Modal should appear! ✨"
    echo ""
    echo "7️⃣  Enter your Telegram username in the modal"
    echo "   (with or without @ symbol)"
    echo ""
    echo "8️⃣  Click 'Verify' button"
    echo ""
    echo "9️⃣  Expected behaviors:"
    echo ""
    echo "   ✅ SUCCESS CASE:"
    echo "      - Username matches your Telegram username"
    echo "      - You're a member of the group"
    echo "      - Modal closes"
    echo "      - Success message appears"
    echo "      - Points awarded"
    echo "      - Bot announces in group with mention"
    echo ""
    echo "   ❌ ERROR CASES:"
    echo "      - Wrong username: 'Username mismatch! You entered @wrong but"
    echo "        your Telegram username is @correct'"
    echo "      - No username set: 'You don't have a Telegram username set!'"
    echo "      - Not a member: 'You are not a member of the group'"
    echo "      - Empty username: 'Please enter your Telegram username'"
    echo ""
}

# Function to test modal UI elements
test_modal_elements() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   Modal UI Elements Checklist                                 ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Check these elements in the browser:"
    echo ""
    echo "□ Modal appears when 'Verify Me' is clicked"
    echo "□ Modal has gaming-themed design (gradient, neon colors)"
    echo "□ Modal shows title: '🔐 Telegram Verification'"
    echo "□ Info box explains why username is needed"
    echo "□ Input field has @ symbol prefix (visual only)"
    echo "□ Input field placeholder says 'username'"
    echo "□ Helper text: 'Enter without @ symbol'"
    echo "□ Cancel button works (closes modal)"
    echo "□ Verify button is disabled when input is empty"
    echo "□ Verify button shows loading state (⏳ Verifying...)"
    echo "□ Error messages appear in modal (not alerts)"
    echo "□ Success closes modal automatically"
    echo "□ Modal is above task detail modal (z-index)"
    echo "□ Modal is responsive on mobile"
    echo "□ Enter key submits the form"
    echo "□ Focus automatically on input when modal opens"
    echo ""
}

# Function to run automated API tests
run_api_tests() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   Automated API Tests                                         ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Test 1: Missing username
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 Test 1: Empty Username Validation"
    echo ""
    
    response=$(curl -s -X POST http://localhost:8000/complete-task \
        -H "Content-Type: application/json" \
        -d '{
            "telegram_id": "123456789",
            "task_id": 1,
            "telegram_username": ""
        }')
    
    echo "📥 Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    
    if echo "$response" | grep -q "Please provide your Telegram username"; then
        echo "✅ PASS: Empty username rejected"
    else
        echo "❌ FAIL: Should reject empty username"
    fi
    echo ""
    
    # Test 2: Username with @ symbol
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧪 Test 2: Username with @ Symbol Stripping"
    echo "   Testing that @username is converted to username"
    echo ""
    
    # This will fail verification but should show @ was stripped
    response=$(curl -s -X POST http://localhost:8000/complete-task \
        -H "Content-Type: application/json" \
        -d '{
            "telegram_id": "999999999",
            "task_id": 1,
            "telegram_username": "@testuser"
        }')
    
    echo "📥 Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo "✅ Check backend logs to verify @ was stripped"
    echo ""
    
    # Test 3: Real user test (if available)
    if [ -f users.json ]; then
        first_user=$(python3 -c "import json; data=json.load(open('users.json')); print(data['users'][0]['telegram_id'] if data['users'] else '')" 2>/dev/null)
        first_username=$(python3 -c "import json; data=json.load(open('users.json')); print(data['users'][0].get('username', '') if data['users'] else '')" 2>/dev/null)
        
        if [ -n "$first_user" ] && [ -n "$first_username" ]; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🧪 Test 3: Real User Verification"
            echo "   Using user from users.json"
            echo ""
            
            test_username_verification "$first_user" 1 "$first_username" "Real User Test"
        fi
    fi
}

# Main menu
main_menu() {
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║   What would you like to test?                                ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "1) Run automated API tests"
    echo "2) Show manual testing instructions"
    echo "3) Show modal UI checklist"
    echo "4) Test specific user (interactive)"
    echo "5) View backend logs (real-time)"
    echo "6) Run all tests"
    echo "0) Exit"
    echo ""
    read -p "Enter choice: " choice
    
    case $choice in
        1)
            check_services && run_api_tests
            ;;
        2)
            show_manual_test_instructions
            ;;
        3)
            test_modal_elements
            ;;
        4)
            read -p "Enter Telegram ID: " tid
            read -p "Enter Username: " uname
            read -p "Enter Task ID: " taskid
            check_services && test_username_verification "$tid" "$taskid" "$uname" "Interactive Test"
            ;;
        5)
            echo "📜 Watching backend logs (Ctrl+C to stop)..."
            echo ""
            docker-compose logs -f backend 2>/dev/null || tail -f nohup.out
            ;;
        6)
            check_services
            run_api_tests
            echo ""
            show_manual_test_instructions
            echo ""
            test_modal_elements
            ;;
        0)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            ;;
    esac
    
    echo ""
    echo "Press Enter to return to menu..."
    read
    main_menu
}

# Check services first
if ! check_services; then
    echo ""
    echo "⚠️  Please start the services first:"
    echo "   ./start.sh"
    echo ""
    exit 1
fi

# Start menu
main_menu
