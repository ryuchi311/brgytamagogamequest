"""
FastAPI Backend Application
"""
import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from dotenv import load_dotenv
from app.models import DatabaseService, supabase
from postgrest.exceptions import APIError

load_dotenv()

app = FastAPI(title="Telegram Bot Points System API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()


# Pydantic Models for API
class UserResponse(BaseModel):
    id: str
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    points: int
    total_earned_points: int
    is_active: bool


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    task_type: str
    platform: Optional[str]
    url: Optional[str]
    points_reward: int
    is_bonus: bool
    is_active: bool


class RewardResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    reward_type: str
    points_cost: int
    quantity_available: Optional[int]
    quantity_claimed: int
    is_active: bool


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    platform: Optional[str] = None
    url: Optional[str] = None
    points_reward: int = 0
    is_bonus: bool = False
    verification_required: bool = False
    verification_data: Optional[dict] = None


class RewardCreate(BaseModel):
    title: str
    description: Optional[str]
    reward_type: str
    points_cost: int
    quantity_available: Optional[int]


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Authentication Functions
def verify_password(plain_password, hashed_password):
    """Verify password using bcrypt"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Get admin from database
    response = supabase.table("admin_users").select("*").eq("username", username).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="User not found")
    
    return response.data[0]


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telegram Bot Points System API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Authentication Endpoints

@app.post("/api/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    """Admin login"""
    response = supabase.table("admin_users").select("*").eq("username", login_request.username).execute()
    
    if not response.data:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    admin = response.data[0]
    
    if not verify_password(login_request.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Update last login
    supabase.table("admin_users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", admin["id"]).execute_update()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# User Endpoints

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100):
    """Get all users"""
    response = supabase.table("users").select("*").range(skip, skip + limit - 1).execute()
    return response.data or []


@app.post("/api/users/init")
async def init_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """Initialize a user if they don't exist - Auto-registration from Telegram"""
    # Check if user exists
    existing = DatabaseService.get_user_by_telegram_id(telegram_id)
    if existing:
        return existing
    
    # Create new user with Telegram data
    user_data = {
        "telegram_id": telegram_id,
        "username": username or f"user_{telegram_id}",
        "first_name": first_name or "Player",
        "last_name": last_name or "",
        "points": 0,
        "is_banned": False
    }
    
    response = supabase.table("users").insert(user_data).execute()
    if response.data:
        return response.data[0]
    raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/api/users/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int):
    """Get user by Telegram ID"""
    user = DatabaseService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/users/{telegram_id}/notifications")
async def get_user_notifications(telegram_id: int, unread_only: bool = False):
    """Get user notifications"""
    user = DatabaseService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = DatabaseService.get_user_notifications(user['id'], unread_only)
    return notifications


@app.post("/api/verify")
async def verify_task_completion(request: dict):
    """Verify and complete a task for a user"""
    from datetime import datetime, timezone
    from app.twitter_client import TwitterClient
    from app.utils import extract_youtube_video_id
    
    telegram_id = request.get('telegram_id')
    task_id = request.get('task_id')
    
    if not telegram_id or not task_id:
        raise HTTPException(status_code=400, detail="telegram_id and task_id are required")
    
    # Get user
    user = DatabaseService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get task
    task_response = supabase.table("tasks").select("*").eq("id", task_id).eq("is_active", True).execute()
    if not task_response.data:
        raise HTTPException(status_code=404, detail="Task not found or inactive")
    
    task = task_response.data[0]
    
    # Check if user already completed this task
    existing = supabase.table("user_tasks").select("*").eq("user_id", user['id']).eq("task_id", task_id).eq("status", "completed").execute()
    if existing.data:
        return {"success": False, "message": "Task already completed"}
    
    # Perform verification based on task_type
    verification_success = False
    verification_message = "Verification pending"
    
    task_type = task.get('task_type', '').lower()
    verification_data = task.get('verification_data') or {}
    
    # Twitter verification (twitter_follow, twitter_like, twitter_retweet, twitter_reply)
    if task_type.startswith('twitter_'):
        try:
            twitter_client = TwitterClient()
            verification_type = verification_data.get('type', task_type.replace('twitter_', ''))
            target_username = verification_data.get('username')
            user_twitter = request.get('twitter_username')
            
            if not user_twitter:
                return {"success": False, "message": "Twitter username required for verification"}
            
            if not target_username and verification_type == 'follow':
                return {"success": False, "message": "Target username not configured in task"}
            
            if verification_type == 'follow':
                result = twitter_client.verify_follow(user_twitter, target_username)
                verification_success = result.get('verified', False)
                verification_message = result.get('message', 'Twitter follow verified' if verification_success else 'Not following')
            
            elif verification_type == 'like':
                tweet_id = verification_data.get('tweet_id')
                if not tweet_id:
                    return {"success": False, "message": "Tweet ID not configured in task"}
                result = twitter_client.verify_like(user_twitter, tweet_id)
                verification_success = result.get('verified', False)
                verification_message = result.get('message', 'Twitter like verified' if verification_success else 'Not liked')
            
            elif verification_type == 'retweet':
                tweet_id = verification_data.get('tweet_id')
                if not tweet_id:
                    return {"success": False, "message": "Tweet ID not configured in task"}
                result = twitter_client.verify_retweet(user_twitter, tweet_id)
                verification_success = result.get('verified', False)
                verification_message = result.get('message', 'Twitter retweet verified' if verification_success else 'Not retweeted')
            
            else:
                verification_message = f"Twitter verification type '{verification_type}' not yet implemented"
                
        except Exception as e:
            verification_message = f"Twitter verification error: {str(e)}"
    
    # Telegram membership verification (telegram_join_group, telegram_join_channel)
    elif task_type.startswith('telegram_'):
        try:
            import requests
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                return {"success": False, "message": "Telegram bot not configured"}
            
            chat_id = verification_data.get('chat_id')
            if not chat_id:
                return {"success": False, "message": "Chat ID not configured in task"}
            
            # Use Telegram Bot API to check membership
            url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
            params = {
                "chat_id": chat_id,
                "user_id": telegram_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('ok'):
                member_status = data.get('result', {}).get('status')
                # Valid statuses: creator, administrator, member, restricted, left, kicked
                if member_status in ['creator', 'administrator', 'member', 'restricted']:
                    verification_success = True
                    verification_message = f"✅ Telegram membership verified! Welcome to {verification_data.get('chat_name', 'the group')}"
                else:
                    verification_success = False
                    verification_message = f"❌ You are not a member of {verification_data.get('chat_name', 'the group')}. Please join first!"
            else:
                error_description = data.get('description', 'Unknown error')
                verification_message = f"Failed to verify membership: {error_description}"
                
        except Exception as e:
            verification_message = f"Telegram verification error: {str(e)}"
            
    # YouTube video watch verification
    elif task_type == 'youtube_watch':
        video_id = extract_youtube_video_id(task.get('url', ''))
        if not video_id:
            return {"success": False, "message": "Invalid YouTube URL"}
        
        try:
            # Check if user already has an active watch session
            existing_view = supabase.table("video_views").select("*").eq("user_id", user['id']).eq("task_id", task_id).eq("status", "watching").execute()
            
            if existing_view.data:
                return {
                    "success": True,
                    "message": "Continue watching and enter the code shown in the video",
                    "requires_code": True,
                    "video_id": video_id,
                    "view_id": existing_view.data[0]['id']
                }
            
            # Create new video view session
            secret_code = verification_data.get('code', 'SECRET')
            min_watch_time = verification_data.get('min_watch_time_seconds', 120)
            
            view_data = {
                "user_id": user['id'],
                "task_id": task_id,
                "video_id": video_id,
                "verification_code": secret_code,
                "status": "watching",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "code_attempts": 0
            }
            
            view_response = supabase.table("video_views").insert(view_data).execute()
            
            if view_response.data:
                return {
                    "success": True,
                    "message": f"Watch the video for at least {min_watch_time} seconds and enter the code",
                    "requires_code": True,
                    "video_id": video_id,
                    "view_id": view_response.data[0]['id'],
                    "min_watch_time": min_watch_time
                }
            else:
                return {"success": False, "message": "Failed to start video session"}
        except APIError as e:
            # If video_views table doesn't exist, create pending task for manual completion
            if 'video_views' in str(e):
                verification_success = True
                verification_message = f"YouTube quest started! Watch the video and remember the code: {verification_data.get('code', 'See video')}"
            else:
                raise
    
    # Daily check-in
    elif task_type == 'daily_checkin':
        # Check if user already checked in today
        today = datetime.now(timezone.utc).date().isoformat()
        recent_checkin = supabase.table("user_tasks").select("*").eq("user_id", user['id']).eq("task_id", task_id).eq("status", "completed").gte("completed_at", today).execute()
        
        if recent_checkin.data:
            return {"success": False, "message": "Already checked in today! Come back tomorrow."}
        
        verification_success = True
        verification_message = "Daily check-in complete!"
    
    # Manual review tasks
    elif task_type == 'manual_review':
        # Create pending user_task for admin review
        verification_success = True
        verification_message = "Task submitted for admin review"
    
    # Generic/other task types
    else:
        verification_success = True
        verification_message = "Task submitted for verification"
    
    # Create or update user_task record
    if verification_success:
        # Determine if task needs pending status (YouTube watch, manual review)
        needs_pending = task_type in ['youtube_watch', 'manual_review']
        
        # Check if pending task exists
        pending_task = supabase.table("user_tasks").select("*").eq("user_id", user['id']).eq("task_id", task_id).execute()
        
        if pending_task.data:
            # Update existing
            user_task_id = pending_task.data[0]['id']
            supabase.table("user_tasks").update({
                "status": "pending" if needs_pending else "completed",
                "completed_at": None if needs_pending else datetime.now(timezone.utc).isoformat()
            }).eq("id", user_task_id).execute()
        else:
            # Create new
            user_task_data = {
                "user_id": user['id'],
                "task_id": task_id,
                "status": "pending" if needs_pending else "completed",
                "completed_at": None if needs_pending else datetime.now(timezone.utc).isoformat()
            }
            supabase.table("user_tasks").insert(user_task_data).execute()
        
        # Award points immediately for completed tasks (not YouTube or manual pending)
        if not needs_pending:
            points_reward = task.get('points_reward', 0)
            new_points = user['points'] + points_reward
            supabase.table("users").update({"points": new_points}).eq("id", user['id']).execute()
            
            return {
                "success": True,
                "message": verification_message,
                "points_earned": points_reward,
                "new_total": new_points
            }
        else:
            return {
                "success": True,
                "message": verification_message,
                "requires_code": task_type == 'youtube_watch'
            }
    
    return {"success": False, "message": verification_message}


# Task Endpoints

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(active_only: bool = True):
    """Get all tasks"""
    if active_only:
        tasks = DatabaseService.get_active_tasks()
    else:
        response = supabase.table("tasks").select("*").execute()
        tasks = response.data or []
    return tasks


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get task by ID"""
    task = DatabaseService.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, admin=Depends(get_current_admin)):
    """Create a new task (Admin only)"""
    # Convert to dict and prepare for insertion
    task_data = {
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "platform": task.platform,
        "url": task.url,
        "points_reward": task.points_reward,
        "is_bonus": task.is_bonus,
        "verification_required": task.verification_required
    }
    
    # Add verification_data only if it exists and is not None
    if task.verification_data is not None:
        task_data["verification_data"] = task.verification_data
    # Attempt insert; if PostgREST schema cache complains about verification_data, retry without it
    try:
        response = supabase.table("tasks").insert(task_data).execute()
    except APIError as e:
        msg = str(e)
        # If verification_data column not found in schema cache, remove it and retry
        if 'verification_data' in msg or 'Could not find the '\
           "'verification_data' column" in msg:
            if 'verification_data' in task_data:
                del task_data['verification_data']
            response = supabase.table("tasks").insert(task_data).execute()
        else:
            raise
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create task")
    
    # Notify all users about new task
    users = supabase.table("users").select("id").eq("is_active", True).execute()
    for user in users.data:
        DatabaseService.create_notification(
            user['id'],
            "New Task Available!",
            f"A new task '{task.title}' is available. Complete it to earn {task.points_reward} points!",
            "new_task"
        )
    
    return response.data[0]


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, admin=Depends(get_current_admin)):
    """Update a task (Admin only)"""
    existing_task = DatabaseService.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task.dict()
    
    try:
        response = supabase.table("tasks").update(task_data).eq("id", task_id).execute()
    except APIError as e:
        # Handle PostgREST schema cache issue with verification_data
        if 'verification_data' in str(e) and 'schema cache' in str(e):
            # Retry without verification_data
            task_data_without_vd = {k: v for k, v in task_data.items() if k != 'verification_data'}
            response = supabase.table("tasks").update(task_data_without_vd).eq("id", task_id).execute()
        else:
            raise
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to update task")
    
    return response.data[0]


@app.patch("/api/tasks/{task_id}/toggle")
async def toggle_task_status(task_id: str, admin=Depends(get_current_admin)):
    """Toggle task active/inactive status (Admin only)"""
    existing_task = DatabaseService.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Toggle the is_active status
    new_status = not existing_task.get('is_active', True)
    response = supabase.table("tasks").update({"is_active": new_status}).eq("id", task_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to toggle task status")
    
    return {
        "message": f"Task {'activated' if new_status else 'deactivated'} successfully",
        "is_active": new_status
    }


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, admin=Depends(get_current_admin)):
    """Delete a task (Admin only)"""
    existing_task = DatabaseService.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Soft delete - just mark as inactive
    supabase.table("tasks").update({"is_active": False}).eq("id", task_id).execute()
    return {"message": "Task deleted successfully"}


# Leaderboard Endpoint

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get leaderboard"""
    leaderboard = DatabaseService.get_leaderboard(limit)
    return leaderboard


# Reward Endpoints

@app.get("/api/rewards", response_model=List[RewardResponse])
async def get_rewards(active_only: bool = True):
    """Get all rewards"""
    if active_only:
        rewards = DatabaseService.get_active_rewards()
    else:
        response = supabase.table("rewards").select("*").execute()
        rewards = response.data or []
    return rewards


@app.post("/api/rewards", response_model=RewardResponse)
async def create_reward(reward: RewardCreate, admin=Depends(get_current_admin)):
    """Create a new reward (Admin only)"""
    reward_data = reward.dict()
    response = supabase.table("rewards").insert(reward_data).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create reward")
    
    return response.data[0]


@app.put("/api/rewards/{reward_id}", response_model=RewardResponse)
async def update_reward(reward_id: str, reward: RewardCreate, admin=Depends(get_current_admin)):
    """Update a reward (Admin only)"""
    reward_data = reward.dict()
    response = supabase.table("rewards").update(reward_data).eq("id", reward_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Reward not found")
    
    return response.data[0]


# Admin Endpoints

@app.get("/api/admin/stats")
async def get_stats(admin=Depends(get_current_admin)):
    """Get system statistics (Admin only)"""
    # Get user count
    users_response = supabase.table("users").select("id", count="exact").execute()
    total_users = users_response.count if users_response.count else 0
    
    # Get active users (last 7 days)
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    active_users_response = supabase.table("activity_logs").select("user_id", count="exact").gte("created_at", seven_days_ago).execute()
    active_users = len(set([log.get('user_id') for log in (active_users_response.data or [])]))
    
    # Get task count
    tasks_response = supabase.table("tasks").select("id", count="exact").eq("is_active", True).execute()
    total_tasks = tasks_response.count if tasks_response.count else 0
    
    # Get completed tasks count
    completed_tasks_response = supabase.table("user_tasks").select("id", count="exact").eq("status", "completed").execute()
    completed_tasks = completed_tasks_response.count if completed_tasks_response.count else 0
    
    # Get total points distributed
    points_response = supabase.table("points_transactions").select("amount").eq("transaction_type", "earned").execute()
    total_points = sum([t.get('amount', 0) for t in (points_response.data or [])])
    
    # Get rewards redeemed
    rewards_response = supabase.table("user_rewards").select("id", count="exact").execute()
    rewards_redeemed = rewards_response.count if rewards_response.count else 0
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "total_points_distributed": total_points,
        "rewards_redeemed": rewards_redeemed
    }


@app.get("/api/admin/user-tasks")
async def get_user_tasks(status: Optional[str] = None, admin=Depends(get_current_admin)):
    """Get user tasks with filters (Admin only)"""
    query = supabase.table("user_tasks").select("*, users(*), tasks(*)")
    
    if status:
        query = query.eq("status", status)
    
    response = query.order("created_at", desc=True).limit(100).execute()
    return response.data or []


@app.put("/api/admin/user-tasks/{user_task_id}/verify")
async def verify_user_task(user_task_id: str, approved: bool, admin=Depends(get_current_admin)):
    """Verify a user task submission (Admin only)"""
    # Get user task
    response = supabase.table("user_tasks").select("*, tasks(*)").eq("id", user_task_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="User task not found")
    
    user_task = response.data[0]
    
    if approved:
        # Award points
        points = user_task['tasks']['points_reward']
        DatabaseService.update_user_points(user_task['user_id'], points, "earned")
        
        # Update user task
        update_data = {
            "status": "completed",
            "points_earned": points,
            "verified_by": admin['id'],
            "verified_at": datetime.utcnow().isoformat()
        }
        
        # Notify user
        DatabaseService.create_notification(
            user_task['user_id'],
            "Task Verified!",
            f"Your task has been verified! You earned {points} points.",
            "task_verified"
        )
    else:
        # Reject task
        update_data = {
            "status": "rejected",
            "verified_by": admin['id'],
            "verified_at": datetime.utcnow().isoformat()
        }
        
        # Notify user
        DatabaseService.create_notification(
            user_task['user_id'],
            "Task Rejected",
            "Your task submission was rejected. Please try again.",
            "system"
        )
    
    supabase.table("user_tasks").update(update_data).eq("id", user_task_id).execute()
    
    return {"message": "Task verification updated"}


@app.put("/api/admin/users/{user_id}/ban")
async def ban_user(user_id: str, admin=Depends(get_current_admin)):
    """Ban/unban a user (Admin only)"""
    user_response = supabase.table("users").select("is_banned").eq("id", user_id).execute()
    
    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_status = user_response.data[0]['is_banned']
    new_status = not current_status
    
    supabase.table("users").update({"is_banned": new_status}).eq("id", user_id).execute()
    
    return {"message": f"User {'banned' if new_status else 'unbanned'} successfully"}


# ============================================================================
# VIDEO VERIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/video-views/start")
async def start_video_view(request: dict):
    """Start tracking a video view for time delay verification"""
    user_id = request.get('user_id')
    task_id = request.get('task_id')
    
    if not user_id or not task_id:
        raise HTTPException(status_code=400, detail="user_id and task_id are required")
    
    # Get task to extract verification code
    task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
    
    if not task_response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_response.data[0]
    verification_data = task.get('verification_data', {})
    
    if not verification_data or verification_data.get('method') != 'time_delay_code':
        raise HTTPException(status_code=400, detail="Task does not support video verification")
    
    verification_code = verification_data.get('code')
    
    # Check if there's already an active view for this user-task combination
    existing_view = supabase.table("video_views").select("*").eq("user_id", user_id).eq("task_id", task_id).eq("status", "watching").execute()
    
    if existing_view.data:
        # Return existing view
        return {"message": "Video view already started", "view": existing_view.data[0]}
    
    # Create new video view record
    view_data = {
        "user_id": user_id,
        "task_id": task_id,
        "verification_code": verification_code,
        "status": "watching"
    }
    
    result = supabase.table("video_views").insert(view_data).execute()
    
    return {"message": "Video view started", "view": result.data[0] if result.data else None}


@app.post("/api/video-views/verify")
async def verify_video_code(request: dict):
    """Verify video code with time delay check"""
    from datetime import datetime, timezone
    
    user_id = request.get('user_id')
    code = request.get('code', '').strip()
    
    if not user_id or not code:
        raise HTTPException(status_code=400, detail="user_id and code are required")
    
    # Find active video view for this user with matching code
    view_response = supabase.table("video_views").select("*, tasks(*)").eq("user_id", user_id).eq("verification_code", code).eq("status", "watching").execute()
    
    if not view_response.data:
        # No active view found - could be wrong code or no active quest
        return {"success": False, "error": "no_active_view", "message": "No active video quest found with this code"}
    
    view = view_response.data[0]
    task = view['tasks']
    verification_data = task.get('verification_data', {})
    
    min_watch_time = verification_data.get('min_watch_time_seconds', 120)
    max_attempts = verification_data.get('max_attempts', 3)
    
    # Calculate time watched
    started_at = datetime.fromisoformat(view['started_at'].replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    time_watched_seconds = int((now - started_at).total_seconds())
    
    # Check if max attempts reached
    if view['code_attempts'] >= max_attempts:
        # Update status to failed
        supabase.table("video_views").update({"status": "failed"}).eq("id", view['id']).execute()
        return {
            "success": False,
            "error": "max_attempts",
            "message": "Maximum verification attempts reached",
            "attempts_left": 0
        }
    
    # Increment attempt counter
    new_attempts = view['code_attempts'] + 1
    supabase.table("video_views").update({"code_attempts": new_attempts}).eq("id", view['id']).execute()
    
    # Check if code is correct (case-insensitive)
    if code.upper() != verification_data.get('code', '').upper():
        attempts_left = max_attempts - new_attempts
        
        if attempts_left <= 0:
            # Failed after max attempts
            supabase.table("video_views").update({"status": "failed"}).eq("id", view['id']).execute()
        
        return {
            "success": False,
            "error": "wrong_code",
            "message": "Incorrect verification code",
            "attempts_left": attempts_left,
            "time_watched_seconds": time_watched_seconds
        }
    
    # Check if minimum watch time has elapsed
    if time_watched_seconds < min_watch_time:
        time_remaining = min_watch_time - time_watched_seconds
        return {
            "success": False,
            "error": "too_soon",
            "message": "Please watch more of the video",
            "time_watched_seconds": time_watched_seconds,
            "min_watch_time_seconds": min_watch_time,
            "time_remaining_seconds": time_remaining,
            "attempts_left": max_attempts - new_attempts
        }
    
    # All checks passed! Mark as completed
    supabase.table("video_views").update({
        "status": "completed",
        "completed_at": now.isoformat()
    }).eq("id", view['id']).execute()
    
    # Check if user already completed this task
    existing_completion = supabase.table("user_tasks").select("*").eq("user_id", user_id).eq("task_id", task['id']).execute()
    
    if existing_completion.data:
        return {
            "success": False,
            "error": "already_completed",
            "message": "You have already completed this task"
        }
    
    # Complete the task
    user_task_data = {
        "user_id": user_id,
        "task_id": task['id'],
        "status": "verified"
    }
    supabase.table("user_tasks").insert(user_task_data).execute()
    
    # Update user points
    user_response = supabase.table("users").select("points").eq("id", user_id).execute()
    current_points = user_response.data[0]['points'] if user_response.data else 0
    new_points = current_points + task['points_reward']
    
    supabase.table("users").update({"points": new_points}).eq("id", user_id).execute()
    
    # Create notification
    notification_data = {
        "user_id": user_id,
        "title": "Quest Completed!",
        "message": f"You earned {task['points_reward']} points for completing '{task['title']}'",
        "type": "task_verified"
    }
    supabase.table("notifications").insert(notification_data).execute()
    
    return {
        "success": True,
        "message": "Video quest completed successfully!",
        "task": task,
        "points_earned": task['points_reward'],
        "time_watched_seconds": time_watched_seconds,
        "attempts_left": max_attempts - new_attempts
    }


@app.get("/api/video-views/stats")
async def get_video_stats(current_admin: dict = Depends(get_current_admin)):
    """Get statistics about video views for admin dashboard"""
    
    # Get counts by status
    stats_query = """
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'watching' THEN 1 END) as watching,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
            AVG(CASE 
                WHEN completed_at IS NOT NULL 
                THEN EXTRACT(EPOCH FROM (completed_at - started_at))
                ELSE NULL 
            END) as avg_watch_time_seconds
        FROM video_views
    """
    
    # Execute raw SQL query
    result = supabase.rpc('exec_sql', {'query': stats_query}).execute()
    
    # If RPC doesn't exist, fall back to counting separately
    if not result.data:
        all_views = supabase.table("video_views").select("status").execute()
        
        stats = {
            "total": len(all_views.data),
            "watching": len([v for v in all_views.data if v['status'] == 'watching']),
            "completed": len([v for v in all_views.data if v['status'] == 'completed']),
            "failed": len([v for v in all_views.data if v['status'] == 'failed']),
            "avg_watch_time_seconds": 0
        }
    else:
        stats = result.data[0]
    
    return stats


# ============================================================================
# TWITTER VERIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/twitter/verify")
async def verify_twitter_action(request: dict):
    """
    Verify Twitter actions (follow, like, retweet) using Twitter API v2
    Free tier: 100 reads/month
    """
    from app.twitter_client import twitter_client
    from datetime import timezone
    
    user_id = request.get('user_id')
    task_id = request.get('task_id')
    twitter_username = request.get('twitter_username', '').strip().lstrip('@')
    verification_type = request.get('verification_type')  # 'follow', 'like', 'retweet'
    tweet_id = request.get('tweet_id')  # For like/retweet
    
    if not all([user_id, task_id, twitter_username, verification_type]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    if verification_type in ['like', 'retweet'] and not tweet_id:
        raise HTTPException(status_code=400, detail="tweet_id required for like/retweet verification")
    
    # Check if already verified (cache check)
    cache_check = supabase.table("twitter_verifications").select("*").eq("user_id", user_id).eq("task_id", task_id).eq("verified", True).execute()
    
    if cache_check.data:
        cached = cache_check.data[0]
        # Check if cache is still valid (24 hours)
        expires_at = datetime.fromisoformat(cached['expires_at'].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) < expires_at:
            return {
                "success": True,
                "verified": True,
                "cached": True,
                "message": "Already verified (cached)",
                "verified_at": cached['verified_at']
            }
    
    # Get task details
    task_response = supabase.table("tasks").select("*").eq("id", task_id).execute()
    if not task_response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_response.data[0]
    
    # Verify based on type
    result = None
    verified = False
    
    if verification_type == 'follow':
        result = twitter_client.verify_follow(twitter_username)
        verified = result.get('is_following', False) if result.get('success') else False
        
    elif verification_type == 'like':
        result = twitter_client.verify_like(twitter_username, tweet_id)
        verified = result.get('has_liked', False) if result.get('success') else False
        
    elif verification_type == 'retweet':
        result = twitter_client.verify_retweet(twitter_username, tweet_id)
        verified = result.get('has_retweeted', False) if result.get('success') else False
    else:
        raise HTTPException(status_code=400, detail=f"Invalid verification_type: {verification_type}")
    
    # Check if API call failed
    if not result or not result.get('success'):
        error_message = result.get('message', 'Twitter API error') if result else 'Twitter API unavailable'
        
        # If API unavailable, fall back to manual verification
        if result and not result.get('api_available', True):
            return {
                "success": False,
                "verified": False,
                "fallback_to_manual": True,
                "error": "twitter_api_unavailable",
                "message": "Twitter API limit reached. Task will be marked for manual verification."
            }
        
        return {
            "success": False,
            "verified": False,
            "error": result.get('error') if result else 'api_error',
            "message": error_message
        }
    
    # Store verification result
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=24)  # Cache for 24 hours
    
    verification_data = {
        "user_id": user_id,
        "task_id": task_id,
        "twitter_username": twitter_username,
        "verification_type": verification_type,
        "tweet_id": tweet_id,
        "verified": verified,
        "verified_at": now.isoformat() if verified else None,
        "expires_at": expires_at.isoformat(),
        "api_response": result
    }
    
    # Upsert verification record
    existing = supabase.table("twitter_verifications").select("id").eq("user_id", user_id).eq("task_id", task_id).execute()
    
    if existing.data:
        supabase.table("twitter_verifications").update(verification_data).eq("id", existing.data[0]['id']).execute()
    else:
        supabase.table("twitter_verifications").insert(verification_data).execute()
    
    # Update user's Twitter username if verified
    if verified:
        supabase.table("users").update({
            "twitter_username": twitter_username,
            "twitter_verified": True,
            "twitter_verified_at": now.isoformat()
        }).eq("id", user_id).execute()
    
    # If not verified, return failure
    if not verified:
        return {
            "success": True,
            "verified": False,
            "message": f"Twitter {verification_type} not detected. Please complete the action and try again."
        }
    
    # If verified, complete the task
    # Check if already completed
    existing_completion = supabase.table("user_tasks").select("*").eq("user_id", user_id).eq("task_id", task_id).execute()
    
    if existing_completion.data:
        return {
            "success": True,
            "verified": True,
            "already_completed": True,
            "message": "Task already completed"
        }
    
    # Complete the task
    user_task_data = {
        "user_id": user_id,
        "task_id": task_id,
        "status": "verified",
        "completed_at": now.isoformat(),
        "verified_at": now.isoformat()
    }
    supabase.table("user_tasks").insert(user_task_data).execute()
    
    # Update user points
    user_response = supabase.table("users").select("points, total_earned_points").eq("id", user_id).execute()
    if user_response.data:
        current_points = user_response.data[0]['points']
        total_earned = user_response.data[0].get('total_earned_points', 0)
        
        new_points = current_points + task['points_reward']
        new_total_earned = total_earned + task['points_reward']
        
        supabase.table("users").update({
            "points": new_points,
            "total_earned_points": new_total_earned
        }).eq("id", user_id).execute()
    
    # Create notification
    notification_data = {
        "user_id": user_id,
        "title": "Twitter Quest Completed!",
        "message": f"You earned {task['points_reward']} points for completing '{task['title']}'",
        "type": "task_verified"
    }
    supabase.table("notifications").insert(notification_data).execute()
    
    return {
        "success": True,
        "verified": True,
        "task": task,
        "points_earned": task['points_reward'],
        "message": f"Twitter {verification_type} verified! {task['points_reward']} points earned!"
    }


@app.get("/api/twitter/usage")
async def get_twitter_api_usage(current_admin: dict = Depends(get_current_admin)):
    """Get Twitter API usage statistics (admin only)"""
    from app.twitter_client import twitter_client
    
    usage_stats = twitter_client.get_usage_stats()
    
    # Also get from database
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    db_stats = supabase.table("twitter_api_usage").select("*").gte("period_start", current_month_start.isoformat()).execute()
    
    return {
        "current_usage": usage_stats,
        "db_tracking": db_stats.data if db_stats.data else []
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
