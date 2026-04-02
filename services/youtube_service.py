"""
YouTube Video Service Module

This module handles YouTube video candidate fetching, filtering, and management
for posting to social media platforms. It is analogous to ArticleService but
sources content from the YouTube database instead of news articles.
"""

import os
import re
import logging
from typing import Optional, List

from config import settings
from data.models import YouTubeVideoCandidate
from data.youtube_database import YouTubeDatabaseConnection, youtube_db
from utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeVideoService:
    """Service for fetching and managing YouTube video candidates for posting."""

    def __init__(
        self,
        youtube_database: Optional[YouTubeDatabaseConnection] = None,
        url_history_file: Optional[str] = None,
        max_history_lines: Optional[int] = None,
        cleanup_threshold: Optional[int] = None,
    ):
        """Initialize the YouTube video service.

        Args:
            youtube_database: YouTube database connection. Defaults to global youtube_db.
            url_history_file: Path to shared URL history file. Defaults to settings.URL_HISTORY_FILE.
            max_history_lines: Max lines in history file. Defaults to settings.MAX_HISTORY_LINES.
            cleanup_threshold: Old entries to remove during cleanup. Defaults to settings.CLEANUP_THRESHOLD.
        """
        self._db = youtube_database if youtube_database is not None else youtube_db
        self.url_history_file = url_history_file if url_history_file is not None else settings.URL_HISTORY_FILE
        self.max_history_lines = max_history_lines if max_history_lines is not None else settings.MAX_HISTORY_LINES
        self.cleanup_threshold = cleanup_threshold if cleanup_threshold is not None else settings.CLEANUP_THRESHOLD

    def get_video_candidates(
        self,
        limit: int = settings.YOUTUBE_MAX_CANDIDATES,
        max_age_days: int = settings.YOUTUBE_MAX_AGE_DAYS,
        min_views: int = settings.YOUTUBE_MIN_VIEWS,
    ) -> List[YouTubeVideoCandidate]:
        """
        Fetch candidate videos from the YouTube database.

        Args:
            limit: Maximum number of candidates to return.
            max_age_days: Only consider videos from the last N days.
            min_views: Minimum view count threshold.

        Returns:
            List[YouTubeVideoCandidate]: List of video candidate dataclass instances.
        """
        df = self._db.get_youtube_candidates(limit, max_age_days, min_views)

        if df is None or len(df) == 0:
            logger.warning("No YouTube video candidates found")
            return []

        candidates = []
        for _, row in df.iterrows():
            candidates.append(YouTubeVideoCandidate(
                youtube_video_id=row['YouTube_Video_ID'],
                youtube_video_key=row['YouTube_Video_Key'],
                title=row['Title'],
                description=row.get('Description', '') or '',
                published_date=row['Published_Date'],
                thumbnail_url=row.get('Thumbnail_URL'),
                duration_seconds=row.get('Duration_Seconds', 0) or 0,
                view_count=row.get('View_Count', 0) or 0,
                like_count=row.get('Like_Count', 0) or 0,
                comment_count=row.get('Comment_Count', 0) or 0,
                channel_name=row.get('Channel_Name'),
                channel_handle=row.get('Channel_Handle'),
            ))

        logger.info(f"Fetched {len(candidates)} YouTube video candidates from database")
        return candidates

    def filter_candidates(self, candidates: List[YouTubeVideoCandidate]) -> List[YouTubeVideoCandidate]:
        """
        Apply additional Python-level filters to video candidates.

        Filters:
        - Skip videos under YOUTUBE_MIN_DURATION_SECONDS
        - Skip videos over YOUTUBE_MAX_DURATION_SECONDS (prefer single news items)
        - Skip blocked channels (YOUTUBE_BLOCKED_CHANNELS)
        - Skip videos whose URL is already in URL history
        - Skip opinion/commentary titles (principle-based editorial filter)
        - Cap per-channel representation (YOUTUBE_MAX_PER_CHANNEL) for source diversity

        Args:
            candidates: List of video candidates to filter.

        Returns:
            List[YouTubeVideoCandidate]: Filtered list of candidates.
        """
        posted_urls = self._get_posted_urls()
        blocked_channels = [h.lower() for h in settings.YOUTUBE_BLOCKED_CHANNELS]
        opinion_patterns = settings.YOUTUBE_OPINION_TITLE_PATTERNS
        max_per_channel = settings.YOUTUBE_MAX_PER_CHANNEL
        channel_counts: dict = {}
        filtered = []

        for video in candidates:
            # Skip very short videos
            if video.duration_seconds < settings.YOUTUBE_MIN_DURATION_SECONDS:
                logger.debug(f"Skipping short video ({video.duration_seconds}s): {video.title}")
                continue

            # Skip long show segments (prefer single news items 1-5 min)
            if video.duration_seconds > settings.YOUTUBE_MAX_DURATION_SECONDS:
                logger.debug(f"Skipping long video ({video.duration_seconds}s): {video.title}")
                continue

            # Skip blocked channels
            if video.channel_handle and video.channel_handle.lower() in blocked_channels:
                logger.debug(f"Skipping blocked channel {video.channel_handle}: {video.title}")
                continue

            # Skip already posted URLs
            if video.url in posted_urls:
                logger.debug(f"Skipping already posted URL: {video.url}")
                continue

            # Skip opinion/commentary content (principle-based, channel-agnostic)
            if self._is_opinion_title(video.title, opinion_patterns):
                logger.debug(f"Skipping opinion/commentary title: {video.title}")
                continue

            # Enforce per-channel diversity cap
            channel_key = (video.channel_handle or video.channel_name or 'unknown').lower()
            channel_counts[channel_key] = channel_counts.get(channel_key, 0) + 1
            if channel_counts[channel_key] > max_per_channel:
                logger.debug(f"Channel cap reached ({max_per_channel}) for {channel_key}: {video.title}")
                continue

            filtered.append(video)

        removed = len(candidates) - len(filtered)
        if removed > 0:
            logger.info(f"Filtered out {removed} videos (duration/blocked/history/editorial/diversity), {len(filtered)} remaining")

        return filtered

    @staticmethod
    def _is_opinion_title(title: str, patterns: List[str]) -> bool:
        """Check if a title matches opinion/commentary patterns."""
        title_lower = title.lower()
        for pattern in patterns:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return True
        return False

    def mark_video_posted(self, youtube_video_id: int) -> bool:
        """
        Mark a video as posted in the YouTube database.

        Args:
            youtube_video_id: The YouTube_Video_ID to mark.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self._db.mark_video_posted(youtube_video_id)

    def is_url_in_history(self, url: str) -> bool:
        """Check if a URL has been posted recently (shared with article history)."""
        return url in self._get_posted_urls()

    def _add_url_to_history(self, url: str) -> None:
        """Add a URL to the shared history file."""
        try:
            urls = self._get_posted_urls()

            if url not in urls:
                urls.append(url)

            if len(urls) > self.max_history_lines:
                logger.info(f"URL history exceeds {self.max_history_lines} entries, removing oldest {self.cleanup_threshold}")
                urls = urls[self.cleanup_threshold:]

            with open(self.url_history_file, 'w') as f:
                for u in urls:
                    f.write(f"{u}\n")

            logger.info(f"Added YouTube URL to history file: {url}")
        except Exception as e:
            logger.error(f"Error adding URL to history file: {e}")

    def _get_posted_urls(self) -> List[str]:
        """Get list of previously posted URLs from the shared history file."""
        try:
            if not os.path.exists(self.url_history_file):
                return []

            with open(self.url_history_file, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]

            return urls
        except Exception as e:
            logger.error(f"Error reading URL history file: {e}")
            return []
