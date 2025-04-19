"""
Social Service Module

This module handles social media integration with the AT Protocol (BlueSky).
It provides functionality for authenticating with BlueSky, posting content,
and retrieving feed information.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import requests

from atproto import Client, models

from config import settings
from utils.logger import get_logger
from services.ai_service import FeedPost

logger = get_logger(__name__)

class SocialService:
    """Service for social media integrations with the AT Protocol (BlueSky)."""
    
    def __init__(self):
        """Initialize the social service with AT Protocol client."""
        self.at_client = Client()
        self._setup_at_protocol()
    
    def _setup_at_protocol(self) -> bool:
        """
        Set up AT Protocol authentication.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            username = settings.AT_PROTOCOL_USERNAME
            password = settings.AT_PROTOCOL_PASSWORD
            
            if not username or not password:
                logger.error("Missing AT Protocol credentials")
                return False
                
            self.at_client.login(username, password)
            logger.info(f"Successfully logged in to AT Protocol as {username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with AT Protocol: {e}")
            return False
    
    def get_recent_posts(self, limit: int = 80) -> List[FeedPost]:
        """
        Fetches recent posts from the AT Protocol feed.

        Args:
            limit (int): The maximum number of posts to fetch. Defaults to 80.

        Returns:
            List[FeedPost]: A list of FeedPost objects representing the recent posts.
        """
        try:
            profile = self.at_client.get_profile(settings.AT_PROTOCOL_USERNAME)
            feed = self.at_client.get_author_feed(profile.did, limit=limit)
            
            posts = []
            for post in feed.feed:
                url = None
                title = None
                
                # Extract embed data if available
                if hasattr(post.post, 'embed') and post.post.embed:
                    if hasattr(post.post.embed, 'external'):
                        url = post.post.embed.external.uri
                        title = post.post.embed.external.title

                # Extract timestamp from indexed_at field
                timestamp = None
                if hasattr(post.post, 'indexed_at'):
                    timestamp = datetime.fromisoformat(post.post.indexed_at.replace('Z', '+00:00'))
                else:
                    logger.warning(f"No timestamp found for post, using current time")
                    timestamp = datetime.now()

                # Extract text from record if available
                text = ""
                if hasattr(post.post, 'record') and hasattr(post.post.record, 'text'):
                    text = post.post.record.text
                elif hasattr(post.post, 'text'):
                    text = post.post.text

                posts.append(FeedPost(
                    text=text,
                    url=url,
                    title=title,
                    timestamp=timestamp
                ))
            
            logger.info(f"Successfully retrieved {len(posts)} recent posts")
            return posts

        except Exception as e:
            logger.error(f"Error fetching recent posts: {e}")
            return []
    
    def post_to_social(self, tweet_text: str, article_url: str, article_title: str, 
                       article_image: Optional[str] = None, facets: Optional[List[Any]] = None) -> bool:
        """
        Post content to the AT Protocol feed.
        
        Args:
            tweet_text: The text to post
            article_url: The URL of the article
            article_title: The title of the article
            article_image: The URL of an image to include (optional)
            facets: Rich text facets for formatting (optional)
            
        Returns:
            bool: True if the post was successful, False otherwise
        """
        try:
            # Process the article image if provided
            thumb = None
            if article_image:
                try:
                    response = requests.get(article_image)
                    img_data = response.content
                    upload = self.at_client.com.atproto.repo.upload_blob(img_data)
                    thumb = upload.blob
                except Exception as e:
                    logger.warning(f"Failed to upload image: {e}")
            
            # Create external embed
            embed_external = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    title=article_title,
                    description=tweet_text[:100] + "..." if len(tweet_text) > 100 else tweet_text,
                    uri=article_url,
                    thumb=thumb
                )
            )

            # Post to Bluesky using the client's send_post method
            self.at_client.send_post(
                text=tweet_text,
                embed=embed_external,
                facets=facets
            )
            
            logger.info(f"Successfully posted to AT Protocol: {article_title}")
            return True
            
        except Exception as e:
            logger.error(f"Error posting to AT Protocol: {e}")
            return False 