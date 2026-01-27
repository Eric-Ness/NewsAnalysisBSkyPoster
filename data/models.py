"""
Data Models for News Poster Application

This module contains data classes and models used throughout the application.
Extracted from database.py for better separation of concerns.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SocialPostData:
    """Data class for social media post information."""
    platform: str                      # 'bluesky' or 'twitter'
    post_id: str                       # Platform's unique post ID
    post_text: str                     # The actual post text
    author_handle: str                 # @handle
    created_at: datetime               # When post was created
    post_uri: Optional[str] = None     # Full URI (BlueSky at:// URIs)
    post_url: Optional[str] = None     # Direct web URL to the post
    author_display_name: Optional[str] = None
    author_avatar_url: Optional[str] = None
    author_did: Optional[str] = None   # BlueSky DID
    post_facets: Optional[str] = None  # JSON string of facets
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    article_description: Optional[str] = None
    article_image_url: Optional[str] = None
    article_image_blob: Optional[str] = None
    news_feed_id: Optional[int] = None
    raw_response: Optional[str] = None # JSON string of full API response
