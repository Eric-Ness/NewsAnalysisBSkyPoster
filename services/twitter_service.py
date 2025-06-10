"""
Twitter Service Module

This module handles integration with Twitter/X API.
It provides functionality for authenticating with Twitter,
posting content, and retrieving tweet information.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import requests
import json
import base64
import hmac
import hashlib
import urllib.parse
import time
import re
import tweepy

from services.ai_service import FeedPost
from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

class TwitterService:
    """Service for Twitter/X integration."""
    
    def __init__(self):
        """Initialize the Twitter service with API authentication."""
        self.api_key = settings.TWITTER_API_KEY
        self.api_key_secret = settings.TWITTER_API_KEY_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.client = None
        
        # Set up Twitter client
        self._setup_twitter()
        
    def _setup_twitter(self) -> bool:
        """
        Set up Twitter API authentication using Tweepy.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            # Check which authentication method to use
            if self.api_key and self.api_key_secret and self.access_token and self.access_token_secret:
                # OAuth 1.0a for full read/write access
                auth = tweepy.OAuth1UserHandler(
                    self.api_key, 
                    self.api_key_secret,
                    self.access_token,
                    self.access_token_secret
                )
                self.client = tweepy.API(auth)
                # Verify credentials
                self.client.verify_credentials()
                logger.info("Successfully authenticated with Twitter API using OAuth 1.0a")
                return True
                
            elif self.bearer_token:
                # OAuth 2.0 Bearer Token (app-only auth - limited to reading public data)
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                # Get some public data to verify connection
                self.client.get_user(username="twitter")
                logger.info("Successfully authenticated with Twitter API using Bearer Token")
                return True
                
            else:
                logger.error("No valid Twitter authentication method found. "
                             "Please provide either OAuth 1.0a credentials or a Bearer Token.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to authenticate with Twitter: {e}")
            return False

    def get_recent_tweets(self, limit: int = 50) -> List[FeedPost]:
        """
        Fetches recent tweets from the user's timeline.

        Args:
            limit: The maximum number of tweets to fetch. Defaults to 50.

        Returns:
            List[FeedPost]: A list of FeedPost objects representing the recent tweets.
        """
        try:
            if not self.client:
                logger.error("Twitter client not initialized")
                return []
                
            tweets = []
            
            # Check if we're using API v1.1 or v2
            if isinstance(self.client, tweepy.API):
                # Using API v1.1 (OAuth 1.0a)
                recent_tweets = self.client.user_timeline(count=limit, tweet_mode="extended")
                
                for tweet in recent_tweets:
                    # Get the full tweet text
                    text = tweet.full_text if hasattr(tweet, 'full_text') else tweet.text
                    
                    # Extract URLs
                    url = None
                    title = None
                    if hasattr(tweet, 'entities') and 'urls' in tweet.entities and tweet.entities['urls']:
                        for url_entity in tweet.entities['urls']:
                            if 'expanded_url' in url_entity:
                                url = url_entity['expanded_url']
                                break
                    
                    # Convert created_at to datetime
                    timestamp = tweet.created_at
                    
                    tweets.append(FeedPost(
                        text=text,
                        url=url,
                        title=title,
                        timestamp=timestamp
                    ))
            else:
                # Using API v2 (Bearer Token)
                # First need to get the user ID
                me = None
                try:
                    # Try to get the authenticated user
                    me = self.client.get_me()
                except:
                    # If that fails (e.g., with bearer token), use a fallback method
                    if self.access_token:
                        # Extract user ID from access token (format: user_id-alphanumeric)
                        user_id = self.access_token.split('-')[0]
                        me = self.client.get_user(id=user_id)
                
                if not me:
                    logger.error("Could not determine user ID for tweet retrieval")
                    return []
                
                user_id = me.data.id
                
                # Get recent tweets with expansions for URLs
                recent_tweets = self.client.get_users_tweets(
                    id=user_id,
                    max_results=min(limit, 100),  # API limit is 100
                    tweet_fields=['created_at', 'entities'],
                    expansions=['attachments.media_keys'],
                    media_fields=['url']
                )
                
                if not recent_tweets.data:
                    logger.warning("No tweets found")
                    return []
                
                for tweet in recent_tweets.data:
                    # Extract URLs
                    url = None
                    title = None
                    if hasattr(tweet, 'entities') and 'urls' in tweet.entities and tweet.entities['urls']:
                        for url_entity in tweet.entities['urls']:
                            if 'expanded_url' in url_entity:
                                url = url_entity['expanded_url']
                                break
                    
                    # Convert created_at string to datetime
                    timestamp = tweet.created_at
                    
                    tweets.append(FeedPost(
                        text=tweet.text,
                        url=url,
                        title=title,
                        timestamp=timestamp
                    ))
            
            logger.info(f"Successfully retrieved {len(tweets)} recent tweets")
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching recent tweets: {e}")
            return []

    def post_tweet(self, tweet_text: str, article_url: str, article_title: str, 
                   article_image: Optional[str] = None) -> bool:
        """
        Post a tweet with an article link.
        
        Args:
            tweet_text: The text to tweet
            article_url: The URL of the article
            article_title: The title of the article
            article_image: The URL of an image to include (optional)
            
        Returns:
            bool: True if the tweet was successful, False otherwise
        """
        try:
            if not self.client:
                logger.error("Twitter client not initialized")
                return False
                
            # Ensure tweet text is within Twitter's character limit (280 chars)
            # URLs are shortened by Twitter's t.co service to 23 characters
            url_length = 23
            
            # Remove URL from text if it's already there (to avoid duplication)
            text_without_url = re.sub(r'https?://\S+', '', tweet_text)
            
            # Calculate available characters
            available_chars = 280 - url_length
            
            # Truncate text if needed
            if len(text_without_url) > available_chars:
                truncated_text = text_without_url[:available_chars-4] + "..."
            else:
                truncated_text = text_without_url
                
            # Combine text with URL
            final_tweet_text = f"{truncated_text.strip()} {article_url}"
            
            # Post the tweet
            if isinstance(self.client, tweepy.API):
                # Using API v1.1 (OAuth 1.0a)
                media_ids = []
                
                # Upload media if provided and supported
                if article_image and article_image.startswith('http'):
                    try:
                        # Download the image
                        image_response = requests.get(article_image, timeout=10)
                        if image_response.status_code == 200:
                            # Create a temporary file
                            import tempfile
                            import os
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                                temp_filename = temp_file.name
                                temp_file.write(image_response.content)
                            
                            # Upload the media
                            media = self.client.media_upload(temp_filename)
                            media_ids.append(media.media_id)
                            
                            # Clean up the temporary file
                            os.unlink(temp_filename)
                            
                    except Exception as e:
                        logger.warning(f"Failed to upload media: {e}")
                
                # Post the tweet
                if media_ids:
                    tweet = self.client.update_status(
                        status=final_tweet_text,
                        media_ids=media_ids
                    )
                else:
                    tweet = self.client.update_status(status=final_tweet_text)
                
                logger.info(f"Successfully posted tweet: {article_title}")
                return True
                
            else:
                # Using API v2 (Client)
                # Check if we have write permissions
                if not self.access_token or not self.access_token_secret:
                    logger.error("Cannot post tweets with Bearer Token authentication. "
                                "OAuth 1.0a credentials are required for posting.")
                    return False
                
                # Create the tweet
                response = self.client.create_tweet(text=final_tweet_text)
                
                if response and hasattr(response, 'data'):
                    logger.info(f"Successfully posted tweet: {article_title}")
                    return True
                else:
                    logger.error("Failed to post tweet: No valid response from Twitter API")
                    return False
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return False