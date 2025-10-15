"""
Utility functions for the application
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional


def generate_random_code(length: int = 8, prefix: str = "") -> str:
    """Generate a random alphanumeric code"""
    characters = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return f"{prefix}{code}" if prefix else code


def generate_redemption_code(reward_type: str = "REWARD") -> str:
    """Generate a unique redemption code for rewards"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = generate_random_code(8)
    return f"{reward_type}-{timestamp}-{random_part}"


def calculate_time_ago(timestamp: datetime) -> str:
    """Calculate human-readable time ago from timestamp"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL"""
    import re
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url) is not None


def format_points(points: int) -> str:
    """Format points with thousand separators"""
    return f"{points:,}"


def calculate_rank(user_points: int, leaderboard: list) -> int:
    """Calculate user rank based on points"""
    rank = 1
    for user in leaderboard:
        if user['points'] > user_points:
            rank += 1
    return rank


def get_task_type_emoji(task_type: str) -> str:
    """Get emoji for task type"""
    emojis = {
        'social_follow': '👥',
        'like_post': '❤️',
        'share_post': '🔄',
        'watch_video': '🎥',
        'custom': '⭐'
    }
    return emojis.get(task_type, '📋')


def get_platform_emoji(platform: str) -> str:
    """Get emoji for social media platform"""
    emojis = {
        'instagram': '📷',
        'twitter': '🐦',
        'facebook': '👍',
        'youtube': '📺',
        'tiktok': '🎵'
    }
    return emojis.get(platform.lower() if platform else '', '📱')


def get_reward_type_emoji(reward_type: str) -> str:
    """Get emoji for reward type"""
    emojis = {
        'discount': '💰',
        'gift_card': '🎁',
        'exclusive_content': '⭐',
        'custom': '🎉'
    }
    return emojis.get(reward_type, '🎁')


class RateLimiter:
    """Simple rate limiter for API requests"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, user_id: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """Check if user is allowed to make a request"""
        now = datetime.utcnow()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < timedelta(seconds=window_seconds)
        ]
        
        # Check if limit exceeded
        if len(self.requests[user_id]) >= max_requests:
            return False
        
        # Add new request
        self.requests[user_id].append(now)
        return True


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = text.strip()[:max_length]
    
    # Basic HTML escaping
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text


def paginate(items: list, page: int = 1, page_size: int = 10) -> dict:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        'items': items[start_idx:end_idx],
        'page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }
