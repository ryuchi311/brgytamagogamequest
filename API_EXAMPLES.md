# API Examples and Usage Guide

This document provides practical examples of using the Telegram Bot Points System API.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Most admin endpoints require JWT authentication. First, obtain a token:

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "changeme123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:
```bash
-H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## User Endpoints

### Get All Users

```bash
curl http://localhost:8000/api/users
```

### Get User by Telegram ID

```bash
curl http://localhost:8000/api/users/123456789
```

Response:
```json
{
  "id": "uuid-here",
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "points": 150,
  "total_earned_points": 300,
  "is_active": true
}
```

### Get User Notifications

```bash
# All notifications
curl http://localhost:8000/api/users/123456789/notifications

# Unread only
curl http://localhost:8000/api/users/123456789/notifications?unread_only=true
```

## Task Endpoints

### Get All Active Tasks

```bash
curl http://localhost:8000/api/tasks
```

### Get All Tasks (Including Inactive)

```bash
curl http://localhost:8000/api/tasks?active_only=false
```

### Get Task by ID

```bash
curl http://localhost:8000/api/tasks/task-uuid-here
```

### Create Task (Admin)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Follow us on Instagram",
    "description": "Follow our Instagram account @example",
    "task_type": "social_follow",
    "platform": "instagram",
    "url": "https://instagram.com/example",
    "points_reward": 50,
    "is_bonus": false,
    "verification_required": false
  }'
```

### Update Task (Admin)

```bash
curl -X PUT http://localhost:8000/api/tasks/task-uuid-here \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "description": "Updated description",
    "task_type": "social_follow",
    "platform": "instagram",
    "url": "https://instagram.com/example",
    "points_reward": 75,
    "is_bonus": true,
    "verification_required": true
  }'
```

### Delete Task (Admin)

```bash
curl -X DELETE http://localhost:8000/api/tasks/task-uuid-here \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Reward Endpoints

### Get All Active Rewards

```bash
curl http://localhost:8000/api/rewards
```

### Create Reward (Admin)

```bash
curl -X POST http://localhost:8000/api/rewards \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "$10 Amazon Gift Card",
    "description": "Get a $10 Amazon gift card",
    "reward_type": "gift_card",
    "points_cost": 1000,
    "quantity_available": 20
  }'
```

### Update Reward (Admin)

```bash
curl -X PUT http://localhost:8000/api/rewards/reward-uuid-here \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "$15 Amazon Gift Card",
    "description": "Updated: Get a $15 Amazon gift card",
    "reward_type": "gift_card",
    "points_cost": 1500,
    "quantity_available": 15
  }'
```

## Leaderboard

### Get Top Users

```bash
# Top 10 (default)
curl http://localhost:8000/api/leaderboard

# Custom limit
curl http://localhost:8000/api/leaderboard?limit=20
```

Response:
```json
[
  {
    "id": "uuid",
    "username": "user1",
    "first_name": "Alice",
    "points": 1500
  },
  {
    "id": "uuid",
    "username": "user2",
    "first_name": "Bob",
    "points": 1200
  }
]
```

## Admin Endpoints

### Get System Statistics

```bash
curl http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "total_users": 150,
  "active_users": 75,
  "total_tasks": 25,
  "completed_tasks": 450,
  "total_points_distributed": 15000,
  "rewards_redeemed": 30
}
```

### Get User Tasks (Verification Queue)

```bash
# All user tasks
curl http://localhost:8000/api/admin/user-tasks \
  -H "Authorization: Bearer YOUR_TOKEN"

# Only submitted tasks (pending verification)
curl http://localhost:8000/api/admin/user-tasks?status=submitted \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Verify Task Submission

```bash
# Approve task
curl -X PUT http://localhost:8000/api/admin/user-tasks/user-task-uuid/verify?approved=true \
  -H "Authorization: Bearer YOUR_TOKEN"

# Reject task
curl -X PUT http://localhost:8000/api/admin/user-tasks/user-task-uuid/verify?approved=false \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ban/Unban User

```bash
curl -X PUT http://localhost:8000/api/admin/users/user-uuid/ban \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python Examples

### Using Requests Library

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
def login(username, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()["access_token"]

# Get authenticated headers
def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

# Get all tasks
def get_tasks():
    response = requests.get(f"{BASE_URL}/tasks")
    return response.json()

# Create task (admin)
def create_task(token, task_data):
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=get_headers(token),
        json=task_data
    )
    return response.json()

# Usage
token = login("admin", "changeme123")
tasks = get_tasks()
print(f"Found {len(tasks)} tasks")

# Create new task
new_task = {
    "title": "Watch YouTube Video",
    "description": "Watch our latest tutorial",
    "task_type": "watch_video",
    "platform": "youtube",
    "url": "https://youtube.com/watch?v=example",
    "points_reward": 30,
    "is_bonus": False,
    "verification_required": False
}
created = create_task(token, new_task)
print(f"Created task: {created['id']}")
```

### Using HTTPX (Async)

```python
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api"

async def get_leaderboard(limit=10):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/leaderboard",
            params={"limit": limit}
        )
        return response.json()

async def main():
    leaderboard = await get_leaderboard(20)
    for i, user in enumerate(leaderboard, 1):
        print(f"{i}. {user['first_name']}: {user['points']} points")

asyncio.run(main())
```

## JavaScript Examples

### Using Fetch API

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Login
async function login(username, password) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.access_token;
}

// Get tasks
async function getTasks() {
  const response = await fetch(`${BASE_URL}/tasks`);
  return await response.json();
}

// Create task (admin)
async function createTask(token, taskData) {
  const response = await fetch(`${BASE_URL}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(taskData)
  });
  return await response.json();
}

// Usage
(async () => {
  const token = await login('admin', 'changeme123');
  const tasks = await getTasks();
  console.log(`Found ${tasks.length} tasks`);
})();
```

### Using Axios

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api';

// Create axios instance with auth
function getClient(token) {
  return axios.create({
    baseURL: BASE_URL,
    headers: { 'Authorization': `Bearer ${token}` }
  });
}

// Login
async function login(username, password) {
  const response = await axios.post(`${BASE_URL}/auth/login`, {
    username,
    password
  });
  return response.data.access_token;
}

// Get stats
async function getStats(token) {
  const client = getClient(token);
  const response = await client.get('/admin/stats');
  return response.data;
}

// Usage
(async () => {
  try {
    const token = await login('admin', 'changeme123');
    const stats = await getStats(token);
    console.log('System Stats:', stats);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
})();
```

## Common Workflows

### New User Registration Flow

1. User sends `/start` to Telegram bot
2. Bot checks if user exists in database
3. If not, creates new user record
4. Returns welcome message with points (0)

### Task Completion Flow

1. User views available tasks (`/tasks`)
2. User selects a task
3. User completes the task externally
4. User marks task as complete
5. If verification required:
   - Task status: `submitted`
   - Admin reviews and approves/rejects
6. If no verification:
   - Points added immediately
   - Task status: `completed`

### Reward Redemption Flow

1. User views rewards (`/rewards`)
2. User selects a reward
3. System checks if user has enough points
4. System checks reward availability
5. Deducts points from user
6. Generates redemption code
7. Creates user_reward record
8. Sends notification to user

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{
  "detail": "Invalid authentication credentials"
}
```

**404 Not Found**
```json
{
  "detail": "User not found"
}
```

**400 Bad Request**
```json
{
  "detail": "Insufficient points"
}
```

### Error Handling Example

```python
import requests

try:
    response = requests.get(f"{BASE_URL}/users/999999999")
    response.raise_for_status()
    user = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("User not found")
    elif e.response.status_code == 401:
        print("Authentication required")
    else:
        print(f"Error: {e.response.text}")
```

## Rate Limiting

The API includes basic rate limiting:
- 10 requests per minute per user for anonymous endpoints
- 100 requests per minute for authenticated endpoints

Rate limit headers in response:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1640000000
```

## Best Practices

1. **Cache tokens**: Store JWT tokens securely, don't request new ones for every API call
2. **Handle errors**: Always implement proper error handling
3. **Use pagination**: For large datasets, implement pagination
4. **Validate input**: Validate data before sending to API
5. **Use HTTPS**: Always use HTTPS in production
6. **Keep secrets safe**: Never expose API keys or tokens in client-side code

## Testing with Postman

Import this collection to Postman:

1. Create new collection "Telegram Bot API"
2. Add environment variables:
   - `baseUrl`: http://localhost:8000/api
   - `token`: (leave empty, will be set after login)
3. Create requests as shown in examples above
4. Use `{{baseUrl}}` and `{{token}}` variables

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide a complete reference with:
- All endpoints
- Request/response schemas
- Try-it-out functionality
- Authentication setup
