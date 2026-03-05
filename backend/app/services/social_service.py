"""
Personal AI Command Center - Social Media Integration Service
"""
import tweepy
from typing import List, Optional, Dict
from datetime import datetime
import asyncio

from app.core.config import settings


class TwitterService:
    """Twitter/X API integration"""
    
    def __init__(self):
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_secret = settings.TWITTER_ACCESS_SECRET
        self.client = None
        self.api = None
    
    async def connect(self) -> bool:
        """Connect to Twitter API"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("Twitter credentials not configured")
            return False
        
        try:
            # Initialize API v1.1
            auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
            auth.set_access_token(self.access_token, self.access_secret)
            self.api = tweepy.API(auth)
            
            # Initialize Client v2
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            
            # Test connection
            self.api.verify_credentials()
            return True
            
        except Exception as e:
            print(f"Twitter connection error: {e}")
            return False
    
    async def post_tweet(self, text: str) -> Optional[Dict]:
        """Post a tweet"""
        if not self.client:
            if not await self.connect():
                return None
        
        try:
            response = self.client.create_tweet(text=text)
            return {
                "id": response.data["id"],
                "text": text,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None
    
    async def get_tweets(self, limit: int = 50) -> List[Dict]:
        """Get recent tweets"""
        if not self.api:
            if not await self.connect():
                return []
        
        try:
            tweets = []
            for tweet in tweepy.Cursor(self.api.home_timeline, count=limit).items(limit):
                tweets.append({
                    "id": str(tweet.id),
                    "text": tweet.text,
                    "author": tweet.user.screen_name,
                    "created_at": tweet.created_at.isoformat(),
                    "likes": tweet.favorite_count,
                    "retweets": tweet.retweet_count
                })
            return tweets
        except Exception as e:
            print(f"Error getting tweets: {e}")
            return []
    
    async def reply_to_tweet(self, tweet_id: str, text: str) -> Optional[Dict]:
        """Reply to a tweet"""
        if not self.client:
            if not await self.connect():
                return None
        
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            return {
                "id": response.data["id"],
                "text": text,
                "in_reply_to": tweet_id,
                "created_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error replying to tweet: {e}")
            return None


class LinkedInService:
    """LinkedIn API integration"""
    
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.access_token = None
    
    async def connect(self) -> bool:
        """Connect to LinkedIn API"""
        if not all([self.client_id, self.client_secret]):
            print("LinkedIn credentials not configured")
            return False
        
        # LinkedIn OAuth flow requires user interaction
        # In production, implement OAuth 2.0 authorization code flow
        # See: https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow
        print("LinkedIn integration requires OAuth flow - returning mock connection")
        return True
    
    async def post_update(self, text: str) -> Optional[Dict]:
        """Post a LinkedIn update"""
        if not self.access_token:
            if not await self.connect():
                return None
        
        # LinkedIn API v2 posting
        # In production, use: https://api.linkedin.com/v2/ugcPosts
        # Requires: r_liteprofile, w_member_social permissions
        print(f"LinkedIn posting not fully implemented - would post: {text[:50]}...")
        return {
            "status": "mock_success",
            "platform": "linkedin",
            "content": text[:100],
            "message": "LinkedIn API integration requires OAuth flow"
        }


class SocialMediaService:
    """Unified social media service"""
    
    def __init__(self):
        self.twitter = TwitterService()
        self.linkedin = LinkedInService()
    
    async def post(self, platform: str, content: str) -> Optional[Dict]:
        """Post to a social media platform"""
        if platform == "twitter":
            return await self.twitter.post_tweet(content)
        elif platform == "linkedin":
            return await self.linkedin.post_update(content)
        else:
            print(f"Unsupported platform: {platform}")
            return None
    
    async def schedule_post(
        self,
        platform: str,
        content: str,
        scheduled_at: datetime
    ) -> bool:
        """Schedule a post for later"""
        # In production, use Celery with Redis for task scheduling
        # Example implementation:
        # from celery import Celery
        # app = Celery('tasks', broker=settings.REDIS_URL)
        # @app.task
        # def scheduled_post(platform, content):
        #     await self.post(platform, content)
        # scheduled_post.apply_async(args=[platform, content], eta=scheduled_at)
        
        print(f"Scheduling post for {platform} at {scheduled_at}")
        # For now, return True to indicate scheduling was accepted
        # Actual scheduling requires Celery + Redis setup
        return True
    
    async def get_feed(self, platform: str, limit: int = 50) -> List[Dict]:
        """Get feed from a platform"""
        if platform == "twitter":
            return await self.twitter.get_tweets(limit)
        else:
            print(f"Feed not supported for {platform}")
            return []


# Create instance
social_service = SocialMediaService()
