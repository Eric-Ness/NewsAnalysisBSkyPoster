"""
Data Layer Protocol Definitions

This module defines typing.Protocol interfaces for data layer operations.
These protocols enable dependency injection for database operations,
making services testable without real database connections.

Protocols defined:
- PostStorage: Interface for storing and retrieving social media posts
"""

from typing import Protocol, Optional, List, Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SocialPostData:
    """Data class for social media post information.

    This is a protocol-compatible version of the SocialPostData class.
    The actual implementation in data.models may have additional fields.
    """
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


class PostStorage(Protocol):
    """Protocol defining the interface for social post storage operations.

    Implementations should provide methods for:
    - Inserting new social media post records
    - Retrieving posts by ID or news feed association
    - Listing recent posts, optionally filtered by platform

    This protocol abstracts database operations, allowing services to work
    with any compatible storage backend (real database, in-memory mock, etc.).
    """

    def insert_social_post(self, post_data: SocialPostData) -> Optional[int]:
        """Insert a social media post record.

        Args:
            post_data: SocialPostData object containing post information.

        Returns:
            The ID of the inserted record, or None if insertion failed.
        """
        ...

    def get_social_post_by_id(self, social_post_id: int) -> Optional[Dict]:
        """Retrieve a social post by its ID.

        Args:
            social_post_id: The ID of the post to retrieve.

        Returns:
            The post data as a dictionary, or None if not found.
        """
        ...

    def get_recent_social_posts(
        self,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> Optional[List[Dict]]:
        """Retrieve recent social posts, optionally filtered by platform.

        Args:
            platform: Filter by platform ('bluesky' or 'twitter'), or None for all.
            limit: Maximum number of posts to return.

        Returns:
            List of post data dictionaries, or None if an error occurred.
        """
        ...
