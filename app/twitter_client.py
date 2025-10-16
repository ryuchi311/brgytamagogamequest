"""
Twitter API v2 Client for Free Tier
Handles follow, like, and retweet verification
"""
import os
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import tweepy

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter API v2 client with rate limit management"""
    
    def __init__(self):
        """Initialize Twitter client with credentials from environment"""
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.account_id = os.getenv('TWITTER_ACCOUNT_ID')  # Your Twitter user ID
        self.username = os.getenv('TWITTER_USERNAME', '').lstrip('@')
        
        if not self.bearer_token:
            logger.error("TWITTER_BEARER_TOKEN not found in environment")
            self.client = None
        else:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("Twitter API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
                self.client = None
        
        # Rate limit tracking (free tier: 100 reads/month)
        self.monthly_limit = 100
        self.requests_made = 0
        self.reset_date = None
        
    def is_available(self) -> bool:
        """Check if Twitter API is available and under rate limit"""
        if not self.client:
            return False
            
        # Check if we're under monthly limit
        if self.requests_made >= self.monthly_limit:
            logger.warning(f"Twitter API monthly limit reached: {self.requests_made}/{self.monthly_limit}")
            return False
            
        return True
    
    def _increment_usage(self):
        """Track API usage"""
        self.requests_made += 1
        logger.info(f"Twitter API usage: {self.requests_made}/{self.monthly_limit}")
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get Twitter user ID from username"""
        if not self.is_available():
            return None
            
        try:
            username = username.lstrip('@')
            response = self.client.get_user(username=username)
            self._increment_usage()
            
            if response.data:
                return response.data.id
            return None
        except tweepy.errors.NotFound:
            logger.warning(f"Twitter user not found: {username}")
            return None
        except Exception as e:
            logger.error(f"Error getting user ID for {username}: {e}")
            return None
    
    def verify_follow(self, username: str) -> Dict[str, any]:
        """
        Verify if user follows your Twitter account
        
        Returns:
            {
                "success": bool,
                "is_following": bool,
                "error": str (if failed),
                "api_available": bool
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "twitter_api_unavailable",
                "message": "Twitter verification temporarily unavailable. Please use manual verification.",
                "api_available": False
            }
        
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": f"Twitter user @{username} not found"
                }
            
            # Check if user follows your account
            # API: GET /2/users/:id/following
            response = self.client.get_users_following(
                id=user_id,
                max_results=100
            )
            self._increment_usage()
            
            if response.data:
                # Check if your account ID is in their following list
                is_following = any(user.id == self.account_id for user in response.data)
            else:
                is_following = False
            
            return {
                "success": True,
                "is_following": is_following,
                "api_available": True
            }
            
        except tweepy.errors.Unauthorized:
            logger.error("Twitter API unauthorized - check credentials")
            return {
                "success": False,
                "error": "api_unauthorized",
                "message": "Twitter API authentication failed"
            }
        except tweepy.errors.TooManyRequests:
            logger.warning("Twitter API rate limit exceeded")
            return {
                "success": False,
                "error": "rate_limit",
                "message": "Twitter API rate limit reached. Please try again later.",
                "api_available": False
            }
        except Exception as e:
            logger.error(f"Error verifying follow: {e}")
            return {
                "success": False,
                "error": "api_error",
                "message": str(e)
            }
    
    def verify_like(self, username: str, tweet_id: str) -> Dict[str, any]:
        """
        Verify if user liked a specific tweet
        
        Args:
            username: Twitter username (with or without @)
            tweet_id: ID of the tweet to check
            
        Returns:
            {
                "success": bool,
                "has_liked": bool,
                "error": str (if failed)
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "twitter_api_unavailable",
                "message": "Twitter verification temporarily unavailable",
                "api_available": False
            }
        
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": f"Twitter user @{username} not found"
                }
            
            # Get users who liked the tweet
            # API: GET /2/tweets/:id/liking_users
            response = self.client.get_liking_users(tweet_id, max_results=100)
            self._increment_usage()
            
            if response.data:
                has_liked = any(user.id == user_id for user in response.data)
            else:
                has_liked = False
            
            return {
                "success": True,
                "has_liked": has_liked,
                "api_available": True
            }
            
        except tweepy.errors.NotFound:
            return {
                "success": False,
                "error": "tweet_not_found",
                "message": f"Tweet {tweet_id} not found"
            }
        except tweepy.errors.TooManyRequests:
            return {
                "success": False,
                "error": "rate_limit",
                "message": "Twitter API rate limit reached",
                "api_available": False
            }
        except Exception as e:
            logger.error(f"Error verifying like: {e}")
            return {
                "success": False,
                "error": "api_error",
                "message": str(e)
            }
    
    def verify_retweet(self, username: str, tweet_id: str) -> Dict[str, any]:
        """
        Verify if user retweeted a specific tweet
        
        Args:
            username: Twitter username
            tweet_id: ID of the tweet to check
            
        Returns:
            {
                "success": bool,
                "has_retweeted": bool,
                "error": str (if failed)
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "twitter_api_unavailable",
                "message": "Twitter verification temporarily unavailable",
                "api_available": False
            }
        
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                return {
                    "success": False,
                    "error": "user_not_found",
                    "message": f"Twitter user @{username} not found"
                }
            
            # Get users who retweeted
            # API: GET /2/tweets/:id/retweeted_by
            response = self.client.get_retweeters(tweet_id, max_results=100)
            self._increment_usage()
            
            if response.data:
                has_retweeted = any(user.id == user_id for user in response.data)
            else:
                has_retweeted = False
            
            return {
                "success": True,
                "has_retweeted": has_retweeted,
                "api_available": True
            }
            
        except tweepy.errors.NotFound:
            return {
                "success": False,
                "error": "tweet_not_found",
                "message": f"Tweet {tweet_id} not found"
            }
        except tweepy.errors.TooManyRequests:
            return {
                "success": False,
                "error": "rate_limit",
                "message": "Twitter API rate limit reached",
                "api_available": False
            }
        except Exception as e:
            logger.error(f"Error verifying retweet: {e}")
            return {
                "success": False,
                "error": "api_error",
                "message": str(e)
            }
    
    def extract_tweet_id(self, url: str) -> Optional[str]:
        """
        Extract tweet ID from Twitter URL
        
        Supports formats:
        - https://twitter.com/username/status/1234567890
        - https://x.com/username/status/1234567890
        - https://mobile.twitter.com/username/status/1234567890
        """
        try:
            # Split by '/' and find 'status' index
            parts = url.split('/')
            if 'status' in parts:
                status_index = parts.index('status')
                if status_index + 1 < len(parts):
                    tweet_id = parts[status_index + 1].split('?')[0]  # Remove query params
                    return tweet_id
            return None
        except Exception as e:
            logger.error(f"Error extracting tweet ID from {url}: {e}")
            return None
    
    def get_usage_stats(self) -> Dict[str, any]:
        """Get current API usage statistics"""
        return {
            "requests_made": self.requests_made,
            "monthly_limit": self.monthly_limit,
            "remaining": self.monthly_limit - self.requests_made,
            "percentage_used": (self.requests_made / self.monthly_limit) * 100,
            "api_available": self.is_available()
        }


# Global instance
twitter_client = TwitterClient()
