#!/bin/bash

# Test YouTube Quest Creation with All YouTube Settings Columns

echo "🎬 Testing YouTube Quest Creation with Full Settings"
echo "=================================================="
echo ""

# First, let's test without authentication (if endpoint allows)
# or we'll need to get an admin token

echo "📝 Creating YouTube quest with all settings..."
echo ""

# Create the quest
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test YouTube Quest - Full Settings",
    "description": "Watch the video and enter the code shown at 0:20 to earn 250 points",
    "task_type": "youtube_watch",
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "points_reward": 250,
    "is_active": true,
    "min_watch_time_seconds": 45,
    "video_duration_seconds": 212,
    "verification_code": "NEWCODE2025",
    "code_display_time_seconds": 20
  }')

echo "Response:"
echo "$RESPONSE" | python3 -m json.tool 2>&1

# Extract task ID if successful
TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "" ]; then
    echo ""
    echo "✅ Quest created successfully!"
    echo "Task ID: $TASK_ID"
    echo ""
    echo "🔍 Verifying YouTube settings were saved..."
    echo ""
    
    # Fetch the task to verify all fields were saved
    curl -s "http://localhost:8000/api/tasks/$TASK_ID" | python3 -m json.tool
    
    echo ""
    echo "✅ Test complete!"
else
    echo ""
    echo "❌ Failed to create quest"
    echo "This might be due to authentication requirements"
fi
