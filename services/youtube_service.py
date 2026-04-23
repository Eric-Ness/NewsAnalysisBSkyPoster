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
        unknown_channels_this_run: set = set()
        for _, row in df.iterrows():
            handle = row.get('Channel_Handle')
            tier = self._resolve_channel_tier(handle, unknown_channels_this_run)
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
                channel_handle=handle,
                tier=tier,
            ))

        logger.info(f"Fetched {len(candidates)} YouTube video candidates from database")
        return candidates

    @staticmethod
    def _resolve_channel_tier(handle: Optional[str], unknown_seen: Optional[set] = None) -> int:
        """Look up a channel's tier from settings.YOUTUBE_CHANNEL_TIERS.

        Falls back to YOUTUBE_DEFAULT_TIER for unknown channels. Emits a single
        WARNING per unknown handle per run (via the unknown_seen set) so the log
        isn't spammy but new channels are still surfaced for classification.
        """
        if not handle:
            return settings.YOUTUBE_DEFAULT_TIER
        key = handle.lower()
        tier = settings.YOUTUBE_CHANNEL_TIERS.get(key)
        if tier is not None:
            return tier
        if unknown_seen is not None and key not in unknown_seen:
            unknown_seen.add(key)
            logger.warning(
                f"Unknown channel {handle} — defaulted to Tier {settings.YOUTUBE_DEFAULT_TIER}. "
                f"Add to YOUTUBE_CHANNEL_TIERS in config/settings.py to classify."
            )
        return settings.YOUTUBE_DEFAULT_TIER

    def filter_candidates(self, candidates: List[YouTubeVideoCandidate]) -> List[YouTubeVideoCandidate]:
        """
        Apply additional Python-level filters to video candidates.

        Filters:
        - Skip videos under YOUTUBE_MIN_DURATION_SECONDS
        - Skip videos over YOUTUBE_MAX_DURATION_SECONDS (prefer single news items)
        - Skip Tier 4 channels (state propaganda / unreliable per YOUTUBE_CHANNEL_TIERS)
        - Skip videos whose URL is already in URL history
        - Skip opinion/commentary titles (principle-based editorial filter)
        - Cap per-channel representation via YOUTUBE_TIER_CAPS for source diversity + quality

        Args:
            candidates: List of video candidates to filter.

        Returns:
            List[YouTubeVideoCandidate]: Filtered list of candidates.
        """
        posted_urls = self._get_posted_urls()
        opinion_patterns = settings.YOUTUBE_OPINION_TITLE_PATTERNS
        tier_caps = settings.YOUTUBE_TIER_CAPS
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

            # Skip Tier 4 (blocked) channels
            if video.tier == 4:
                logger.debug(f"Skipping Tier 4 channel {video.channel_handle}: {video.title}")
                continue

            # Skip already posted URLs
            if video.url in posted_urls:
                logger.debug(f"Skipping already posted URL: {video.url}")
                continue

            # Skip non-English content (title or description with non-Latin characters)
            if not self._is_likely_english(video.title, video.description):
                logger.debug(f"Skipping non-English video: {video.title}")
                continue

            # Skip opinion/commentary content (principle-based, channel-agnostic)
            if self._is_opinion_title(video.title, opinion_patterns):
                logger.debug(f"Skipping opinion/commentary title: {video.title}")
                continue

            # Enforce per-tier channel cap
            channel_key = (video.channel_handle or video.channel_name or 'unknown').lower()
            channel_counts[channel_key] = channel_counts.get(channel_key, 0) + 1
            cap = tier_caps.get(video.tier, tier_caps.get(settings.YOUTUBE_DEFAULT_TIER, 3))
            if channel_counts[channel_key] > cap:
                logger.debug(
                    f"Tier {video.tier} cap reached ({cap}) for {channel_key}: {video.title}"
                )
                continue

            filtered.append(video)

        removed = len(candidates) - len(filtered)
        if removed > 0:
            logger.info(f"Filtered out {removed} videos (duration/tier/history/editorial/diversity), {len(filtered)} remaining")

        # Log tier distribution of the remaining pool for observability
        if filtered:
            tier_dist: dict = {}
            for v in filtered:
                tier_dist[v.tier] = tier_dist.get(v.tier, 0) + 1
            dist_str = ", ".join(f"T{t}={c}" for t, c in sorted(tier_dist.items()))
            logger.info(f"Candidate pool by tier: {dist_str}")

        return filtered

    @staticmethod
    def _is_likely_english(title: str, description: str) -> bool:
        """Check if title and description are likely English by measuring Latin character ratio.

        Non-Latin scripts (Korean, Arabic, Chinese, Cyrillic, etc.) will have a low
        ratio of basic Latin characters, making this a reliable language-agnostic filter.
        """
        for text in [title, description]:
            if not text or len(text.strip()) < 10:
                continue
            # Count characters that are basic Latin letters (a-z, A-Z)
            latin_chars = sum(1 for c in text if c.isascii() and c.isalpha())
            total_alpha = sum(1 for c in text if c.isalpha())
            if total_alpha > 0 and (latin_chars / total_alpha) < 0.7:
                return False
        return True

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
