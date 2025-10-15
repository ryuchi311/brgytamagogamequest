"""
Database models and Supabase client configuration
"""
import os
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


# Pydantic Models
class User(BaseModel):
    id: Optional[str] = None
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    points: int = 0
    total_earned_points: int = 0
    is_active: bool = True
    is_banned: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Task(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    task_type: str  # 'social_follow', 'like_post', 'share_post', 'watch_video', 'custom'
    platform: Optional[str] = None
    url: Optional[str] = None
    points_reward: int
    is_bonus: bool = False
    max_completions: int = 1
    verification_required: bool = False
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserTask(BaseModel):
    id: Optional[str] = None
    user_id: str
    task_id: str
    status: str = "pending"  # 'pending', 'in_progress', 'submitted', 'verified', 'completed', 'rejected'
    proof_url: Optional[str] = None
    completion_count: int = 0
    points_earned: int = 0
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Reward(BaseModel):
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    reward_type: str  # 'discount', 'gift_card', 'exclusive_content', 'custom'
    points_cost: int
    quantity_available: Optional[int] = None
    quantity_claimed: int = 0
    is_active: bool = True
    image_url: Optional[str] = None
    code_prefix: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserReward(BaseModel):
    id: Optional[str] = None
    user_id: str
    reward_id: str
    redemption_code: Optional[str] = None
    status: str = "pending"  # 'pending', 'delivered', 'used', 'expired'
    redeemed_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    used_at: Optional[datetime] = None


class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    message: str
    notification_type: Optional[str] = None
    is_read: bool = False
    is_sent: bool = False
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class AdminUser(BaseModel):
    id: Optional[str] = None
    username: str
    password_hash: str
    email: Optional[str] = None
    role: str = "admin"
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class PointsTransaction(BaseModel):
    id: Optional[str] = None
    user_id: str
    amount: int
    transaction_type: str  # 'earned', 'spent', 'bonus', 'refund', 'adjustment'
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class ActivityLog(BaseModel):
    id: Optional[str] = None
    user_id: str
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None


# Database Service Class
class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[dict]:
        """Get user by Telegram ID"""
        response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def create_user(user_data: dict) -> dict:
        """Create a new user"""
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def update_user_points(user_id: str, points_change: int, transaction_type: str = "earned") -> dict:
        """Update user points and create transaction log"""
        # Get current user
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_response.data:
            return None
        
        user = user_response.data[0]
        new_points = user["points"] + points_change
        
        # Update user points
        update_data = {"points": new_points}
        if points_change > 0:
            update_data["total_earned_points"] = user["total_earned_points"] + points_change
        
        supabase.table("users").update(update_data).eq("id", user_id).execute()
        
        # Create transaction log
        transaction_data = {
            "user_id": user_id,
            "amount": points_change,
            "transaction_type": transaction_type
        }
        supabase.table("points_transactions").insert(transaction_data).execute()
        
        return {"points": new_points, "total_earned_points": update_data.get("total_earned_points", user["total_earned_points"])}
    
    @staticmethod
    def get_active_tasks() -> List[dict]:
        """Get all active tasks"""
        response = supabase.table("tasks").select("*").eq("is_active", True).execute()
        return response.data or []
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[dict]:
        """Get task by ID"""
        response = supabase.table("tasks").select("*").eq("id", task_id).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def complete_task(user_id: str, task_id: str, proof_url: Optional[str] = None) -> dict:
        """Mark task as completed for user"""
        # Check if user_task exists
        existing = supabase.table("user_tasks").select("*").eq("user_id", user_id).eq("task_id", task_id).execute()
        
        task = DatabaseService.get_task_by_id(task_id)
        if not task:
            return {"error": "Task not found"}
        
        if existing.data:
            # Update existing
            update_data = {
                "status": "completed" if not task["verification_required"] else "submitted",
                "completion_count": existing.data[0]["completion_count"] + 1,
                "completed_at": datetime.utcnow().isoformat()
            }
            if proof_url:
                update_data["proof_url"] = proof_url
            
            if not task["verification_required"]:
                update_data["points_earned"] = task["points_reward"]
                DatabaseService.update_user_points(user_id, task["points_reward"], "earned")
            
            response = supabase.table("user_tasks").update(update_data).eq("id", existing.data[0]["id"]).execute()
        else:
            # Create new
            insert_data = {
                "user_id": user_id,
                "task_id": task_id,
                "status": "completed" if not task["verification_required"] else "submitted",
                "completion_count": 1,
                "completed_at": datetime.utcnow().isoformat()
            }
            if proof_url:
                insert_data["proof_url"] = proof_url
            
            if not task["verification_required"]:
                insert_data["points_earned"] = task["points_reward"]
                DatabaseService.update_user_points(user_id, task["points_reward"], "earned")
            
            response = supabase.table("user_tasks").insert(insert_data).execute()
        
        return response.data[0] if response.data else None
    
    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[dict]:
        """Get top users by points"""
        response = supabase.table("users").select("*").eq("is_active", True).eq("is_banned", False).order("points", desc=True).limit(limit).execute()
        return response.data or []
    
    @staticmethod
    def get_active_rewards() -> List[dict]:
        """Get all active rewards"""
        response = supabase.table("rewards").select("*").eq("is_active", True).execute()
        return response.data or []
    
    @staticmethod
    def redeem_reward(user_id: str, reward_id: str) -> dict:
        """Redeem a reward for user"""
        # Get user
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_response.data:
            return {"error": "User not found"}
        
        user = user_response.data[0]
        
        # Get reward
        reward_response = supabase.table("rewards").select("*").eq("id", reward_id).execute()
        if not reward_response.data:
            return {"error": "Reward not found"}
        
        reward = reward_response.data[0]
        
        # Check if user has enough points
        if user["points"] < reward["points_cost"]:
            return {"error": "Insufficient points"}
        
        # Check if reward is available
        if reward["quantity_available"] and reward["quantity_claimed"] >= reward["quantity_available"]:
            return {"error": "Reward not available"}
        
        # Deduct points
        DatabaseService.update_user_points(user_id, -reward["points_cost"], "spent")
        
        # Generate redemption code
        import random
        import string
        code_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        redemption_code = f"{reward.get('code_prefix', 'REWARD')}-{code_suffix}"
        
        # Create user reward
        user_reward_data = {
            "user_id": user_id,
            "reward_id": reward_id,
            "redemption_code": redemption_code,
            "status": "pending"
        }
        supabase.table("user_rewards").insert(user_reward_data).execute()
        
        # Update reward claimed count
        supabase.table("rewards").update({"quantity_claimed": reward["quantity_claimed"] + 1}).eq("id", reward_id).execute()
        
        return {"success": True, "redemption_code": redemption_code}
    
    @staticmethod
    def create_notification(user_id: str, title: str, message: str, notification_type: str = "system") -> dict:
        """Create a notification for user"""
        notification_data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "notification_type": notification_type
        }
        response = supabase.table("notifications").insert(notification_data).execute()
        return response.data[0] if response.data else None
    
    @staticmethod
    def get_user_notifications(user_id: str, unread_only: bool = False) -> List[dict]:
        """Get user notifications"""
        query = supabase.table("notifications").select("*").eq("user_id", user_id)
        if unread_only:
            query = query.eq("is_read", False)
        response = query.order("created_at", desc=True).execute()
        return response.data or []
