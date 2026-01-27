"""
Social Service Module

This module handles social media integration with the AT Protocol (BlueSky).
It provides functionality for authenticating with BlueSky, posting content,
and retrieving feed information.
"""

import json
from typing import Optional, List, Any, Tuple
from datetime import datetime
import requests

from atproto import Client, models

from config import settings
from utils.logger import get_logger
from utils.exceptions import AuthenticationError, PostingError, MediaUploadError, SocialMediaError
from services.ai_service import FeedPost
from data.database import db, SocialPostData

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
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate with AT Protocol: {e}")
            return False
    
    def get_recent_posts(self, limit: int = settings.BLUESKY_FETCH_LIMIT) -> List[FeedPost]:
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

        except SocialMediaError:
            raise
        except Exception as e:
            logger.error(f"Error fetching recent posts: {e}")
            return []
    
    def post_to_social(self, tweet_text: str, article_url: str, article_title: str,
                       article_image: Optional[str] = None, facets: Optional[List[Any]] = None,
                       news_feed_id: Optional[int] = None) -> Tuple[bool, Optional[int]]:
        """
        Post content to the AT Protocol feed.

        Args:
            tweet_text: The text to post
            article_url: The URL of the article
            article_title: The title of the article
            article_image: The URL of an image to include (optional)
            facets: Rich text facets for formatting (optional)
            news_feed_id: The News_Feed_ID for linking to the source article (optional)

        Returns:
            Tuple[bool, Optional[int]]: (success, social_post_id) - success status and the ID of the stored post record
        """
        try:
            # Process the article image if provided
            thumb = None
            thumb_blob_ref = None
            if article_image:
                try:
                    response = requests.get(article_image, timeout=settings.BLUESKY_IMAGE_TIMEOUT)
                    img_data = response.content
                    upload = self.at_client.com.atproto.repo.upload_blob(img_data)
                    thumb = upload.blob
                    thumb_blob_ref = str(thumb.ref) if hasattr(thumb, 'ref') else None
                except MediaUploadError:
                    raise
                except Exception as e:
                    logger.warning(f"Failed to upload image: {e}")

            # Create external embed
            embed_external = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    title=article_title,
                    description=tweet_text[:settings.EMBED_DESCRIPTION_LENGTH] + "..." if len(tweet_text) > settings.EMBED_DESCRIPTION_LENGTH else tweet_text,
                    uri=article_url,
                    thumb=thumb
                )
            )

            # Post to Bluesky using the client's send_post method
            post_response = self.at_client.send_post(
                text=tweet_text,
                embed=embed_external,
                facets=facets
            )

            logger.info(f"Successfully posted to AT Protocol: {article_title}")

            # Extract post data from response and store in database
            social_post_id = None
            try:
                # Get profile info for author data
                profile = self.at_client.get_profile(settings.AT_PROTOCOL_USERNAME)

                # Extract post ID and URI from response
                post_uri = post_response.uri if hasattr(post_response, 'uri') else None
                post_cid = post_response.cid if hasattr(post_response, 'cid') else None

                # Build the web URL from the URI
                # URI format: at://did:plc:xxxxx/app.bsky.feed.post/xxxxx
                post_url = None
                if post_uri:
                    # Extract the rkey (post ID) from the URI
                    uri_parts = post_uri.split('/')
                    if len(uri_parts) >= 5:
                        rkey = uri_parts[-1]
                        post_url = f"https://bsky.app/profile/{settings.AT_PROTOCOL_USERNAME}/post/{rkey}"

                # Serialize facets to JSON if present
                facets_json = None
                if facets:
                    try:
                        facets_json = json.dumps([f.model_dump() if hasattr(f, 'model_dump') else str(f) for f in facets])
                    except Exception:
                        facets_json = str(facets)

                # Create SocialPostData object
                post_data = SocialPostData(
                    platform='bluesky',
                    post_id=post_cid or post_uri.split('/')[-1] if post_uri else str(datetime.now().timestamp()),
                    post_text=tweet_text,
                    author_handle=settings.AT_PROTOCOL_USERNAME,
                    created_at=datetime.now(),
                    post_uri=post_uri,
                    post_url=post_url,
                    author_display_name=profile.display_name if hasattr(profile, 'display_name') else None,
                    author_avatar_url=profile.avatar if hasattr(profile, 'avatar') else None,
                    author_did=profile.did if hasattr(profile, 'did') else None,
                    post_facets=facets_json,
                    article_url=article_url,
                    article_title=article_title,
                    article_description=tweet_text[:settings.EMBED_DESCRIPTION_LENGTH] + "..." if len(tweet_text) > settings.EMBED_DESCRIPTION_LENGTH else tweet_text,
                    article_image_url=article_image,
                    article_image_blob=thumb_blob_ref,
                    news_feed_id=news_feed_id,
                    raw_response=json.dumps({
                        'uri': post_uri,
                        'cid': post_cid
                    }) if post_uri or post_cid else None
                )

                # Insert into database
                social_post_id = db.insert_social_post(post_data)
                if social_post_id:
                    logger.info(f"Stored BlueSky post in database - Social_Post_ID: {social_post_id}")
                else:
                    logger.warning("Failed to store BlueSky post in database")

            except Exception as e:
                logger.error(f"Error storing post data in database: {e}")

            return True, social_post_id

        except (PostingError, AuthenticationError, MediaUploadError):
            raise
        except Exception as e:
            logger.error(f"Error posting to AT Protocol: {e}")
            return False, None