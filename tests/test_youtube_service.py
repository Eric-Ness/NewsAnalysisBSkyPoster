"""
Tests for YouTube Video Service

Tests the YouTubeVideoService class including candidate fetching,
filtering, URL history management, and video posting tracking.
"""

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import MagicMock, patch

from services.youtube_service import YouTubeVideoService
from data.models import YouTubeVideoCandidate


class TestGetVideoCandidates:
    """Tests for YouTubeVideoService.get_video_candidates()"""

    def test_returns_empty_list_when_no_data(self, mock_youtube_service):
        """Should return empty list when database returns None."""
        service, mock_db, _ = mock_youtube_service
        mock_db.get_youtube_candidates.return_value = None

        result = service.get_video_candidates()
        assert result == []

    def test_returns_empty_list_when_empty_dataframe(self, mock_youtube_service):
        """Should return empty list when database returns empty DataFrame."""
        service, mock_db, _ = mock_youtube_service
        mock_db.get_youtube_candidates.return_value = pd.DataFrame()

        result = service.get_video_candidates()
        assert result == []

    def test_converts_dataframe_to_candidates(self, mock_youtube_service):
        """Should convert DataFrame rows to YouTubeVideoCandidate instances."""
        service, mock_db, _ = mock_youtube_service

        mock_db.get_youtube_candidates.return_value = pd.DataFrame([{
            'YouTube_Video_ID': 1,
            'YouTube_Video_Key': 'abc123def45',
            'Title': 'Breaking News: Test Event',
            'Description': 'Full description here',
            'Published_Date': datetime(2026, 3, 31),
            'Thumbnail_URL': 'https://i.ytimg.com/vi/abc123def45/maxresdefault.jpg',
            'Duration_Seconds': 600,
            'View_Count': 100000,
            'Like_Count': 5000,
            'Comment_Count': 800,
            'Channel_Name': 'CNN',
            'Channel_Handle': '@CNN',
        }])

        result = service.get_video_candidates()
        assert len(result) == 1
        assert isinstance(result[0], YouTubeVideoCandidate)
        assert result[0].youtube_video_id == 1
        assert result[0].youtube_video_key == 'abc123def45'
        assert result[0].title == 'Breaking News: Test Event'
        assert result[0].url == 'https://www.youtube.com/watch?v=abc123def45'
        assert result[0].view_count == 100000


class TestFilterCandidates:
    """Tests for YouTubeVideoService.filter_candidates()"""

    def test_filters_short_duration_videos(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out videos under minimum duration."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, duration_seconds=30),  # Too short
            youtube_video_candidate_factory(video_id=2, video_key="xyz789abc01", duration_seconds=300),  # OK
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1
        assert result[0].youtube_video_id == 2

    def test_filters_blocked_channels(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out videos from blocked channels."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, channel_handle="@BlockedChannel"),
            youtube_video_candidate_factory(video_id=2, video_key="xyz789abc01", channel_handle="@GoodChannel"),
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = ["@BlockedChannel"]
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1
        assert result[0].youtube_video_id == 2

    def test_filters_long_duration_videos(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out videos over maximum duration (show segments)."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, duration_seconds=1200),  # 20 min - too long
            youtube_video_candidate_factory(video_id=2, video_key="xyz789abc01", duration_seconds=240),  # 4 min - OK
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1
        assert result[0].youtube_video_id == 2

    def test_filters_opinion_commentary_titles(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out opinion/commentary videos by title pattern."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, title="My Take on the Election Results"),
            youtube_video_candidate_factory(video_id=2, video_key="xyz789abc01", title="Hurricane Makes Landfall in Florida"),
            youtube_video_candidate_factory(video_id=3, video_key="def456ghi78", title="FULL SHOW: Morning News Roundup"),
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = [
                    r'\b(opinion|editorial|commentary|my take|my thoughts)\b',
                    r'\b(full (show|episode|program|interview))\b',
                ]
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1
        assert result[0].title == "Hurricane Makes Landfall in Florida"

    def test_filters_non_latin_script_titles(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out videos with non-Latin scripts (Korean, Arabic, Chinese, etc.)."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, title="속보: 북한 미사일 발사", description="북한이 동해로 미사일을 발사했다"),
            youtube_video_candidate_factory(video_id=2, video_key="xyz789abc01", title="عاجل: هجوم صاروخي على المنطقة", description="القوات المسلحة ردت على الهجوم"),
            youtube_video_candidate_factory(video_id=3, video_key="def456ghi78", title="Hurricane Makes Landfall in Florida", description="A major hurricane hit the coast today"),
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1
        assert result[0].title == "Hurricane Makes Landfall in Florida"

    def test_allows_english_with_some_non_latin(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should allow English titles that contain a few non-Latin characters (e.g., accented names)."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, title="Iran's Président addresses UN assembly", description="Full coverage of today's session"),
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
                result = service.filter_candidates(candidates)

        assert len(result) == 1

    def test_caps_per_channel_diversity(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should cap videos per channel to ensure source diversity."""
        service, _, _ = mock_youtube_service

        candidates = [
            youtube_video_candidate_factory(video_id=1, video_key="vid1key00001", channel_handle="@SameChannel"),
            youtube_video_candidate_factory(video_id=2, video_key="vid2key00002", channel_handle="@SameChannel"),
            youtube_video_candidate_factory(video_id=3, video_key="vid3key00003", channel_handle="@SameChannel"),
            youtube_video_candidate_factory(video_id=4, video_key="vid4key00004", channel_handle="@SameChannel"),
            youtube_video_candidate_factory(video_id=5, video_key="vid5key00005", channel_handle="@OtherChannel"),
        ]

        with patch.object(type(service), '_get_posted_urls', return_value=[]):
            with patch('services.youtube_service.settings') as mock_settings:
                mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
                mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
                mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
                mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
                mock_settings.YOUTUBE_MAX_PER_CHANNEL = 2
                result = service.filter_candidates(candidates)

        # 2 from @SameChannel (capped at 2) + 1 from @OtherChannel = 3
        assert len(result) == 3
        same_channel = [v for v in result if v.channel_handle == "@SameChannel"]
        assert len(same_channel) == 2

    def test_filters_already_posted_urls(self, mock_youtube_service, youtube_video_candidate_factory):
        """Should filter out videos whose URL is already in history."""
        service, _, history_file = mock_youtube_service

        video = youtube_video_candidate_factory(video_id=1, video_key="abc123def45")
        history_file.write_text(f"{video.url}\n")

        candidates = [video]

        with patch('services.youtube_service.settings') as mock_settings:
            mock_settings.YOUTUBE_MIN_DURATION_SECONDS = 60
            mock_settings.YOUTUBE_MAX_DURATION_SECONDS = 360
            mock_settings.YOUTUBE_BLOCKED_CHANNELS = []
            mock_settings.YOUTUBE_OPINION_TITLE_PATTERNS = []
            mock_settings.YOUTUBE_MAX_PER_CHANNEL = 3
            result = service.filter_candidates(candidates)

        assert len(result) == 0


class TestUrlHistory:
    """Tests for URL history management."""

    def test_is_url_in_history_returns_false_for_new_url(self, mock_youtube_service):
        """Should return False for URLs not in history."""
        service, _, _ = mock_youtube_service
        assert service.is_url_in_history("https://www.youtube.com/watch?v=newvideo") is False

    def test_is_url_in_history_returns_true_for_existing_url(self, mock_youtube_service):
        """Should return True for URLs already in history."""
        service, _, history_file = mock_youtube_service
        url = "https://www.youtube.com/watch?v=existingvideo"
        history_file.write_text(f"{url}\n")

        assert service.is_url_in_history(url) is True

    def test_add_url_to_history(self, mock_youtube_service):
        """Should add URL to history file."""
        service, _, history_file = mock_youtube_service
        url = "https://www.youtube.com/watch?v=newvideo"

        service._add_url_to_history(url)

        content = history_file.read_text()
        assert url in content

    def test_mark_video_posted_delegates_to_db(self, mock_youtube_service):
        """Should delegate to database for marking video as posted."""
        service, mock_db, _ = mock_youtube_service
        service.mark_video_posted(42)
        mock_db.mark_video_posted.assert_called_once_with(42)


class TestYouTubeVideoCandidate:
    """Tests for the YouTubeVideoCandidate data model."""

    def test_url_property(self, youtube_video_candidate_factory):
        """Should generate correct YouTube URL from video key."""
        video = youtube_video_candidate_factory(video_key="abc123def45")
        assert video.url == "https://www.youtube.com/watch?v=abc123def45"

    def test_engagement_score(self, youtube_video_candidate_factory):
        """Should calculate weighted engagement score."""
        video = youtube_video_candidate_factory(
            view_count=10000,
            like_count=500,
            comment_count=100
        )
        # 10000 + (500 * 10) + (100 * 5) = 10000 + 5000 + 500 = 15500
        assert video.engagement_score == 15500
