"""
YouTube Video Poster Application

This is the entry point for the YouTube Video Poster application.
It fetches YouTube news videos, selects the most newsworthy ones,
and posts them to social media platforms (BlueSky).

Runs independently from the article poster (main.py) on its own schedule.

Author: Eric Ness
Version: 1.0
"""

import sys
import argparse
import logging
from datetime import date
from typing import Optional, List

from config import settings
from utils.logger import get_logger, setup_file_logging
from utils.exceptions import (
    NewsPosterError, AIServiceError, SocialMediaError, DatabaseError
)
from data.database import db
from services.youtube_service import YouTubeVideoService
from services.ai_service import AIService, FeedPost
from services.social_service import SocialService

# Set up logging
logger = get_logger(__name__)


class YouTubePoster:
    """Main application class for the YouTube Video Poster.

    This class orchestrates the process of fetching YouTube video candidates,
    selecting the most newsworthy ones using AI, and posting them to social media.

    Services can be injected via constructor for testing and flexibility.
    """

    def __init__(
        self,
        youtube_service: Optional[YouTubeVideoService] = None,
        ai_service: Optional[AIService] = None,
        social_service: Optional[SocialService] = None,
        validate: bool = True
    ):
        """Initialize the YouTube Poster application.

        Args:
            youtube_service: Service for YouTube video operations. Defaults to new YouTubeVideoService.
            ai_service: Service for AI operations. Defaults to new AIService.
            social_service: Service for BlueSky posting. Defaults to new SocialService.
            validate: Whether to validate settings on init. Defaults to True.
        """
        self.youtube_service = youtube_service if youtube_service is not None else YouTubeVideoService()
        self.ai_service = ai_service if ai_service is not None else AIService()
        self.social_service = social_service if social_service is not None else SocialService()

        if validate:
            settings.validate_settings()

    def run(self, test_mode: bool = False, max_posts: int = settings.YOUTUBE_MAX_POSTS_PER_RUN) -> bool:
        """
        Run the YouTube video posting workflow.

        Args:
            test_mode: If True, runs without actually posting to social media.
            max_posts: Maximum number of videos to post in this run.

        Returns:
            bool: True if at least one video was posted successfully, False otherwise.
        """
        try:
            today = date.today()
            posts_made = 0

            # 1. Fetch video candidates from YouTube database
            logger.info("Fetching YouTube video candidates...")
            candidates = self.youtube_service.get_video_candidates()
            if not candidates:
                logger.warning("No YouTube video candidates available")
                return False

            logger.info(f"Found {len(candidates)} raw candidates from database")

            # 2. Filter candidates (duration, blocked channels, URL history)
            candidates = self.youtube_service.filter_candidates(candidates)
            if not candidates:
                logger.warning("No candidates remaining after filtering")
                return False

            logger.info(f"{len(candidates)} candidates after filtering")

            # 3. Get recent BlueSky posts for cross-content dedup
            recent_posts = self.social_service.get_recent_posts()
            logger.info(f"Retrieved {len(recent_posts)} recent BlueSky posts for dedup")

            # 4. Prepare candidate dicts for AI selection
            candidate_dicts = [
                {
                    'YouTube_Video_ID': v.youtube_video_id,
                    'Title': v.title,
                    'Description': v.description[:500] if v.description else '',
                    'View_Count': v.view_count,
                    'Like_Count': v.like_count,
                    'Comment_Count': v.comment_count,
                    'Duration_Seconds': v.duration_seconds,
                    'Channel_Name': v.channel_name,
                    'Channel_Handle': v.channel_handle,
                    'Tier': v.tier,
                    'url': v.url,
                    'thumbnail_url': v.thumbnail_url,
                    'youtube_video_key': v.youtube_video_key,
                }
                for v in candidates
            ]

            # 5. AI selects top videos
            selected_videos = self.ai_service.select_youtube_videos(
                candidate_dicts, recent_posts, max_count=settings.YOUTUBE_MAX_RETRIES
            )
            if not selected_videos:
                logger.warning("No videos selected by AI")
                return False

            logger.info(f"AI selected {len(selected_videos)} video candidates to try")

            # 6. Try each selected video until we hit max_posts
            for video_dict in selected_videos:
                if posts_made >= max_posts:
                    break

                video_title = video_dict['Title']
                video_url = video_dict['url']
                logger.info(f"Trying video: {video_title}")

                # 6a. Check URL history
                if self.youtube_service.is_url_in_history(video_url):
                    logger.warning(f"Video URL already in history: {video_url}")
                    db.increment_stories_skipped(today)
                    continue

                # 6b. Check content similarity against recent posts
                description = video_dict.get('Description', '') or ''
                if self.ai_service.check_content_similarity(
                    video_title, description, recent_posts
                ):
                    logger.warning(f"Video content too similar to recent posts: {video_title}")
                    db.increment_stories_skipped(today)
                    continue

                # 6c. Generate social media post text
                tweet_data = self.ai_service.generate_tweet(
                    article_text=description,
                    article_title=video_title,
                    article_url=video_url,
                    content_type="youtube_video",
                    channel_name=video_dict.get('Channel_Name')
                )

                if not tweet_data:
                    logger.warning(f"Failed to generate post for video: {video_title}")
                    db.increment_stories_skipped(today)
                    continue

                # 6d. Post to BlueSky (unless test mode)
                if not test_mode:
                    posted, social_post_id = self.social_service.post_to_social(
                        tweet_text=tweet_data['tweet_text'],
                        article_url=video_url,
                        article_title=video_title,
                        article_image=video_dict.get('thumbnail_url'),
                        facets=tweet_data.get('facets'),
                        news_feed_id=None,
                        youtube_video_id=video_dict['YouTube_Video_ID']
                    )

                    if posted:
                        logger.info(f"Successfully posted YouTube video to BlueSky: {video_title}")
                        if social_post_id:
                            logger.info(f"Stored with Social_Post_ID: {social_post_id}")

                        # 6e. Mark video as posted in YouTube DB
                        self.youtube_service.mark_video_posted(video_dict['YouTube_Video_ID'])

                        # 6f. Add to URL history
                        self.youtube_service._add_url_to_history(video_url)

                        # 6g. Track metrics
                        db.increment_stories_posted(today)

                        posts_made += 1

                        # Add to recent posts for dedup within this run
                        recent_posts.append(FeedPost(
                            text=tweet_data['tweet_text'],
                            url=video_url,
                            title=video_title,
                            timestamp=date.today()
                        ))
                    else:
                        logger.warning(f"Failed to post video to BlueSky: {video_title}")
                else:
                    # Test mode
                    logger.info(f"TEST MODE: Would post YouTube video: {video_title}")
                    logger.info(f"Social media text: {tweet_data['tweet_text']}")
                    logger.info(f"Video URL: {video_url}")
                    posts_made += 1

            # Record profile metrics if we posted anything
            if posts_made > 0:
                self._record_profile_metrics(today)
                logger.info(f"YouTube Poster completed: {posts_made} video(s) posted")
                return True

            logger.warning("All selected YouTube videos failed processing")
            return False

        except AIServiceError as e:
            logger.error(f"AI service error in YouTube posting: {e}", exc_info=True)
            return False
        except SocialMediaError as e:
            logger.error(f"Social media error in YouTube posting: {e}", exc_info=True)
            return False
        except DatabaseError as e:
            logger.error(f"Database error in YouTube posting: {e}", exc_info=True)
            return False
        except NewsPosterError as e:
            logger.error(f"YouTube poster error: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error in YouTube poster: {e}", exc_info=True)
            return False

    def _record_profile_metrics(self, today: date) -> None:
        """Fetch BlueSky profile stats and upsert today's daily metrics row."""
        try:
            profile_metrics = self.social_service.get_profile_metrics()
            if not profile_metrics:
                return

            existing = db.get_daily_metrics(today)

            from data.models import BlueSkyDailyMetrics
            metrics = BlueSkyDailyMetrics(
                snapshot_date=today,
                follower_count=profile_metrics['follower_count'],
                following_count=profile_metrics['following_count'],
                total_posts_count=profile_metrics['total_posts_count'],
                stories_posted=existing['Stories_Posted'] if existing else 0,
                stories_skipped=existing['Stories_Skipped'] if existing else 0,
            )
            db.upsert_daily_metrics(metrics)
            logger.info(f"Recorded daily profile metrics for {today}")
        except Exception as e:
            logger.error(f"Failed to record daily profile metrics: {e}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='YouTube Video Poster Application')
    parser.add_argument('--test', action='store_true', help='Run in test mode without posting')
    parser.add_argument('--max-posts', type=int, default=settings.YOUTUBE_MAX_POSTS_PER_RUN,
                        help='Maximum number of videos to post per run')
    parser.add_argument('--log-file', type=str, default='youtube_poster.log', help='Log file path')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Logging level')
    return parser.parse_args()


def main():
    """Main entry point for the YouTube Poster application."""
    args = parse_arguments()

    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_file_logging(args.log_file, log_level)

    logger.info("Starting YouTube Video Poster application")
    logger.info(f"Max posts per run: {args.max_posts}")

    try:
        poster = YouTubePoster()
        success = poster.run(test_mode=args.test, max_posts=args.max_posts)

        if success:
            logger.info("YouTube Poster completed successfully")
            exit_code = 0
        else:
            logger.warning("YouTube Poster completed with warnings or errors")
            exit_code = 1

    except Exception as e:
        logger.error(f"Unhandled exception in YouTube Poster: {e}", exc_info=True)
        exit_code = 2

    logger.info(f"YouTube Poster application finished with exit code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
