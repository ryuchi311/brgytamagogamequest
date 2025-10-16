#!/usr/bin/env python3
"""
Test Telegram quest creation and verification
"""
import requests
import json

API_URL = "http://localhost/api"

def test_admin_login():
    """Test admin login"""
    print("🔐 Logging in as admin...")
    response = requests.post(f"{API_URL}/auth/login", json={
        "username": "admin",
        "password": "changeme123"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_create_telegram_join_group_quest(token):
    """Create a Telegram join group quest"""
    print("\n✈️ Creating Telegram JOIN GROUP quest...")
    
    quest_data = {
        "title": "Join Our Telegram Community",
        "description": "Join our official Telegram group to stay updated with the latest news and connect with other members!",
        "task_type": "telegram_join_group",
        "platform": "telegram",
        "url": "https://t.me/yourgroupname",
        "points_reward": 50,
        "is_active": True,
        "verification_required": True,
        "verification_data": {
            "method": "telegram_membership",
            "type": "join_group",
            "chat_id": "@yourgroupname",  # or numeric ID like -1001234567890
            "chat_name": "Official Community Group",
            "invite_link": "https://t.me/yourgroupname"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{API_URL}/tasks", headers=headers, json=quest_data)
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Telegram GROUP quest created successfully!")
        print(f"   ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Points: +{task['points_reward']} XP")
        print(f"   Type: {task['task_type']}")
        return task['id']
    else:
        print(f"❌ Failed to create quest: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_create_telegram_join_channel_quest(token):
    """Create a Telegram join channel quest"""
    print("\n✈️ Creating Telegram SUBSCRIBE CHANNEL quest...")
    
    quest_data = {
        "title": "Subscribe to Our Telegram Channel",
        "description": "Subscribe to our official Telegram channel for announcements and updates!",
        "task_type": "telegram_join_channel",
        "platform": "telegram",
        "url": "https://t.me/yourchannelname",
        "points_reward": 30,
        "is_active": True,
        "verification_required": True,
        "verification_data": {
            "method": "telegram_membership",
            "type": "join_channel",
            "chat_id": "@yourchannelname",  # or numeric ID
            "chat_name": "Official Announcement Channel",
            "invite_link": "https://t.me/yourchannelname"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{API_URL}/tasks", headers=headers, json=quest_data)
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Telegram CHANNEL quest created successfully!")
        print(f"   ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Points: +{task['points_reward']} XP")
        print(f"   Type: {task['task_type']}")
        return task['id']
    else:
        print(f"❌ Failed to create quest: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_verify_telegram_membership(task_id, telegram_id=123456789):
    """Test Telegram membership verification"""
    print(f"\n🔍 Testing verification for task {task_id[:8]}...")
    
    verify_data = {
        "telegram_id": telegram_id,
        "task_id": task_id
    }
    
    response = requests.post(f"{API_URL}/verify", json=verify_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Verification request sent")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        return result.get('success', False)
    else:
        print(f"❌ Verification failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    print("=" * 70)
    print("🧪 TELEGRAM QUEST CREATION & VERIFICATION TEST")
    print("=" * 70)
    
    # Login
    token = test_admin_login()
    if not token:
        return
    
    # Create Telegram join group quest
    group_task_id = test_create_telegram_join_group_quest(token)
    
    # Create Telegram join channel quest
    channel_task_id = test_create_telegram_join_channel_quest(token)
    
    # Test verification (will fail if user not in group/channel)
    if group_task_id:
        print("\n" + "-" * 70)
        print("Testing GROUP verification (will likely fail - user not in group)")
        print("-" * 70)
        test_verify_telegram_membership(group_task_id)
    
    if channel_task_id:
        print("\n" + "-" * 70)
        print("Testing CHANNEL verification (will likely fail - user not in channel)")
        print("-" * 70)
        test_verify_telegram_membership(channel_task_id)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Telegram JOIN GROUP quest: {'CREATED' if group_task_id else 'FAILED'}")
    print(f"✅ Telegram SUBSCRIBE CHANNEL quest: {'CREATED' if channel_task_id else 'FAILED'}")
    print("=" * 70)
    print("\n💡 NEXT STEPS:")
    print("  1. Open http://localhost/admin.html")
    print("  2. Go to Quests tab")
    print("  3. Click 'CREATE QUEST'")
    print("  4. Select 'Telegram' quest type")
    print("  5. Fill in group/channel details")
    print("  6. Create quest!")
    print("\n⚠️ IMPORTANT:")
    print("  - Bot must be admin in the group/channel")
    print("  - Use numeric chat_id (get with @userinfobot)")
    print("  - Or use @username for public groups/channels")
    print("=" * 70)

if __name__ == "__main__":
    main()
