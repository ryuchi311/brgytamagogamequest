#!/usr/bin/env python3
"""
Fix YouTube quest that's missing column data
Extracts data from verification_data JSON and updates the columns
"""

import os
from supabase import create_client

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    exit(1)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Quest ID to fix
QUEST_ID = '2f66701b-a7d1-401b-b715-e5753fb66e03'

print(f"🔧 Fixing quest: {QUEST_ID}")
print("━" * 60)

# Get the current quest data
response = supabase.table('tasks').select('*').eq('id', QUEST_ID).execute()

if not response.data:
    print(f"❌ Quest {QUEST_ID} not found!")
    exit(1)

quest = response.data[0]
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

# Update the quest
update_response = supabase.table('tasks').update(update_data).eq('id', QUEST_ID).execute()

if update_response.data:
    print(f"\n✅ Quest updated successfully!")
    
    # Verify the update
    verify_response = supabase.table('tasks').select('*').eq('id', QUEST_ID).execute()
    updated_quest = verify_response.data[0]
    
    print(f"\n✨ Updated YouTube columns:")
    print(f"   youtube_video_id: {updated_quest.get('youtube_video_id')}")
    print(f"   min_watch_time_seconds: {updated_quest.get('min_watch_time_seconds')}")
    print(f"   video_duration_seconds: {updated_quest.get('video_duration_seconds')}")
    print(f"   verification_code: {updated_quest.get('verification_code')}")
    print(f"   code_display_time_seconds: {updated_quest.get('code_display_time_seconds')}")
else:
    print(f"\n❌ Update failed!")

print("\n━" * 60)
print("✅ Done!")
