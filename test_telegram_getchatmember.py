#!/usr/bin/env python3
"""
Test Telegram getChatMember API
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN not found in .env")
    sys.exit(1)

print("✅ Bot Token loaded")
print(f"Bot Token: {BOT_TOKEN[:20]}...")

# Test parameters
telegram_id = input("\n Enter Telegram User ID (e.g., 7988161711): ").strip()
chat_id = input("Enter Chat ID (e.g., @tamagowarriors or -1001234567890): ").strip()

print(f"\n🔍 Testing getChatMember...")
print(f"   User ID: {telegram_id}")
print(f"   Chat ID: {chat_id}")

# Call Telegram Bot API
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
params = {
    "chat_id": chat_id,
    "user_id": telegram_id
}

print(f"\n📡 Calling: {url}")
print(f"   Params: {params}")

try:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"   Response: {data}")
    
    if data.get('ok'):
        result = data.get('result', {})
        status = result.get('status')
        user = result.get('user', {})
        
        print(f"\n✅ API Call Successful!")
        print(f"   Status: {status}")
        print(f"   User ID: {user.get('id')}")
        print(f"   Username: @{user.get('username', 'N/A')}")
        print(f"   First Name: {user.get('first_name', 'N/A')}")
        
        # Check if valid member
        valid_statuses = ['creator', 'administrator', 'member', 'restricted']
        if status in valid_statuses:
            print(f"\n🎉 User IS a member! ({status})")
        else:
            print(f"\n❌ User is NOT a member (status: {status})")
    else:
        error_desc = data.get('description', 'Unknown error')
        print(f"\n❌ API Call Failed!")
        print(f"   Error: {error_desc}")
        print(f"\n💡 Common reasons:")
        print(f"   1. Bot is not in the group/channel")
        print(f"   2. Chat ID is incorrect")
        print(f"   3. User ID is incorrect")
        print(f"   4. Bot doesn't have admin permissions (for channels)")
        
except Exception as e:
    print(f"\n💥 Exception occurred: {str(e)}")
