"""
Simple API client for the Telegram bot to communicate with the FastAPI backend
This avoids dependency conflicts by not importing Supabase directly
"""
import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://api:8000/api")


class BotAPIClient:
    """API client for bot to interact with the backend"""
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        try:
            response = requests.get(f"{API_URL}/users/{telegram_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            response = requests.post(f"{API_URL}/users", json=user_data)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def get_active_tasks() -> List[Dict[str, Any]]:
        """Get all active tasks"""
        try:
            response = requests.get(f"{API_URL}/tasks")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        try:
            response = requests.get(f"{API_URL}/tasks/{task_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    @staticmethod
    def complete_task(user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Complete a task for a user"""
        try:
            response = requests.post(f"{API_URL}/users/{user_id}/tasks/{task_id}/complete")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error completing task: {e}")
            return None
    
    @staticmethod
    def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
        """Get leaderboard"""
        try:
            response = requests.get(f"{API_URL}/leaderboard?limit={limit}")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    @staticmethod
    def get_active_rewards() -> List[Dict[str, Any]]:
        """Get all active rewards"""
        try:
            response = requests.get(f"{API_URL}/rewards")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting rewards: {e}")
            return []
    
    @staticmethod
    def redeem_reward(user_id: str, reward_id: str) -> Optional[Dict[str, Any]]:
        """Redeem a reward for a user"""
        try:
            response = requests.post(f"{API_URL}/users/{user_id}/rewards/{reward_id}/redeem")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error redeeming reward: {e}")
            return None
    
    @staticmethod
    def create_notification(notification_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a notification"""
        try:
            response = requests.post(f"{API_URL}/notifications", json=notification_data)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None
