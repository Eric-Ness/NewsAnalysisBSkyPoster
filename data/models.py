"""
Data Models for News Poster Application

This module contains data classes and models used throughout the application.
Extracted from database.py for better separation of concerns.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

# =============================================================================
# YouTube Video Candidate
# =============================================================================

@dataclass
class YouTubeVideoCandidate:
    """Data class for a YouTube video candidate for posting."""
    youtube_video_id: int
    youtube_video_key: str          # 11-char YouTube video ID
    title: str
    description: str
    published_date: datetime
    thumbnail_url: Optional[str] = None
    duration_seconds: int = 0
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    channel_name: Optional[str] = None
    channel_handle: Optional[str] = None

    @property
    def url(self) -> str:
        """YouTube watch URL for this video."""
        return f"https://www.youtube.com/watch?v={self.youtube_video_key}"

    @property
    def engagement_score(self) -> float:
        """Weighted engagement score for ranking."""
        return self.view_count + (self.like_count * 10) + (self.comment_count * 5)


# =============================================================================
# Social Post Data
# =============================================================================


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
    youtube_video_id: Optional[int] = None  # FK to YouTube Video (cross-database, logical only)
    raw_response: Optional[str] = None # JSON string of full API response


@dataclass
class BlueSkyDailyMetrics:
    """Data class for daily BlueSky account metrics."""
    snapshot_date: date                         # The date this snapshot represents
    follower_count: int = 0                     # Total followers as of this date
    following_count: int = 0                    # Total accounts followed
    total_posts_count: int = 0                  # Total posts on the account
    stories_posted: int = 0                     # Stories posted by the app on this date
    stories_skipped: int = 0                    # Stories skipped on this date
    daily_likes: int = 0                        # Total likes received on this date
    daily_reposts: int = 0                      # Total reposts received on this date
    daily_replies: int = 0                      # Total replies received on this date
    daily_quotes: int = 0                       # Total quotes received on this date
    daily_impressions: int = 0                  # Total impressions on this date
    new_followers: int = 0                      # Net new followers gained
    new_unfollowers: int = 0                    # Followers lost on this date
