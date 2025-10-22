#!/usr/bin/env python3
"""
Fix YouTube quest columns by extracting from verification_data
"""

import os
import requests
import json

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

QUEST_ID = '2f66701b-a7d1-401b-b715-e5753fb66e03'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

print(f"🔧 Fixing quest: {QUEST_ID}")
print("━" * 60)

# Get quest data
url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{QUEST_ID}&select=*"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ Error fetching quest: {response.text}")
    exit(1)

quests = response.json()
if not quests:
    print(f"❌ Quest not found!")
    exit(1)

quest = quests[0]
print(f"✅ Found quest: {quest['title']}")
print(f"\n📊 Current YouTube columns:")
print(f"   youtube_video_id: {quest.get('youtube_video_id')}")
print(f"   min_watch_time_seconds: {quest.get('min_watch_time_seconds')}")
print(f"   video_duration_seconds: {quest.get('video_duration_seconds')}")
print(f"   verification_code: {quest.get('verification_code')}")
print(f"   code_display_time_seconds: {quest.get('code_display_time_seconds')}")

# Extract from verification_data
verification_data = quest.get('verification_data', {})
print(f"\n📦 Data in verification_data JSON:")
print(f"   video_id: {verification_data.get('video_id')}")
print(f"   min_watch_time: {verification_data.get('min_watch_time')}")
print(f"   video_duration: {verification_data.get('video_duration')}")
print(f"   verification_code: {verification_data.get('verification_code')}")
print(f"   code_display_time: {verification_data.get('code_display_time')}")

# Prepare update data
update_data = {
    'youtube_video_id': verification_data.get('video_id'),
    'min_watch_time_seconds': verification_data.get('min_watch_time', 30),
    'video_duration_seconds': verification_data.get('video_duration'),
    'verification_code': verification_data.get('verification_code'),
    'code_display_time_seconds': verification_data.get('code_display_time')
}

# Remove None values
update_data = {k: v for k, v in update_data.items() if v is not None}

print(f"\n🔄 Updating with:")
for key, value in update_data.items():
    print(f"   {key}: {value}")

# Update quest
update_url = f"{SUPABASE_URL}/rest/v1/tasks?id=eq.{QUEST_ID}"
update_response = requests.patch(update_url, headers=headers, json=update_data)

if update_response.status_code in [200, 204]:
    print(f"\n✅ Quest updated successfully!")
    
    # Verify
    verify_response = requests.get(url, headers=headers)
    updated_quest = verify_response.json()[0]
    
    print(f"\n✨ Updated YouTube columns:")
    print(f"   youtube_video_id: {updated_quest.get('youtube_video_id')}")
    print(f"   min_watch_time_seconds: {updated_quest.get('min_watch_time_seconds')}")
    print(f"   video_duration_seconds: {updated_quest.get('video_duration_seconds')}")
    print(f"   verification_code: {updated_quest.get('verification_code')}")
    print(f"   code_display_time_seconds: {updated_quest.get('code_display_time_seconds')}")
else:
    print(f"\n❌ Update failed: {update_response.status_code}")
    print(update_response.text)

print("\n━" * 60)
print("✅ Done!")
