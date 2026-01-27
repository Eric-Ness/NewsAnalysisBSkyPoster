"""
Service Protocol Definitions

This module defines typing.Protocol interfaces for services used in the NewsAnalysisBSkyPoster
application. These protocols enable loose coupling, dependency injection, and easier testing.

Protocols defined:
- ArticleServiceProtocol: Interface for article fetching and URL handling
- AIServiceProtocol: Interface for AI-powered content operations
- SocialPlatformService: Interface for social media platform services (BlueSky, Twitter)
"""

from typing import Protocol, Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class FeedPost:
    """Data class to store feed post content from social media platforms."""
    text: str
    url: Optional[str]
    title: Optional[str]
    timestamp: datetime


@dataclass
class ArticleContent:
    """Data class to store article content and metadata."""
    url: str
    title: str
    text: str
    summary: str
    top_image: str
    news_feed_id: Optional[int] = None


class ArticleServiceProtocol(Protocol):
    """Protocol defining the interface for article fetching services.

    Implementations should provide methods for:
    - Extracting real URLs from redirect URLs (e.g., Google News)
    - Fetching and parsing article content
    - Managing URL history to avoid duplicate posts
    """

    def get_real_url(self, google_url: str) -> Optional[str]:
        """Get the real article URL from a redirect URL.

        Args:
            google_url: The redirect URL (e.g., Google News URL).

        Returns:
            The resolved article URL, or None if extraction failed.
        """
        ...

    def fetch_article(self, url: str, news_feed_id: Optional[int] = None) -> Optional[ArticleContent]:
        """Fetch and parse article content from a URL.

        Args:
            url: The URL of the article to fetch.
            news_feed_id: Optional ID linking to the news feed source.

        Returns:
            ArticleContent with parsed data, or None if fetch failed.
        """
        ...

    def is_url_in_history(self, url: str) -> bool:
        """Check if a URL has already been processed.

        Args:
            url: The URL to check.

        Returns:
            True if URL is in history, False otherwise.
        """
        ...

    def _add_url_to_history(self, url: str) -> None:
        """Add a URL to the history of processed URLs.

        Args:
            url: The URL to add to history.
        """
        ...


class AIServiceProtocol(Protocol):
    """Protocol defining the interface for AI-powered operations.

    Implementations should provide methods for:
    - Selecting newsworthy articles from candidates
    - Checking content similarity against recent posts
    - Generating social media content from articles
    """

    def select_news_articles(
        self,
        candidates: List[Dict[str, Any]],
        recent_posts: List[FeedPost],
        max_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Select the most newsworthy articles from candidates.

        Args:
            candidates: List of candidate articles with URL, Title, News_Feed_ID.
            recent_posts: List of recent posts to avoid duplicates.
            max_count: Maximum number of articles to select.

        Returns:
            List of selected articles in priority order.
        """
        ...

    def select_news_article(
        self,
        candidates: List[Dict[str, Any]],
        recent_posts: List[FeedPost]
    ) -> Optional[Dict[str, Any]]:
        """Select the single most newsworthy article from candidates.

        Args:
            candidates: List of candidate articles.
            recent_posts: List of recent posts to avoid duplicates.

        Returns:
            The selected article, or None if no suitable article found.
        """
        ...

    def check_content_similarity(
        self,
        article_title: str,
        article_text: str,
        recent_posts: List[FeedPost]
    ) -> bool:
        """Check if article content is too similar to recent posts.

        Args:
            article_title: Title of the candidate article.
            article_text: Text content of the candidate article.
            recent_posts: List of recent posts to compare against.

        Returns:
            True if content is similar to recent posts, False otherwise.
        """
        ...

    def generate_tweet(
        self,
        article_text: str,
        article_title: str,
        article_url: str
    ) -> Optional[Dict[str, Any]]:
        """Generate social media post content for an article.

        Args:
            article_text: The full text of the article.
            article_title: The title of the article.
            article_url: The URL of the article.

        Returns:
            Dictionary with 'tweet_text', 'summary', and 'facets', or None on failure.
        """
        ...


class SocialPlatformService(Protocol):
    """Protocol defining the interface for social media platform services.

    This protocol unifies the interface for BlueSky (SocialService) and
    Twitter (TwitterService), enabling them to be used interchangeably.

    Implementations should provide methods for:
    - Retrieving recent posts from the platform
    - Posting content to the platform
    """

    def get_recent_posts(self, limit: int = 50) -> List[FeedPost]:
        """Fetch recent posts from the social media platform.

        Args:
            limit: Maximum number of posts to fetch.

        Returns:
            List of FeedPost objects representing recent posts.
        """
        ...

    def post_content(
        self,
        text: str,
        article_url: str,
        article_title: str,
        article_image: Optional[str] = None,
        news_feed_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int]]:
        """Post content to the social media platform.

        Args:
            text: The text content to post.
            article_url: The URL of the article being shared.
            article_title: The title of the article.
            article_image: Optional URL of an image to include.
            news_feed_id: Optional ID linking to the news feed source.

        Returns:
            Tuple of (success, social_post_id) where social_post_id is the
            database ID of the stored post record, or None if storage failed.
        """
        ...
