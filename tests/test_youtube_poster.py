"""
Tests for YouTube Poster Application

Tests the YouTubePoster class including the full workflow,
skip logic, cross-content dedup, and test mode.
"""

import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch, PropertyMock

from youtube_poster import YouTubePoster
from data.models import YouTubeVideoCandidate
from services.ai_service import FeedPost


@pytest.fixture
def mock_services(youtube_video_candidate_factory):
    """Create mocked services for YouTubePoster testing."""
    mock_youtube_svc = MagicMock()
    mock_ai_svc = MagicMock()
    mock_social_svc = MagicMock()

    # Default: return some candidates
    candidates = [
        youtube_video_candidate_factory(video_id=1, video_key="vid1key1234"),
        youtube_video_candidate_factory(video_id=2, video_key="vid2key5678", title="Second Video"),
    ]
    mock_youtube_svc.get_video_candidates.return_value = candidates
    mock_youtube_svc.filter_candidates.return_value = candidates
    mock_youtube_svc.is_url_in_history.return_value = False
    mock_youtube_svc.mark_video_posted.return_value = True

    # Default: AI selects videos and generates posts
    mock_ai_svc.select_youtube_videos.return_value = [
        {
            'YouTube_Video_ID': 1,
            'Title': 'Test Video 1: Breaking News Report',
            'Description': 'Test description',
            'View_Count': 50000,
            'Like_Count': 1500,
            'Comment_Count': 200,
            'Duration_Seconds': 300,
            'Channel_Name': 'CNN',
            'Channel_Handle': '@CNN',
            'url': 'https://www.youtube.com/watch?v=vid1key1234',
            'thumbnail_url': 'https://i.ytimg.com/vi/vid1key1234/maxresdefault.jpg',
            'youtube_video_key': 'vid1key1234',
        }
    ]
    mock_ai_svc.check_content_similarity.return_value = False
    mock_ai_svc.generate_tweet.return_value = {
        'tweet_text': 'Breaking news report about test event #TestNews #News',
        'summary': 'Test event summary.',
        'facets': []
    }

    # Default: posting succeeds
    mock_social_svc.get_recent_posts.return_value = []
    mock_social_svc.post_to_social.return_value = (True, 42)

    return mock_youtube_svc, mock_ai_svc, mock_social_svc


class TestYouTubePosterRun:
    """Tests for YouTubePoster.run() workflow."""

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_successful_post(self, mock_settings, mock_db, mock_services):
        """Should successfully post a YouTube video to BlueSky."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run(test_mode=False, max_posts=1)

        assert result is True
        mock_social_svc.post_to_social.assert_called_once()
        mock_youtube_svc.mark_video_posted.assert_called_once_with(1)
        mock_youtube_svc._add_url_to_history.assert_called_once()

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_test_mode_does_not_post(self, mock_settings, mock_db, mock_services):
        """Should not post in test mode."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run(test_mode=True, max_posts=1)

        assert result is True
        mock_social_svc.post_to_social.assert_not_called()
        mock_youtube_svc.mark_video_posted.assert_not_called()

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_skips_url_in_history(self, mock_settings, mock_db, mock_services):
        """Should skip videos already in URL history."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services
        mock_youtube_svc.is_url_in_history.return_value = True

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run(test_mode=False, max_posts=1)

        assert result is False
        mock_social_svc.post_to_social.assert_not_called()
        mock_db.increment_stories_skipped.assert_called()

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_skips_similar_content(self, mock_settings, mock_db, mock_services):
        """Should skip videos with content similar to recent posts."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services
        mock_ai_svc.check_content_similarity.return_value = True

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run(test_mode=False, max_posts=1)

        assert result is False
        mock_social_svc.post_to_social.assert_not_called()

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_returns_false_when_no_candidates(self, mock_settings, mock_db, mock_services):
        """Should return False when no candidates available."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services
        mock_youtube_svc.get_video_candidates.return_value = []

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run()

        assert result is False

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_skips_failed_tweet_generation(self, mock_settings, mock_db, mock_services):
        """Should skip videos when tweet generation fails."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services
        mock_ai_svc.generate_tweet.return_value = None

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        result = poster.run(test_mode=False, max_posts=1)

        assert result is False
        mock_social_svc.post_to_social.assert_not_called()

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_passes_youtube_video_id_to_social_service(self, mock_settings, mock_db, mock_services):
        """Should pass youtube_video_id through to social service."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        poster.run(test_mode=False, max_posts=1)

        call_kwargs = mock_social_svc.post_to_social.call_args
        assert call_kwargs.kwargs.get('youtube_video_id') == 1
        assert call_kwargs.kwargs.get('news_feed_id') is None

    @patch('youtube_poster.db')
    @patch('youtube_poster.settings')
    def test_generates_tweet_with_youtube_content_type(self, mock_settings, mock_db, mock_services):
        """Should call generate_tweet with content_type='youtube_video'."""
        mock_settings.validate_settings = MagicMock()
        mock_settings.YOUTUBE_MAX_POSTS_PER_RUN = 1
        mock_settings.YOUTUBE_MAX_RETRIES = 15
        mock_youtube_svc, mock_ai_svc, mock_social_svc = mock_services

        poster = YouTubePoster(
            youtube_service=mock_youtube_svc,
            ai_service=mock_ai_svc,
            social_service=mock_social_svc,
            validate=False
        )
        poster.run(test_mode=False, max_posts=1)

        call_kwargs = mock_ai_svc.generate_tweet.call_args
        assert call_kwargs.kwargs.get('content_type') == 'youtube_video'
        assert call_kwargs.kwargs.get('channel_name') == 'CNN'
