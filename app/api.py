"""
FastAPI Backend Application
"""
import os
import re
import time
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from dotenv import load_dotenv
from app.models import DatabaseService, supabase, get_db_connection
from postgrest.exceptions import APIError
from psycopg2 import OperationalError
from psycopg2.errors import UndefinedColumn

load_dotenv()

app = FastAPI(
    title="Telegram Bot Points System API",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

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

# Feature detection flags
ADMIN_PERMISSION_COLUMNS_SUPPORTED = True
USER_TASK_SUBMISSION_TEXT_SUPPORTED = True


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
    
    # YouTube Settings Columns
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None
    
    verification_data: Optional[dict] = None  # Added for YouTube/quest settings


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
    is_active: bool = True
    verification_required: bool = False
    
    # YouTube Settings Columns
    youtube_video_id: Optional[str] = None
    min_watch_time_seconds: Optional[int] = None
    video_duration_seconds: Optional[int] = None
    verification_code: Optional[str] = None
    code_display_time_seconds: Optional[int] = None
    
    verification_data: Optional[dict] = None


class RewardCreate(BaseModel):
    title: str
    description: Optional[str]
    reward_type: str
    points_cost: int
    quantity_available: Optional[int]


class AdminCreateRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None
    is_super_admin: bool = False
    permissions: Optional[List[str]] = None


class AdminUpdateRequest(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_super_admin: Optional[bool] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


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


def parse_permissions(raw_permissions) -> List[str]:
    """Convert stored permissions text into a cleaned list"""
    if not raw_permissions:
        return []
    if isinstance(raw_permissions, list):
        return [perm for perm in raw_permissions if perm]
    return [perm.strip() for perm in str(raw_permissions).split(',') if perm.strip()]


def serialize_permissions(permissions: Optional[List[str]]) -> str:
    """Serialize permissions into a comma-delimited string"""
    if not permissions:
        return ""
    cleaned = [perm.strip() for perm in permissions if perm and perm.strip()]
    seen = set()
    deduped = []
    for perm in cleaned:
        if perm not in seen:
            seen.add(perm)
            deduped.append(perm)
    return ','.join(deduped)


def derive_permissions_from_role(role: Optional[str]) -> List[str]:
    """Provide default permission set for legacy role-only setups"""
    if not role:
        return []
    role = role.lower()
    if role == "super_admin":
        return ["quests", "users", "verification", "loot", "server"]
    if role in ("admin", "manager"):
        return ["quests", "users", "verification"]
    if role in ("moderator", "verifier"):
        return ["verification"]
    return []


def format_admin_record(record: dict) -> dict:
    """Standardize admin records for API responses"""
    if not record:
        return {}
    is_super_admin = bool(record.get("is_super_admin") or record.get("role") == "super_admin")
    permissions = parse_permissions(record.get("permissions"))
    if not permissions:
        permissions = derive_permissions_from_role(record.get("role"))
    return {
        "id": record.get("id"),
        "username": record.get("username"),
        "role": record.get("role") or ("super_admin" if is_super_admin else "admin"),
        "is_super_admin": is_super_admin,
        "is_active": record.get("is_active", True),
        "permissions": permissions,
        "created_at": record.get("created_at"),
        "last_login": record.get("last_login"),
    }


def ensure_super_admin(admin_record: dict):
    """Ensure that the caller has super admin privileges"""
    if not admin_record:
        raise HTTPException(status_code=403, detail="Invalid admin context")
    if admin_record.get("is_super_admin") or admin_record.get("role") == "super_admin":
        return
    raise HTTPException(status_code=403, detail="Only super admins can manage admin accounts")


def is_permission_column_error(error: Exception) -> bool:
    if isinstance(error, UndefinedColumn):
        return True
    message = str(error).lower()
    if "permissions" in message or "is_super_admin" in message:
        return True
    return False


def sanitize_permission_payload(payload: dict) -> dict:
    cleaned = payload.copy()
    cleaned.pop("permissions", None)
    cleaned.pop("is_super_admin", None)
    return cleaned


def insert_admin_record(payload: dict):
    """Insert admin record with graceful fallback when columns are missing"""
    global ADMIN_PERMISSION_COLUMNS_SUPPORTED
    working_payload = payload.copy()
    if not ADMIN_PERMISSION_COLUMNS_SUPPORTED:
        working_payload = sanitize_permission_payload(working_payload)
    try:
        return supabase.table("admin_users").insert(working_payload).execute()
    except Exception as exc:
        if ADMIN_PERMISSION_COLUMNS_SUPPORTED and is_permission_column_error(exc):
            ADMIN_PERMISSION_COLUMNS_SUPPORTED = False
            working_payload = sanitize_permission_payload(payload)
            return supabase.table("admin_users").insert(working_payload).execute()
        raise


def update_admin_record(admin_id: str, payload: dict):
    """Update admin record with graceful fallback when columns are missing"""
    global ADMIN_PERMISSION_COLUMNS_SUPPORTED
    working_payload = payload.copy()
    if not ADMIN_PERMISSION_COLUMNS_SUPPORTED:
        working_payload = sanitize_permission_payload(working_payload)
    try:
        return supabase.table("admin_users").update(working_payload).eq("id", admin_id).execute()
    except Exception as exc:
        if ADMIN_PERMISSION_COLUMNS_SUPPORTED and is_permission_column_error(exc):
            ADMIN_PERMISSION_COLUMNS_SUPPORTED = False
            working_payload = sanitize_permission_payload(payload)
            return supabase.table("admin_users").update(working_payload).eq("id", admin_id).execute()
        raise


def is_submission_text_error(error: Exception) -> bool:
    return "submission_text" in str(error).lower()


def safe_user_task_update(update_data: dict, user_task_id: str):
    """Update user_tasks rows while handling optional submission_text column"""
    global USER_TASK_SUBMISSION_TEXT_SUPPORTED
    working_payload = update_data.copy()
    if not USER_TASK_SUBMISSION_TEXT_SUPPORTED:
        working_payload.pop("submission_text", None)
    try:
        return supabase.table("user_tasks").update(working_payload).eq("id", user_task_id).execute()
    except Exception as exc:
        if USER_TASK_SUBMISSION_TEXT_SUPPORTED and is_submission_text_error(exc):
            USER_TASK_SUBMISSION_TEXT_SUPPORTED = False
            working_payload.pop("submission_text", None)
            return supabase.table("user_tasks").update(working_payload).eq("id", user_task_id).execute()
        raise


def safe_user_task_insert(insert_data: dict):
    """Insert user_tasks rows while handling optional submission_text column"""
    global USER_TASK_SUBMISSION_TEXT_SUPPORTED
    working_payload = insert_data.copy()
    if not USER_TASK_SUBMISSION_TEXT_SUPPORTED:
        working_payload.pop("submission_text", None)
    try:
        return supabase.table("user_tasks").insert(working_payload).execute()
    except Exception as exc:
        if USER_TASK_SUBMISSION_TEXT_SUPPORTED and is_submission_text_error(exc):
            USER_TASK_SUBMISSION_TEXT_SUPPORTED = False
            working_payload.pop("submission_text", None)
            return supabase.table("user_tasks").insert(working_payload).execute()
        raise


def enforce_manual_submission_rules(task_payload: dict):
    """Ensure manual review quests always use text/link submissions"""
    if task_payload.get("task_type") != "manual_review":
        return
    verification_data = task_payload.get("verification_data") or {}
    instructions = verification_data.get("instructions", "")
    verification_data.update({
        "method": "manual_review",
        "submission_type": "text",
        "requires_approval": True,
        "instructions": instructions.strip() if isinstance(instructions, str) else instructions
    })
    task_payload["verification_data"] = verification_data
    task_payload["verification_required"] = True
    if not task_payload.get("platform"):
        task_payload["platform"] = "manual"


URL_CAPTURE_PATTERN = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)


def extract_first_url(value: Optional[str]) -> Optional[str]:
    """Return the first probable URL inside a submission text"""
    if not value or not isinstance(value, str):
        return None
    match = URL_CAPTURE_PATTERN.search(value)
    if not match:
        return None
        url = match.group(1).rstrip(").,]\"'\n")
    return url


@app.get("/api/status/servers")
async def get_server_status():
    """Detailed server + database status used by the dashboard cards"""
    api_latency = 0.0
    db_status = {
        "status": "error",
        "message": "OFFLINE",
        "latency_ms": None,
        "port_label": "PostgreSQL"
    }

    # Measure lightweight API latency (this endpoint already proves availability)
    api_start = time.perf_counter()
    api_latency = round((time.perf_counter() - api_start) * 1000, 2)

    # Check database connectivity with a simple query
    conn = None
    try:
        db_start = time.perf_counter()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        conn = None
        db_latency = round((time.perf_counter() - db_start) * 1000, 2)
        db_status = {
            "status": "connected",
            "message": "CONNECTED",
            "latency_ms": db_latency,
            "port_label": "PostgreSQL"
        }
    except (OperationalError, Exception) as exc:
        if conn:
            conn.close()
        db_status = {
            "status": "error",
            "message": "OFFLINE",
            "latency_ms": None,
            "port_label": "PostgreSQL",
            "error": str(exc)
        }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "frontend": {
            "status": "running",
            "message": "RUNNING",
            "port_label": "Port 8080",
        },
        "api": {
            "status": "running",
            "message": "RUNNING",
            "latency_ms": api_latency,
            "port_label": "Port 8080"
        },
        "database": db_status,
        "performance": {
            "status": "ok" if db_status["status"] != "error" else "degraded",
            "message": "SYSTEM STABLE" if db_status["status"] != "error" else "CHECK DATABASE"
        }
    }


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

@app.get("/api/health")
async def api_health_check():
    """API Health check endpoint"""
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


@app.get("/api/auth/verify")
async def verify_token(admin=Depends(get_current_admin)):
    """Verify admin token is valid"""
    return {
        "valid": True,
        "username": admin["username"],
        "message": "Token is valid"
    }


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


@app.get("/api/users/telegram/username/{username}")
async def get_user_by_username(username: str):
    """Get user by Telegram username (for validation)"""
    try:
        # Remove @ if present
        clean_username = username.strip().replace('@', '')
        
        print(f"🔍 Looking up username: '{clean_username}'")
        
        # Search in database - use eq with case-insensitive search
        # First try exact match (case-sensitive)
        response = supabase.table("users").select("*").eq("username", clean_username).execute()
        
        # If not found, try case-insensitive
        if not response.data or len(response.data) == 0:
            print(f"   Exact match not found, trying case-insensitive...")
            response = supabase.table("users").select("*").execute()
            
            # Filter manually for case-insensitive match
            matching_users = [
                user for user in response.data 
                if user.get('username', '').lower() == clean_username.lower()
            ]
            
            if matching_users:
                user = matching_users[0]
                print(f"   ✅ Found user: {user.get('username')} (telegram_id: {user.get('telegram_id')})")
                return {
                    "telegram_id": user.get('telegram_id'),
                    "username": user.get('username'),
                    "found": True
                }
            else:
                print(f"   ❌ No user found with username: {clean_username}")
                raise HTTPException(status_code=404, detail="Username not found")
        else:
            user = response.data[0]
            print(f"   ✅ Found user: {user.get('username')} (telegram_id: {user.get('telegram_id')})")
            # Return minimal info for validation
            return {
                "telegram_id": user.get('telegram_id'),
                "username": user.get('username'),
                "found": True
            }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error looking up username: {e}")
        raise HTTPException(status_code=500, detail="Error looking up username")


@app.patch("/api/users/{telegram_id}/profile")
async def update_user_profile(telegram_id: int, data: dict):
    """Update user profile (e.g., save Twitter username)"""
    try:
        # Get user by telegram_id
        user = DatabaseService.get_user_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare update data
        update_data = {}
        
        # Allow updating twitter_username
        if 'twitter_username' in data:
            update_data['twitter_username'] = data['twitter_username']
        
        # Allow updating other profile fields if needed
        if 'instagram_username' in data:
            update_data['instagram_username'] = data['instagram_username']
        
        if 'discord_username' in data:
            update_data['discord_username'] = data['discord_username']
        
        # Update the user profile
        if update_data:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = supabase.table("users").update(update_data).eq("id", user['id']).execute()
            
            if result.data:
                return {"success": True, "message": "Profile updated successfully", "data": result.data[0]}
            else:
                return {"success": False, "message": "Failed to update profile"}
        else:
            return {"success": False, "message": "No valid fields to update"}
            
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@app.get("/api/users/{telegram_id}/notifications")
async def get_user_notifications(telegram_id: int, unread_only: bool = False):
    """Get user notifications"""
    user = DatabaseService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = DatabaseService.get_user_notifications(user['id'], unread_only)
    return notifications


@app.get("/api/users/{telegram_id}/tasks")
async def get_user_task_history(telegram_id: int):
    """Get user's quest activity history"""
    user = DatabaseService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all user tasks
    user_tasks_response = supabase.table("user_tasks").select("*").eq("user_id", user['id']).order("updated_at", desc=True).execute()
    
    # Get all tasks to create a lookup map
    tasks_response = supabase.table("tasks").select("*").execute()
    tasks_map = {task['id']: task for task in tasks_response.data}
    
    # Format the response by combining user_tasks with task details
    activities = []
    for user_task in user_tasks_response.data:
        task_id = user_task.get('task_id')
        task = tasks_map.get(task_id, {})
        activities.append({
            "id": user_task.get('id'),
            "task_id": task_id,
            "task_title": task.get('title', 'Unknown Quest'),
            "task_platform": task.get('platform'),
            "status": user_task.get('status'),
            "points_earned": user_task.get('points_earned', 0),
            "completed_at": user_task.get('completed_at'),
            "created_at": user_task.get('created_at'),
            "updated_at": user_task.get('updated_at')
        })
    
    return activities


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
    
    # Persisted submission artifacts for manual verification
    proof_url = request.get('proof_url')
    submission_text = request.get('submission_text')

    if isinstance(proof_url, str):
        proof_url = proof_url.strip()
        if not proof_url:
            proof_url = None

    if isinstance(submission_text, str):
        submission_text = submission_text.strip()
        if submission_text:
            submission_text = submission_text[:2000]
        else:
            submission_text = None

    # Perform verification based on task_type
    verification_success = False
    verification_message = "Verification pending"
    needs_pending = False  # Initialize here - will be set to True only for tasks requiring review
    pending_status = None
    
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
    
    # Telegram membership verification (telegram_join_group, telegram_join_channel, telegram)
    elif task_type.startswith('telegram_') or task_type == 'telegram' or task.get('platform') == 'telegram':
        try:
            import requests
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            provided_username = request.get('telegram_username', '').strip().replace('@', '')
            
            print(f"\n🔍 Telegram Verification Debug:")
            print(f"   Task ID: {task_id}")
            print(f"   Task Type: {task_type}")
            print(f"   Platform: {task.get('platform')}")
            print(f"   User Telegram ID: {telegram_id}")
            print(f"   Provided Username: @{provided_username}" if provided_username else "   Provided Username: (not provided)")
            print(f"   Bot Token: {bot_token[:20] if bot_token else 'NOT SET'}...")
            
            if not bot_token:
                print("❌ Bot token not configured!")
                return {"success": False, "message": "Telegram bot not configured"}
            
            if not provided_username:
                print("❌ Telegram username not provided!")
                return {"success": False, "message": "Please provide your Telegram username"}
            
            chat_id = verification_data.get('chat_id')
            print(f"   Chat ID: {chat_id}")
            print(f"   Verification Data: {verification_data}")
            
            if not chat_id:
                print("❌ Chat ID not found in verification_data!")
                return {"success": False, "message": "Chat ID not configured in task"}
            
            # Use Telegram Bot API to check membership
            url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
            params = {
                "chat_id": chat_id,
                "user_id": telegram_id
            }
            
            print(f"   API URL: {url[:60]}...")
            print(f"   Params: {params}")
            print(f"   Calling Telegram Bot API...")
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Data: {data}")
            
            if data.get('ok'):
                member_status = data.get('result', {}).get('status')
                user_info = data.get('result', {}).get('user', {})
                print(f"   Member Status: {member_status}")
                print(f"   User Info: {user_info}")
                
                # Valid statuses: creator, administrator, member, restricted, left, kicked
                if member_status in ['creator', 'administrator', 'member', 'restricted']:
                    print(f"✅ User is a member! Status: {member_status}")
                    
                    # Get user's display name and username from Telegram
                    user_display_name = user_info.get('first_name', 'User')
                    if user_info.get('last_name'):
                        user_display_name += f" {user_info.get('last_name')}"
                    telegram_username = user_info.get('username', '').replace('@', '')
                    
                    print(f"   Telegram User Info:")
                    print(f"   - ID: {telegram_id}")
                    print(f"   - Name: {user_display_name}")
                    print(f"   - Username from Telegram API: @{telegram_username}" if telegram_username else "   - Username: (none)")
                    print(f"   - Username provided by user: @{provided_username}")
                    
                    # Verify that the provided username matches the Telegram API username
                    if telegram_username and provided_username:
                        if telegram_username.lower() != provided_username.lower():
                            verification_success = False
                            verification_message = f"❌ Username mismatch! You entered @{provided_username} but your Telegram username is @{telegram_username}"
                            print(f"   ❌ Username mismatch: Provided @{provided_username}, Actual @{telegram_username}")
                            return {"success": False, "message": verification_message}
                        else:
                            print(f"   ✅ Username matches: @{provided_username}")
                    elif not telegram_username:
                        # User has no username set in Telegram
                        verification_success = False
                        verification_message = "❌ You don't have a Telegram username set! Please set a username in Telegram Settings first."
                        print(f"   ❌ User has no Telegram username")
                        return {"success": False, "message": verification_message}
                    
                    # Step 1: Check against users.json file
                    import json
                    users_json_path = 'users.json'
                    users_json_valid = False
                    
                    try:
                        if os.path.exists(users_json_path):
                            with open(users_json_path, 'r') as f:
                                users_data = json.load(f)
                                
                            # Check if user exists in users.json with matching telegram_id
                            user_in_json = None
                            for json_user in users_data.get('users', []):
                                if str(json_user.get('telegram_id')) == str(telegram_id):
                                    user_in_json = json_user
                                    break
                            
                            if user_in_json:
                                print(f"   ✅ User found in users.json")
                                print(f"      - Stored username: {user_in_json.get('username', 'N/A')}")
                                
                                # Verify username matches (if both exist)
                                stored_username = user_in_json.get('username', '').replace('@', '')
                                if telegram_username and stored_username:
                                    if stored_username.lower() == telegram_username.lower():
                                        users_json_valid = True
                                        print(f"   ✅ Username matches in users.json!")
                                    else:
                                        print(f"   ⚠️  Username mismatch: JSON has @{stored_username}, Telegram has @{telegram_username}")
                                else:
                                    # If no username to compare, just verify ID match is enough
                                    users_json_valid = True
                                    print(f"   ✅ Telegram ID matches in users.json!")
                            else:
                                print(f"   ❌ User NOT found in users.json (telegram_id: {telegram_id})")
                        else:
                            print(f"   ⚠️  users.json file not found - creating new one")
                            users_data = {"users": []}
                            
                    except Exception as json_error:
                        print(f"   ⚠️  Error reading users.json: {str(json_error)}")
                        users_json_valid = False
                    
                    # Step 2: Check against Supabase users table
                    database_valid = False
                    try:
                        db_user = supabase.table("users").select("*").eq("telegram_id", str(telegram_id)).execute()
                        
                        if db_user.data and len(db_user.data) > 0:
                            db_user_record = db_user.data[0]
                            print(f"   ✅ User found in database")
                            print(f"      - User ID: {db_user_record.get('id')}")
                            print(f"      - Username: {db_user_record.get('username', 'N/A')}")
                            print(f"      - Total XP: {db_user_record.get('total_xp', 0)}")
                            
                            # Verify username matches (if both exist)
                            stored_db_username = db_user_record.get('username', '').replace('@', '')
                            if telegram_username and stored_db_username:
                                if stored_db_username.lower() == telegram_username.lower():
                                    database_valid = True
                                    print(f"   ✅ Username matches in database!")
                                else:
                                    print(f"   ⚠️  Username mismatch: DB has @{stored_db_username}, Telegram has @{telegram_username}")
                            else:
                                # If no username to compare, ID match is enough
                                database_valid = True
                                print(f"   ✅ Telegram ID matches in database!")
                        else:
                            print(f"   ❌ User NOT found in database (telegram_id: {telegram_id})")
                            
                    except Exception as db_error:
                        print(f"   ⚠️  Error checking database: {str(db_error)}")
                        database_valid = False
                    
                    # Step 3: Verify user exists in both sources
                    print(f"\n   📋 Verification Summary:")
                    print(f"      - Telegram membership: ✅ Verified")
                    print(f"      - users.json check: {'✅ Valid' if users_json_valid else '❌ Not found or mismatch'}")
                    print(f"      - Database check: {'✅ Valid' if database_valid else '❌ Not found or mismatch'}")
                    
                    if users_json_valid and database_valid:
                        verification_success = True
                        verification_message = f"✅ Full verification successful! Welcome to {verification_data.get('chat_name', 'the group')}"
                        print(f"\n   🎉 VERIFICATION PASSED - User authenticated from all sources!")
                        
                        # Check quest type from verification_data to determine if announcement is needed
                        quest_type = verification_data.get('type', '').lower()
                        print(f"   Quest type from verification_data: {quest_type}")
                        
                        # Only send announcement for join_group, not for join_channel
                        if quest_type == 'join_group':
                            print(f"   📢 Quest type is 'join_group' - sending announcement...")
                            try:
                                # Build announcement message with user mention
                                user_mention = f"[{user_display_name}](tg://user?id={telegram_id})"
                                
                                announcement = f"🎉 **Quest Verified!**\n\n"
                                announcement += f"✅ {user_mention}"
                                if telegram_username:
                                    announcement += f" (@{telegram_username})"
                                announcement += f" has successfully completed the quest!\n\n"
                                announcement += f"📍 Group: **{verification_data.get('chat_name', 'Brgy Tamago')}**\n"
                                announcement += f"🎮 Quest: **{task.get('title', 'Join Quest')}**\n"
                                announcement += f"💎 Reward: **{task.get('points_reward', 0)} XP**\n\n"
                                announcement += f"� Verified user ready to claim reward! 🚀"
                            
                                
                                # Send message to the group
                                send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                                send_params = {
                                    "chat_id": chat_id,
                                    "text": announcement,
                                    "parse_mode": "Markdown"
                                }
                                
                                print(f"   📢 Sending announcement to group...")
                                announce_response = requests.post(send_url, json=send_params, timeout=10)
                                announce_data = announce_response.json()
                                
                                if announce_data.get('ok'):
                                    print(f"   ✅ Announcement sent successfully!")
                                else:
                                    print(f"   ⚠️  Announcement failed: {announce_data.get('description')}")
                            except Exception as announce_error:
                                print(f"   ⚠️  Failed to send announcement: {str(announce_error)}")
                                # Don't fail the verification if announcement fails
                        else:
                            print(f"   ℹ️  Quest type is '{quest_type}' - skipping announcement (only for join_group)")
                    else:
                        verification_success = False
                        reasons = []
                        if not users_json_valid:
                            reasons.append("not found in users.json")
                        if not database_valid:
                            reasons.append("not found in database")
                        
                        verification_message = f"❌ Verification failed: User {' and '.join(reasons)}. Please ensure you're registered in Quest Hub first!"
                        print(f"\n   ❌ VERIFICATION FAILED - User not authenticated from all sources")
                else:
                    verification_success = False
                    verification_message = f"❌ You are not a member of {verification_data.get('chat_name', 'the group')}. Please join first! (Status: {member_status})"
                    print(f"❌ Verification failed! User status is: {member_status}")
            else:
                error_description = data.get('description', 'Unknown error')
                error_code = data.get('error_code', 'N/A')
                
                print(f"❌ Telegram API returned error!")
                print(f"   Error Code: {error_code}")
                print(f"   Error Description: {error_description}")
                
                # Provide user-friendly error messages
                if 'bot is not a member' in error_description.lower() or error_code == 403:
                    verification_message = "❌ Bot is not in the group. Please contact admin to add the bot first."
                    print(f"   Reason: Bot not added to group")
                elif 'chat not found' in error_description.lower() or error_code == 400:
                    verification_message = "❌ Group not found. Please check the group link and try again."
                    print(f"   Reason: Chat ID incorrect or group doesn't exist")
                elif 'user not found' in error_description.lower():
                    verification_message = "❌ User not found. Please make sure you're using the correct Telegram account."
                    print(f"   Reason: User ID incorrect")
                else:
                    verification_message = f"❌ Verification failed: {error_description}"
                
                print(f"   Possible solutions:")
                print(f"   1. Make sure bot is added to the group/channel")
                print(f"   2. Verify chat_id is correct in quest configuration")
                print(f"   3. Check if user has actually joined the group")
                print(f"   4. For channels, bot needs admin rights to check membership")
                
        except Exception as e:
            verification_message = f"Telegram verification error: {str(e)}"
            print(f"💥 Exception during Telegram verification: {str(e)}")
            import traceback
            traceback.print_exc()
            
    # YouTube video watch verification - supports both 'youtube' and 'youtube_watch' task types
    elif task_type in ['youtube', 'youtube_watch']:
        video_id = extract_youtube_video_id(task.get('url', ''))
        if not video_id:
            return {"success": False, "message": "Invalid YouTube URL"}
        
        # Get verification method
        method = verification_data.get('method', 'video_code')
        
        # For video_code method, require code verification
        if method == 'video_code' or method == 'youtube_code':
            # Accept both 'verification_code' and 'code' field names
            verification_code = request.get('verification_code', request.get('code', '')).strip()
            
            # Get expected code from task columns first, then fall back to verification_data
            expected_code = task.get('verification_code', '').strip()
            if not expected_code:
                expected_code = verification_data.get('verification_code', verification_data.get('code', '')).strip()
            
            if not verification_code:
                return {
                    "success": False, 
                    "message": "Please watch the video and enter the verification code shown in it",
                    "requires_code": True
                }
            
            # Check if code matches (case-insensitive)
            if verification_code.upper() != expected_code.upper():
                return {
                    "success": False,
                    "message": "❌ Incorrect verification code. Watch the video carefully!",
                    "requires_code": True
                }
            
            # Code is correct, check if already completed
            existing_completion = supabase.table("user_tasks").select("*").eq("user_id", user['id']).eq("task_id", task_id).eq("status", "completed").execute()
            if existing_completion.data:
                return {"success": False, "message": "You have already completed this task"}
            
            # Mark as completed immediately (code verified)
            verification_success = True
            verification_message = "✅ Video quest completed! Code verified."
            needs_pending = False  # Code is correct, complete the quest immediately
        
        # For time_delay_code method, use video_views tracking (if available)
        elif method == 'time_delay_code':
            # Check if code was provided
            submitted_code = request.get('code', '').strip()
            expected_code = verification_data.get('code', '').strip()
            
            if not submitted_code:
                # No code submitted yet - return instructions
                verification_success = False
                verification_message = "Watch the video and enter the verification code shown"
                needs_pending = True
            elif submitted_code.upper() != expected_code.upper():
                # Wrong code
                return {
                    "success": False,
                    "message": "❌ Invalid verification code. Please watch the video carefully and try again."
                }
            else:
                # Correct code!
                verification_success = True
                verification_message = "✅ Video quest completed! Code verified."
                needs_pending = False  # Code is correct, complete the quest
            
            # Optional: Use video_views tracking if table exists
            try:
                # Check if user already has an active watch session
                existing_view = supabase.table("video_views").select("*").eq("user_id", user['id']).eq("task_id", task_id).eq("status", "watching").execute()
                
                if existing_view.data and not submitted_code:
                    return {
                        "success": True,
                        "message": "Continue watching and enter the code shown in the video",
                        "requires_code": True,
                        "video_id": video_id,
                        "view_id": existing_view.data[0]['id']
                    }
                
                # Create new video view session (only if no code submitted yet)
                if not submitted_code:
                    secret_code = verification_data.get('verification_code', verification_data.get('code', 'SECRET'))
                    min_watch_time = verification_data.get('min_watch_time', verification_data.get('min_watch_time_seconds', 120))
                    
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
            except Exception as video_tracking_error:
                # Video tracking is optional - continue without it if table doesn't exist
                print(f"Video tracking disabled: {video_tracking_error}")
                pass
        else:
            # Unknown YouTube method
            verification_success = False
            verification_message = "YouTube quest verification method not properly configured"
    
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
        if not submission_text and not proof_url:
            return {"success": False, "message": "Please include your link or short notes before submitting."}
        if not proof_url:
            proof_url = extract_first_url(submission_text or "")
        # Create pending user_task for admin review
        verification_success = True
        verification_message = "Task submitted for admin review"
        needs_pending = True
        pending_status = 'submitted'
    
    # Generic/other task types
    else:
        verification_success = True
        verification_message = "Task submitted for verification"
    
    # Create or update user_task record
    if verification_success:
        # Determine if task needs pending status (YouTube watch, manual review)
        # YouTube tasks are only pending if code wasn't submitted yet
        # Manual review tasks always need pending status
        if task_type == 'youtube_watch':
            # If code was submitted and verified, don't keep it pending
            submitted_code = request.get('code', '').strip()
            needs_pending = not bool(submitted_code)  # Only pending if no code submitted
        elif task_type == 'manual_review':
            needs_pending = True
            pending_status = pending_status or 'submitted'
        # For all other task types, needs_pending should already be set correctly above
        
        # Check if pending task exists
        pending_task = supabase.table("user_tasks").select("*").eq("user_id", user['id']).eq("task_id", task_id).execute()
        
        status_value = pending_status if (needs_pending and pending_status) else ("pending" if needs_pending else "completed")

        if pending_task.data:
            # Update existing
            user_task_id = pending_task.data[0]['id']
            update_data = {
                "status": status_value,
                "completed_at": None if needs_pending else datetime.now(timezone.utc).isoformat()
            }
            # Add points_earned for completed tasks
            if not needs_pending:
                update_data["points_earned"] = task.get('points_reward', 0)
            if proof_url:
                update_data["proof_url"] = proof_url
            if submission_text:
                update_data["submission_text"] = submission_text
            
            safe_user_task_update(update_data, user_task_id)
        else:
            # Create new
            user_task_data = {
                "user_id": user['id'],
                "task_id": task_id,
                "status": status_value,
                "completed_at": None if needs_pending else datetime.now(timezone.utc).isoformat()
            }
            # Add points_earned for completed tasks
            if not needs_pending:
                user_task_data["points_earned"] = task.get('points_reward', 0)
            if proof_url:
                user_task_data["proof_url"] = proof_url
            if submission_text:
                user_task_data["submission_text"] = submission_text
            
            safe_user_task_insert(user_task_data)
        
        # Award points immediately for completed tasks (not YouTube or manual pending)
        if not needs_pending:
            points_reward = task.get('points_reward', 0)
            new_points = user['points'] + points_reward
            supabase.table("users").update({"points": new_points}).eq("id", user['id']).execute()
            
            return {
                "success": True,
                "message": verification_message,
                "points_earned": points_reward,
                "new_total": new_points,
                "status": status_value,
                "pending_review": False
            }
        else:
            return {
                "success": True,
                "message": verification_message,
                "status": status_value,
                "pending_review": True,
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


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str, request: dict):
    """Complete a task for a user - Frontend-friendly endpoint"""
    # This endpoint wraps the /api/verify endpoint for easier frontend integration
    telegram_id = request.get('telegram_id')
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="telegram_id is required")
    
    # Build request for verify endpoint
    verify_request = {
        'telegram_id': telegram_id,
        'task_id': task_id
    }
    
    # Pass through any additional data (like code for YouTube quests)
    for key, value in request.items():
        if key != 'telegram_id':
            verify_request[key] = value
    
    # Call the existing verify endpoint
    result = await verify_task_completion(verify_request)
    return result


@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, admin=Depends(get_current_admin)):
    """Create a new task (Admin only)"""
    import json
    import re
    
    # Auto-extract YouTube video ID from URL
    youtube_video_id = task.youtube_video_id
    if task.url and not youtube_video_id:
        # Extract video ID from various YouTube URL formats
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        # https://www.youtube.com/embed/VIDEO_ID
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, task.url)
            if match:
                youtube_video_id = match.group(1)
                break
    
    # Convert to dict and prepare for insertion
    task_data = {
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "platform": task.platform,
        "url": task.url,
        "points_reward": task.points_reward,
        "is_bonus": task.is_bonus,
        "is_active": task.is_active,
        "verification_required": task.verification_required,
        
        # YouTube Settings Columns
        "youtube_video_id": youtube_video_id,
        "min_watch_time_seconds": task.min_watch_time_seconds,
        "video_duration_seconds": task.video_duration_seconds,
        "verification_code": task.verification_code,
        "code_display_time_seconds": task.code_display_time_seconds
    }
    
    # CRITICAL FIX: Properly handle verification_data as JSONB
    if task.verification_data is not None:
        # Ensure it's JSON-serializable and convert to proper format
        try:
            # Serialize and deserialize to validate and ensure proper JSON format
            verification_json = json.loads(json.dumps(task.verification_data))
            task_data["verification_data"] = verification_json
        except (TypeError, ValueError) as e:
            print(f"Warning: Could not serialize verification_data: {e}")
            print(f"verification_data value: {task.verification_data}")
            # Skip verification_data if it can't be serialized
            pass

    enforce_manual_submission_rules(task_data)
    
    try:
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
        
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR creating task: {e}")
        print(f"Task data: {task_data}")
        
        # Check if it's a JSONB adaptation error
        if "can't adapt type 'dict'" in error_msg or "adapt" in error_msg:
            raise HTTPException(
                status_code=500,
                detail="Failed to save quest verification data. Please check all fields are properly filled."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskCreate, admin=Depends(get_current_admin)):
    """Update a task (Admin only)"""
    import json
    import re
    
    existing_task = DatabaseService.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Auto-extract YouTube video ID from URL
    youtube_video_id = task.youtube_video_id
    if task.url and not youtube_video_id:
        # Extract video ID from various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'[?&]v=([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, task.url)
            if match:
                youtube_video_id = match.group(1)
                break
    
    task_data = {
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "platform": task.platform,
        "url": task.url,
        "points_reward": task.points_reward,
        "is_bonus": task.is_bonus,
        "is_active": task.is_active,
        "verification_required": task.verification_required,
        
        # YouTube Settings Columns
        "youtube_video_id": youtube_video_id,
        "min_watch_time_seconds": task.min_watch_time_seconds,
        "video_duration_seconds": task.video_duration_seconds,
        "verification_code": task.verification_code,
        "code_display_time_seconds": task.code_display_time_seconds
    }
    
    # CRITICAL FIX: Properly handle verification_data as JSONB
    # Supabase/PostgREST requires JSONB to be sent as a JSON string or proper dict
    if task.verification_data:
        # Ensure it's a proper dict for JSONB column
        vd = task.verification_data
        if not isinstance(vd, dict):
            task_data['verification_data'] = dict(vd)
        else:
            # Ensure all values are JSON-serializable
            task_data['verification_data'] = json.loads(json.dumps(vd))

    enforce_manual_submission_rules(task_data)
    
    try:
        response = supabase.table("tasks").update(task_data).eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update task")
        
        return response.data[0]
        
    except APIError as e:
        error_msg = str(e).lower()
        print(f"ERROR updating task {task_id}: {e}")
        print(f"Task data: {task_data}")
        
        # If verification_data column issue, try alternative approach
        if 'verification_data' in error_msg:
            # Try updating verification_data separately using raw SQL approach
            try:
                # Update all fields except verification_data first
                basic_data = {k: v for k, v in task_data.items() if k != 'verification_data'}
                response = supabase.table("tasks").update(basic_data).eq("id", task_id).execute()
                
                # Then update verification_data separately if it exists
                if 'verification_data' in task_data and task_data['verification_data']:
                    vd_update = {"verification_data": task_data['verification_data']}
                    response = supabase.table("tasks").update(vd_update).eq("id", task_id).execute()
                
                if not response.data:
                    raise HTTPException(status_code=400, detail="Failed to update task")
                
                return response.data[0]
            except Exception as inner_e:
                print(f"Alternative update also failed: {inner_e}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to update task. Error: {str(e)}"
                )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


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
    query = supabase.table("user_tasks").select("*")
    
    if status:
        query = query.eq("status", status)
    
    user_tasks_response = query.order("created_at", desc=True).limit(100).execute()
    
    # Get users and tasks to create lookup maps
    users_response = supabase.table("users").select("*").execute()
    tasks_response = supabase.table("tasks").select("*").execute()
    
    users_map = {user['id']: user for user in users_response.data}
    tasks_map = {task['id']: task for task in tasks_response.data}
    
    # Combine the data
    result = []
    for user_task in user_tasks_response.data:
        user_task['users'] = users_map.get(user_task.get('user_id'), {})
        user_task['tasks'] = tasks_map.get(user_task.get('task_id'), {})
        result.append(user_task)
    
    return result


@app.put("/api/admin/user-tasks/{user_task_id}/verify")
async def verify_user_task(user_task_id: str, approved: bool, admin=Depends(get_current_admin)):
    """Verify a user task submission (Admin only)"""
    # Get user task
    user_task_response = supabase.table("user_tasks").select("*").eq("id", user_task_id).execute()
    
    if not user_task_response.data:
        raise HTTPException(status_code=404, detail="User task not found")
    
    user_task = user_task_response.data[0]
    
    # Get task details
    task_response = supabase.table("tasks").select("*").eq("id", user_task['task_id']).execute()
    if not task_response.data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_response.data[0]
    
    if approved:
        # Award points
        points = task['points_reward']
        update_result = DatabaseService.update_user_points(user_task['user_id'], points, "earned")
        if update_result is None:
            raise HTTPException(status_code=500, detail="Failed to update user points")
        
        # Update user task
        update_data = {
            "status": "completed",
            "points_earned": update_result.get("awarded_points", points),
            "verified_at": datetime.utcnow().isoformat()
        }
        
        # Notify user
        DatabaseService.create_notification(
            user_task['user_id'],
            "Task Verified!",
            f"Your task has been verified! You earned {update_result.get('awarded_points', points)} points.",
            "task_verified"
        )
    else:
        # Reject task
        update_data = {
            "status": "rejected",
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
# ADMIN MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/admin/users")
async def get_admin_users(current_admin=Depends(get_current_admin)):
    """Get the list of admin users"""
    try:
        response = supabase.table("admin_users").select("*").order("created_at", desc=False).execute()
        admins = [format_admin_record(row) for row in (response.data or [])]
        return admins
    except APIError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin users: {exc}")


@app.post("/api/admin/create-admin", status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    admin_data: AdminCreateRequest,
    current_admin=Depends(get_current_admin)
):
    """Create a new admin user"""
    ensure_super_admin(current_admin)
    try:
        username = admin_data.username.strip()
        password = admin_data.password.strip()
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")

        existing_user = supabase.table("admin_users").select("id").eq("username", username).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Username already exists")

        is_super_admin = admin_data.is_super_admin or (admin_data.role == "super_admin")
        role = admin_data.role or ("super_admin" if is_super_admin else "admin")
        permissions = admin_data.permissions
        if is_super_admin and not permissions:
            permissions = ["quests", "users", "verification", "loot", "server"]

        new_admin = {
            "username": username,
            "password_hash": get_password_hash(password),
            "role": role,
            "permissions": serialize_permissions(permissions),
            "is_super_admin": is_super_admin,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }

        response = insert_admin_record(new_admin)
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create admin user")

        message = "Admin user created successfully"
        if not ADMIN_PERMISSION_COLUMNS_SUPPORTED:
            message += " (legacy role-only mode active)"

        return {
            "message": message,
            "admin": format_admin_record(response.data[0])
        }
    except HTTPException:
        raise
    except APIError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {exc}")


@app.delete("/api/admin/delete-admin/{admin_id}")
async def delete_admin_user(
    admin_id: str,
    current_admin=Depends(get_current_admin)
):
    """Delete an admin user"""
    ensure_super_admin(current_admin)
    try:
        if current_admin.get("id") == admin_id:
            raise HTTPException(status_code=400, detail="You cannot delete your own account")

        admin_to_delete = supabase.table("admin_users").select("*").eq("id", admin_id).execute()
        if not admin_to_delete.data:
            raise HTTPException(status_code=404, detail="Admin not found")

        target_admin = admin_to_delete.data[0]
        if target_admin.get("username") == "admin":
            raise HTTPException(status_code=403, detail="Cannot delete the main admin account")

        supabase.table("admin_users").delete().eq("id", admin_id).execute()
        return {"message": "Admin user deleted successfully"}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to delete admin: {exc}")


@app.put("/api/admin/update-admin/{admin_id}")
async def update_admin_user(
    admin_id: str,
    admin_data: AdminUpdateRequest,
    current_admin=Depends(get_current_admin)
):
    """Update admin credentials, permissions, or status"""
    try:
        current_is_super = current_admin.get("is_super_admin") or current_admin.get("role") == "super_admin"
        if not current_is_super and current_admin.get("id") != admin_id:
            raise HTTPException(status_code=403, detail="You can only update your own account")

        admin_to_update = supabase.table("admin_users").select("*").eq("id", admin_id).execute()
        if not admin_to_update.data:
            raise HTTPException(status_code=404, detail="Admin not found")

        update_data = {}

        if admin_data.password:
            update_data["password_hash"] = get_password_hash(admin_data.password)

        if admin_data.permissions is not None:
            if not current_is_super:
                raise HTTPException(status_code=403, detail="Only super admins can change permissions")
            update_data["permissions"] = serialize_permissions(admin_data.permissions)

        if admin_data.is_super_admin is not None:
            if not current_is_super:
                raise HTTPException(status_code=403, detail="Only super admins can change super admin access")
            update_data["is_super_admin"] = admin_data.is_super_admin
            if admin_data.is_super_admin:
                update_data["role"] = "super_admin"

        if admin_data.role:
            if not current_is_super:
                raise HTTPException(status_code=403, detail="Only super admins can change roles")
            update_data["role"] = admin_data.role
            update_data["is_super_admin"] = admin_data.role == "super_admin"

        if admin_data.is_active is not None:
            if not current_is_super:
                raise HTTPException(status_code=403, detail="Only super admins can activate/deactivate admins")
            update_data["is_active"] = admin_data.is_active

        if not update_data:
            return {"message": "No changes made"}
        update_admin_record(admin_id, update_data)
        refreshed = supabase.table("admin_users").select("*").eq("id", admin_id).execute()
        message = "Admin user updated successfully"
        if not ADMIN_PERMISSION_COLUMNS_SUPPORTED:
            message += " (legacy role-only mode active)"
        return {
            "message": message,
            "admin": format_admin_record(refreshed.data[0])
        }
    except HTTPException:
        raise
    except APIError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update admin: {exc}")


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
    view_response = supabase.table("video_views").select("*").eq("user_id", user_id).eq("verification_code", code).eq("status", "watching").execute()
    
    if not view_response.data:
        # No active view found - could be wrong code or no active quest
        return {"success": False, "error": "no_active_view", "message": "No active video quest found with this code"}
    
    view = view_response.data[0]
    
    # Get task details
    task_response = supabase.table("tasks").select("*").eq("id", view['task_id']).execute()
    if not task_response.data:
        return {"success": False, "error": "task_not_found", "message": "Task not found"}
    
    task = task_response.data[0]
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
        "status": "verified",
        "points_earned": task['points_reward'],
        "completed_at": now.isoformat()
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
        "points_earned": task['points_reward'],
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
