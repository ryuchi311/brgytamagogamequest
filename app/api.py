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
    description: Optional[str]
    task_type: str
    platform: Optional[str]
    url: Optional[str]
    points_reward: int
    is_bonus: bool = False
    verification_required: bool = False


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
    supabase.table("admin_users").update({"last_login": datetime.utcnow().isoformat()}).eq("id", admin["id"]).execute()
    
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
    task_data = task.dict()
    response = supabase.table("tasks").insert(task_data).execute()
    
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
    response = supabase.table("tasks").update(task_data).eq("id", task_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to update task")
    
    return response.data[0]


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
