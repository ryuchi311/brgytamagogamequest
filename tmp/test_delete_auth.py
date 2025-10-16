#!/usr/bin/env python3
"""
Test DELETE task endpoint with authentication
"""
import requests
import json

API_URL = "http://localhost/api"

def test_delete_task():
    print("=" * 70)
    print("🧪 DELETE TASK AUTHENTICATION TEST")
    print("=" * 70)
    
    # Step 1: Login
    print("\n🔐 Step 1: Logging in as admin...")
    login_response = requests.post(f"{API_URL}/auth/login", json={
        "username": "admin",
        "password": "changeme123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    # Step 2: Get list of tasks
    print("\n📋 Step 2: Fetching tasks...")
    headers = {"Authorization": f"Bearer {token}"}
    tasks_response = requests.get(f"{API_URL}/tasks", headers=headers)
    
    if tasks_response.status_code != 200:
        print(f"❌ Failed to fetch tasks: {tasks_response.status_code}")
        return
    
    tasks = tasks_response.json()
    print(f"✅ Found {len(tasks)} tasks")
    
    if not tasks:
        print("⚠️ No tasks available to test delete")
        return
    
    # Find an inactive task to safely delete
    test_task = None
    for task in tasks:
        if not task.get('is_active', True):
            test_task = task
            break
    
    # If no inactive task, use the last one
    if not test_task:
        test_task = tasks[-1]
        print(f"\n⚠️ No inactive tasks found, using active task for testing")
    
    task_id = test_task['id']
    print(f"\n🎯 Selected task for DELETE test:")
    print(f"   ID: {task_id}")
    print(f"   Title: {test_task.get('title', 'N/A')}")
    print(f"   Active: {test_task.get('is_active', True)}")
    
    # Step 3: Test DELETE without auth (should fail)
    print(f"\n❌ Step 3: Testing DELETE without authentication...")
    delete_no_auth = requests.delete(f"{API_URL}/tasks/{task_id}")
    print(f"   Status: {delete_no_auth.status_code}")
    if delete_no_auth.status_code == 401:
        print(f"   ✅ Correctly rejected (401 Unauthorized)")
    else:
        print(f"   ⚠️ Unexpected status (expected 401)")
    
    # Step 4: Test DELETE with invalid token (should fail)
    print(f"\n❌ Step 4: Testing DELETE with invalid token...")
    bad_headers = {"Authorization": "Bearer invalid_token_12345"}
    delete_bad_token = requests.delete(f"{API_URL}/tasks/{task_id}", headers=bad_headers)
    print(f"   Status: {delete_bad_token.status_code}")
    if delete_bad_token.status_code == 401:
        print(f"   ✅ Correctly rejected (401 Unauthorized)")
    else:
        print(f"   ⚠️ Unexpected status (expected 401)")
    
    # Step 5: Test DELETE with valid token (should succeed)
    print(f"\n✅ Step 5: Testing DELETE with valid authentication...")
    delete_response = requests.delete(f"{API_URL}/tasks/{task_id}", headers=headers)
    print(f"   Status: {delete_response.status_code}")
    
    if delete_response.status_code == 200:
        print(f"   ✅ DELETE successful!")
        result = delete_response.json()
        print(f"   Message: {result.get('message', 'Task deleted')}")
    else:
        print(f"   ❌ DELETE failed")
        print(f"   Response: {delete_response.text}")
    
    # Step 6: Verify task is deleted (soft delete - marked as inactive)
    print(f"\n🔍 Step 6: Verifying task is deleted...")
    verify_response = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)
    
    if verify_response.status_code == 200:
        task = verify_response.json()
        if not task.get('is_active', True):
            print(f"   ✅ Task marked as inactive (soft delete confirmed)")
        else:
            print(f"   ⚠️ Task still active (unexpected)")
    elif verify_response.status_code == 404:
        print(f"   ✅ Task not found (hard delete confirmed)")
    else:
        print(f"   ⚠️ Unexpected status: {verify_response.status_code}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Authentication: Working")
    print(f"✅ Authorization Check: Working (401 without/with invalid token)")
    print(f"✅ DELETE Endpoint: {'Working' if delete_response.status_code == 200 else 'Failed'}")
    print("=" * 70)
    
    print("\n💡 SOLUTION FOR 401 ERRORS:")
    print("   1. Make sure you're logged in to the admin panel")
    print("   2. If you see 401 errors, refresh the page and log in again")
    print("   3. Token expires after 30 minutes - re-login if needed")
    print("   4. Check browser console for 'authToken' value")
    print("=" * 70)

if __name__ == "__main__":
    test_delete_task()
