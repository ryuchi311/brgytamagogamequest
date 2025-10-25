#!/usr/bin/env python3
"""
Complete Telegram Quest Verification Test
Tests the actual quest from database to verify why it's failing
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Supabase
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Installing supabase package...")
    os.system("pip install supabase -q")
    from supabase import create_client, Client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not all([SUPABASE_URL, SUPABASE_KEY, BOT_TOKEN]):
    print("❌ Missing environment variables!")
    print(f"   SUPABASE_URL: {'✅' if SUPABASE_URL else '❌'}")
    print(f"   SUPABASE_KEY: {'✅' if SUPABASE_KEY else '❌'}")
    print(f"   TELEGRAM_BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
    sys.exit(1)

print("✅ Environment variables loaded")
print(f"   Supabase URL: {SUPABASE_URL}")
print(f"   Bot Token: {BOT_TOKEN[:20]}...")
print()

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected to Supabase")
print()

# Get all Telegram quests
print("📋 Fetching Telegram quests from database...")
try:
    response = supabase.table("tasks").select("*").or_(
        "task_type.eq.telegram,task_type.like.telegram_%,platform.eq.telegram"
    ).execute()
    
    quests = response.data
    print(f"✅ Found {len(quests)} Telegram quest(s)")
    print()
    
    if not quests:
        print("❌ No Telegram quests found in database!")
        print("   Create a Telegram quest in the admin panel first.")
        sys.exit(1)
    
    # Display quests
    for i, quest in enumerate(quests, 1):
        print(f"{'='*60}")
        print(f"Quest #{i}: {quest.get('title')}")
        print(f"{'='*60}")
        print(f"   ID: {quest.get('id')}")
        print(f"   Task Type: {quest.get('task_type')}")
        print(f"   Platform: {quest.get('platform')}")
        print(f"   Points: {quest.get('points_reward')}")
        print(f"   Active: {quest.get('is_active')}")
        print(f"   URL: {quest.get('url')}")
        print(f"   Verification Data: {quest.get('verification_data')}")
        
        # Check verification_data
        verification_data = quest.get('verification_data') or {}
        chat_id = verification_data.get('chat_id')
        chat_name = verification_data.get('chat_name')
        method = verification_data.get('method')
        
        print()
        print(f"   Verification Config:")
        print(f"      Method: {method or 'NOT SET ❌'}")
        print(f"      Chat ID: {chat_id or 'NOT SET ❌'}")
        print(f"      Chat Name: {chat_name or 'NOT SET ❌'}")
        print()
        
        # Test this quest
        if chat_id:
            print(f"🧪 Testing Quest: {quest.get('title')}")
            print(f"   Chat ID: {chat_id}")
            
            # Get test user ID
            test_user_id = input(f"\n   Enter Telegram User ID to test (or press Enter to skip): ").strip()
            
            if test_user_id:
                print(f"\n   Testing user {test_user_id} in chat {chat_id}...")
                
                # Call Telegram Bot API
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
                params = {
                    "chat_id": chat_id,
                    "user_id": test_user_id
                }
                
                try:
                    api_response = requests.get(url, params=params, timeout=10)
                    data = api_response.json()
                    
                    print(f"\n   📡 API Response:")
                    print(f"      Status Code: {api_response.status_code}")
                    print(f"      OK: {data.get('ok')}")
                    
                    if data.get('ok'):
                        result = data.get('result', {})
                        status = result.get('status')
                        user = result.get('user', {})
                        
                        print(f"      User Status: {status}")
                        print(f"      User ID: {user.get('id')}")
                        print(f"      Username: @{user.get('username', 'N/A')}")
                        print(f"      First Name: {user.get('first_name', 'N/A')}")
                        
                        # Check if member
                        valid_statuses = ['creator', 'administrator', 'member', 'restricted']
                        if status in valid_statuses:
                            print(f"\n   ✅ SUCCESS! User IS a member ({status})")
                            print(f"      This quest SHOULD work for user {test_user_id}")
                        else:
                            print(f"\n   ❌ FAILED! User is NOT a member (status: {status})")
                            print(f"      User needs to join the group first")
                    else:
                        error_desc = data.get('description', 'Unknown error')
                        error_code = data.get('error_code')
                        print(f"      Error Code: {error_code}")
                        print(f"      Error: {error_desc}")
                        
                        print(f"\n   ❌ API call failed!")
                        print(f"\n   💡 Possible issues:")
                        
                        if 'chat not found' in error_desc.lower():
                            print(f"      • Bot is not in the group/channel")
                            print(f"      • Chat ID '{chat_id}' is incorrect")
                            print(f"      • Bot was removed from the group")
                        elif 'user not found' in error_desc.lower():
                            print(f"      • User ID '{test_user_id}' is incorrect")
                            print(f"      • User has never started the bot")
                        elif 'admin required' in error_desc.lower():
                            print(f"      • Bot needs admin permissions (for channels)")
                        
                except Exception as e:
                    print(f"\n   💥 Exception: {str(e)}")
            
            print()
        else:
            print(f"   ⚠️  WARNING: No chat_id configured for this quest!")
            print(f"      Edit the quest in admin panel and set the chat_id")
            print()
    
except Exception as e:
    print(f"❌ Error fetching quests: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("="*60)
print("🔧 TROUBLESHOOTING STEPS")
print("="*60)
print()
print("If verification is still failing:")
print()
print("1. Check Backend Logs:")
print("   • Restart backend: uvicorn app.api:app --reload")
print("   • Look for detailed debug output")
print()
print("2. Verify Quest Configuration:")
print("   • Open admin panel")
print("   • Edit Telegram quest")
print("   • Ensure chat_id is set correctly")
print("   • Save and try again")
print()
print("3. Verify Bot is in Group:")
print("   • Open Telegram group")
print("   • Ensure @bt_taskerbot is a member")
print("   • Bot should appear in member list")
print()
print("4. Test with Different User:")
print("   • Ask another group member to test")
print("   • Verify their Telegram ID is correct")
print()
print("5. Check Browser Console:")
print("   • Open DevTools (F12)")
print("   • Look for error messages")
print("   • Check network tab for API responses")
print()
