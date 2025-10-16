#!/usr/bin/env python3
"""
Test script to verify Edit and Toggle Status functionality
"""
import requests
import json

API_URL = "http://localhost/api"

def test_admin_login():
    """Test admin login"""
    print("🔐 Testing admin login...")
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

def test_get_tasks(token):
    """Get all tasks"""
    print("\n📋 Fetching all tasks...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/tasks", headers=headers)
    
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ Found {len(tasks)} tasks")
        return tasks
    else:
        print(f"❌ Failed to fetch tasks: {response.status_code}")
        return []

def test_toggle_status(token, task_id, current_status):
    """Test toggle task status"""
    print(f"\n🔄 Toggling task {task_id[:8]}... (currently {'ACTIVE' if current_status else 'INACTIVE'})")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(f"{API_URL}/tasks/{task_id}/toggle", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        new_status = result.get("is_active")
        print(f"✅ Status toggled! Now: {'ACTIVE' if new_status else 'INACTIVE'}")
        return True
    else:
        print(f"❌ Failed to toggle: {response.status_code} - {response.text}")
        return False

def test_edit_task(token, task_id):
    """Test editing a task"""
    print(f"\n✏️ Editing task {task_id[:8]}...")
    
    # First get the task
    headers = {"Authorization": f"Bearer {token}"}
    get_response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)
    
    if get_response.status_code != 200:
        print(f"❌ Failed to fetch task: {get_response.status_code}")
        return False
    
    task = get_response.json()
    original_title = task.get("title")
    
    # Update the task
    task["title"] = f"{original_title} (EDITED)"
    task["points_reward"] = (task.get("points_reward", 0) or 0) + 5
    
    put_response = requests.put(
        f"{API_URL}/tasks/{task_id}",
        headers={**headers, "Content-Type": "application/json"},
        json=task
    )
    
    if put_response.status_code == 200:
        updated = put_response.json()
        print(f"✅ Task edited successfully!")
        print(f"   Old title: {original_title}")
        print(f"   New title: {updated.get('title')}")
        print(f"   New points: +{updated.get('points_reward')} XP")
        return True
    else:
        print(f"❌ Failed to edit: {put_response.status_code} - {put_response.text}")
        return False

def main():
    print("=" * 60)
    print("🧪 ADMIN PANEL ACTIONS TEST")
    print("=" * 60)
    
    # Login
    token = test_admin_login()
    if not token:
        return
    
    # Get tasks
    tasks = test_get_tasks(token)
    if not tasks:
        print("\n⚠️ No tasks found. Create some tasks first!")
        return
    
    # Test with first task
    test_task = tasks[0]
    task_id = test_task["id"]
    current_status = test_task.get("is_active", True)
    
    print(f"\n📝 Testing with task: {test_task['title']}")
    print(f"   ID: {task_id}")
    print(f"   Type: {test_task.get('task_type', 'N/A')}")
    print(f"   Points: +{test_task.get('points_reward', 0)} XP")
    print(f"   Status: {'ACTIVE' if current_status else 'INACTIVE'}")
    
    # Test toggle
    toggle_success = test_toggle_status(token, task_id, current_status)
    
    if toggle_success:
        # Toggle back
        print("\n🔄 Toggling back to original status...")
        test_toggle_status(token, task_id, not current_status)
    
    # Test edit
    edit_success = test_edit_task(token, task_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Toggle Status: {'PASSED' if toggle_success else 'FAILED'}")
    print(f"✅ Edit Task: {'PASSED' if edit_success else 'FAILED'}")
    print("=" * 60)
    
    if toggle_success and edit_success:
        print("\n🎉 All tests PASSED! Actions are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
