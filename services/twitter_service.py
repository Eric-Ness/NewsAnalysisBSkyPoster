"""
Twitter Service Module

This module handles integration with Twitter/X API.
It provides functionality for authenticating with Twitter,
posting content, and retrieving tweet information.
"""

from typing import Optional, List, Tuple, Any
from datetime import datetime
import requests
import json
import re
import tweepy

from services.ai_service import FeedPost
from config import settings
from utils.logger import get_logger
from utils.exceptions import AuthenticationError, PostingError, MediaUploadError, SocialMediaError, RateLimitError
from data.database import db, SocialPostData
from data.protocols import PostStorage

logger = get_logger(__name__)

class TwitterService:
    """Service for Twitter/X integration.

    This service can be instantiated with custom dependencies for dependency injection,
    or use default values from settings for backward compatibility.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_key_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        post_storage: Optional[PostStorage] = None,
        client: Optional[Any] = None
    ):
        """Initialize the Twitter service with API authentication.

        Args:
            api_key: Twitter API key. Defaults to settings.TWITTER_API_KEY.
            api_key_secret: Twitter API key secret. Defaults to settings.TWITTER_API_KEY_SECRET.
            access_token: Twitter access token. Defaults to settings.TWITTER_ACCESS_TOKEN.
            access_token_secret: Twitter access token secret. Defaults to settings.TWITTER_ACCESS_TOKEN_SECRET.
            bearer_token: Twitter bearer token. Defaults to settings.TWITTER_BEARER_TOKEN.
            post_storage: Storage backend for posts (implements PostStorage protocol).
                         Defaults to the global db instance. Pass None to skip storage.
            client: Pre-configured Tweepy client. If provided, skips authentication setup.
        """
        self.api_key = api_key if api_key is not None else settings.TWITTER_API_KEY
        self.api_key_secret = api_key_secret if api_key_secret is not None else settings.TWITTER_API_KEY_SECRET
        self.access_token = access_token if access_token is not None else settings.TWITTER_ACCESS_TOKEN
        self.access_token_secret = access_token_secret if access_token_secret is not None else settings.TWITTER_ACCESS_TOKEN_SECRET
        self.bearer_token = bearer_token if bearer_token is not None else settings.TWITTER_BEARER_TOKEN
        # Use global db as default, but allow None to skip storage entirely
        self._post_storage = post_storage if post_storage is not None else db

        # Use pre-configured client or set up authentication
        if client is not None:
            self.client = client
        else:
            self.client = None
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
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate with Twitter: {e}")
            return False

    def get_recent_tweets(self, limit: int = settings.TWITTER_FETCH_LIMIT) -> List[FeedPost]:
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
                except Exception as e:
                    # If that fails (e.g., with bearer token), use a fallback method
                    logger.debug(f"Could not get authenticated user directly: {e}")
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
                    max_results=min(limit, settings.TWITTER_API_MAX_RESULTS),  # API limit
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
            
        except SocialMediaError:
            raise
        except Exception as e:
            logger.error(f"Error fetching recent tweets: {e}")
            return []

    def post_tweet(self, tweet_text: str, article_url: str, article_title: str,
                   article_image: Optional[str] = None,
                   news_feed_id: Optional[int] = None) -> Tuple[bool, Optional[int]]:
        """
        Post a tweet with an article link.

        Args:
            tweet_text: The text to tweet
            article_url: The URL of the article
            article_title: The title of the article
            article_image: The URL of an image to include (optional)
            news_feed_id: The News_Feed_ID for linking to the source article (optional)

        Returns:
            Tuple[bool, Optional[int]]: (success, social_post_id) - success status and the ID of the stored post record
        """
        try:
            if not self.client:
                logger.error("Twitter client not initialized")
                return False, None

            # Ensure tweet text is within Twitter's character limit
            # URLs are shortened by Twitter's t.co service
            url_length = settings.TWITTER_URL_LENGTH

            # Remove URL from text if it's already there (to avoid duplication)
            text_without_url = re.sub(r'https?://\S+', '', tweet_text)

            # Calculate available characters
            available_chars = settings.TWITTER_CHARACTER_LIMIT - url_length

            # Truncate text if needed
            if len(text_without_url) > available_chars:
                truncated_text = text_without_url[:available_chars - settings.TWEET_TRUNCATION_PADDING] + "..."
            else:
                truncated_text = text_without_url

            # Combine text with URL
            final_tweet_text = f"{truncated_text.strip()} {article_url}"

            # Variables to store tweet response data
            tweet_id = None
            tweet_response = None
            author_handle = None
            author_display_name = None
            author_avatar_url = None

            # Post the tweet
            if isinstance(self.client, tweepy.API):
                # Using API v1.1 (OAuth 1.0a)
                media_ids = []

                # Upload media if provided and supported
                if article_image and article_image.startswith('http'):
                    try:
                        # Download the image
                        image_response = requests.get(article_image, timeout=settings.TWITTER_IMAGE_TIMEOUT)
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

                    except MediaUploadError:
                        raise
                    except Exception as e:
                        logger.warning(f"Failed to upload media: {e}")

                # Post the tweet
                if media_ids:
                    tweet_response = self.client.update_status(
                        status=final_tweet_text,
                        media_ids=media_ids
                    )
                else:
                    tweet_response = self.client.update_status(status=final_tweet_text)

                # Extract data from v1.1 response
                if tweet_response:
                    tweet_id = str(tweet_response.id)
                    if hasattr(tweet_response, 'user'):
                        author_handle = tweet_response.user.screen_name
                        author_display_name = tweet_response.user.name
                        author_avatar_url = tweet_response.user.profile_image_url_https

                logger.info(f"Successfully posted tweet: {article_title}")

            else:
                # Using API v2 (Client)
                # Check if we have write permissions
                if not self.access_token or not self.access_token_secret:
                    logger.error("Cannot post tweets with Bearer Token authentication. "
                                "OAuth 1.0a credentials are required for posting.")
                    return False, None

                # Create the tweet
                response = self.client.create_tweet(text=final_tweet_text)

                if response and hasattr(response, 'data'):
                    tweet_id = str(response.data['id'])
                    tweet_response = response

                    # Try to get user info
                    try:
                        me = self.client.get_me(user_fields=['profile_image_url'])
                        if me and hasattr(me, 'data'):
                            author_handle = me.data.username
                            author_display_name = me.data.name
                            author_avatar_url = me.data.profile_image_url if hasattr(me.data, 'profile_image_url') else None
                    except Exception as e:
                        logger.warning(f"Could not fetch user info: {e}")

                    logger.info(f"Successfully posted tweet: {article_title}")
                else:
                    logger.error("Failed to post tweet: No valid response from Twitter API")
                    return False, None

            # Store post data in database
            social_post_id = None
            if tweet_id:
                try:
                    # Build tweet URL
                    post_url = f"https://twitter.com/{author_handle}/status/{tweet_id}" if author_handle else None

                    # Create SocialPostData object
                    post_data = SocialPostData(
                        platform='twitter',
                        post_id=tweet_id,
                        post_text=final_tweet_text,
                        author_handle=author_handle or 'unknown',
                        created_at=datetime.now(),
                        post_uri=None,  # Twitter doesn't use URIs like BlueSky
                        post_url=post_url,
                        author_display_name=author_display_name,
                        author_avatar_url=author_avatar_url,
                        author_did=None,  # Twitter doesn't have DIDs
                        post_facets=None,  # Twitter doesn't use facets
                        article_url=article_url,
                        article_title=article_title,
                        article_description=None,
                        article_image_url=article_image,
                        article_image_blob=None,
                        news_feed_id=news_feed_id,
                        raw_response=json.dumps({
                            'id': tweet_id,
                            'text': final_tweet_text
                        })
                    )

                    # Insert into database (if storage is configured)
                    if self._post_storage is not None:
                        social_post_id = self._post_storage.insert_social_post(post_data)
                        if social_post_id:
                            logger.info(f"Stored Twitter post in database - Social_Post_ID: {social_post_id}")
                        else:
                            logger.warning("Failed to store Twitter post in database")

                except Exception as e:
                    logger.error(f"Error storing tweet data in database: {e}")

            return True, social_post_id

        except (PostingError, AuthenticationError, MediaUploadError, RateLimitError):
            raise
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return False, None