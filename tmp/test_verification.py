import requests
import json

# Test user
telegram_id = 123456789

# Test 1: Daily check-in (should auto-complete)
print("=== Test 1: Daily Check-in ===")
r = requests.post('http://localhost/api/verify', json={
    'telegram_id': telegram_id,
    'task_id': '51b64498-08e6-452e-8060-104c94c20804'
})
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# Test 2: YouTube watch (should create video session)
print("=== Test 2: YouTube Watch ===")
r = requests.post('http://localhost/api/verify', json={
    'telegram_id': telegram_id,
    'task_id': '88a3f240-1b85-4d1d-bc7c-e786a281ee51'
})
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# Test 3: Twitter follow (will fail without twitter username, but shows flow)
print("=== Test 3: Twitter Follow (no username) ===")
r = requests.post('http://localhost/api/verify', json={
    'telegram_id': telegram_id,
    'task_id': '63f558a8-eb3e-414d-997c-76d8b4897fad'
})
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# Test 4: Twitter follow (with username)
print("=== Test 4: Twitter Follow (with username) ===")
r = requests.post('http://localhost/api/verify', json={
    'telegram_id': telegram_id,
    'task_id': '63f558a8-eb3e-414d-997c-76d8b4897fad',
    'twitter_username': 'testuser123'
})
print(f"Status: {r.status_code}")
print(json.dumps(r.json(), indent=2))
print()

# Check user points
print("=== User Points After Tests ===")
r = requests.get(f'http://localhost/api/users/{telegram_id}')
if r.status_code == 200:
    user = r.json()
    print(f"Points: {user['points']}")
    print(f"Total Earned: {user['total_earned_points']}")
