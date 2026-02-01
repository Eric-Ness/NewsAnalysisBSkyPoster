"""
Tests for Twitter Service - Twitter/X API Integration

Tests cover authentication (OAuth 1.0a and Bearer Token), tweet retrieval,
posting, media upload, rate limiting, and error handling for the TwitterService class.

Note: These tests use module-level patching to handle the isinstance() checks in
the TwitterService code that compare against tweepy.API and tweepy.Client.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
import sys
import os
import importlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.exceptions import AuthenticationError, PostingError, MediaUploadError, RateLimitError, SocialMediaError
from data.database import SocialPostData


# =============================================================================
# Module-level setup for mocking tweepy
# =============================================================================

# Create mock instances that will be returned by the fake classes
_mock_api_instance = None
_mock_client_instance = None


class FakeAPI:
    """Fake tweepy.API class for isinstance checks."""

    def __new__(cls, *args, **kwargs):
        global _mock_api_instance
        if _mock_api_instance is not None:
            return _mock_api_instance
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        pass


class FakeClient:
    """Fake tweepy.Client class for isinstance checks."""

    def __new__(cls, *args, **kwargs):
        global _mock_client_instance
        if _mock_client_instance is not None:
            return _mock_client_instance
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        pass


class FakeOAuth1UserHandler:
    """Fake OAuth handler."""
    def __init__(self, *args, **kwargs):
        pass


# Create mock tweepy module
mock_tweepy_module = MagicMock()
mock_tweepy_module.API = FakeAPI
mock_tweepy_module.Client = FakeClient
mock_tweepy_module.OAuth1UserHandler = FakeOAuth1UserHandler

# Patch tweepy in sys.modules before importing TwitterService
sys.modules['tweepy'] = mock_tweepy_module


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test."""
    global _mock_api_instance, _mock_client_instance
    _mock_api_instance = None
    _mock_client_instance = None
    mock_tweepy_module.API = FakeAPI
    mock_tweepy_module.Client = FakeClient
    mock_tweepy_module.OAuth1UserHandler = FakeOAuth1UserHandler
    yield
    # Cleanup after test
    _mock_api_instance = None
    _mock_client_instance = None


@pytest.fixture
def mock_settings_oauth():
    """Mock settings for OAuth 1.0a authentication."""
    settings = MagicMock()
    settings.TWITTER_API_KEY = "test-api-key"
    settings.TWITTER_API_KEY_SECRET = "test-api-secret"
    settings.TWITTER_ACCESS_TOKEN = "test-access-token"
    settings.TWITTER_ACCESS_TOKEN_SECRET = "test-access-secret"
    settings.TWITTER_BEARER_TOKEN = None
    settings.TWITTER_FETCH_LIMIT = 50
    settings.TWITTER_API_MAX_RESULTS = 100
    settings.TWITTER_URL_LENGTH = 23
    settings.TWITTER_CHARACTER_LIMIT = 280
    settings.TWEET_TRUNCATION_PADDING = 4
    settings.TWITTER_IMAGE_TIMEOUT = 10
    return settings


@pytest.fixture
def mock_settings_bearer():
    """Mock settings for Bearer Token authentication."""
    settings = MagicMock()
    settings.TWITTER_API_KEY = None
    settings.TWITTER_API_KEY_SECRET = None
    settings.TWITTER_ACCESS_TOKEN = None
    settings.TWITTER_ACCESS_TOKEN_SECRET = None
    settings.TWITTER_BEARER_TOKEN = "test-bearer-token"
    settings.TWITTER_FETCH_LIMIT = 50
    settings.TWITTER_API_MAX_RESULTS = 100
    settings.TWITTER_URL_LENGTH = 23
    settings.TWITTER_CHARACTER_LIMIT = 280
    settings.TWEET_TRUNCATION_PADDING = 4
    settings.TWITTER_IMAGE_TIMEOUT = 10
    return settings


@pytest.fixture
def mock_settings_missing():
    """Mock settings with missing credentials."""
    settings = MagicMock()
    settings.TWITTER_API_KEY = None
    settings.TWITTER_API_KEY_SECRET = None
    settings.TWITTER_ACCESS_TOKEN = None
    settings.TWITTER_ACCESS_TOKEN_SECRET = None
    settings.TWITTER_BEARER_TOKEN = None
    settings.TWITTER_FETCH_LIMIT = 50
    settings.TWITTER_API_MAX_RESULTS = 100
    settings.TWITTER_URL_LENGTH = 23
    settings.TWITTER_CHARACTER_LIMIT = 280
    settings.TWEET_TRUNCATION_PADDING = 4
    settings.TWITTER_IMAGE_TIMEOUT = 10
    return settings


@pytest.fixture
def mock_v1_api():
    """Create a mock API instance that passes isinstance checks."""
    global _mock_api_instance

    # Create instance that IS a FakeAPI
    mock_instance = FakeAPI.__new__(FakeAPI)
    mock_instance.verify_credentials = MagicMock(return_value=MagicMock())
    mock_instance.user_timeline = MagicMock(return_value=[])
    mock_instance.update_status = MagicMock()
    mock_instance.media_upload = MagicMock()

    _mock_api_instance = mock_instance
    return mock_instance


@pytest.fixture
def mock_v2_client():
    """Create a mock Client instance that passes isinstance checks."""
    global _mock_client_instance

    # Create instance that IS a FakeClient
    mock_instance = FakeClient.__new__(FakeClient)
    mock_user = MagicMock()
    mock_user.data = MagicMock()
    mock_user.data.id = "123456789"
    mock_user.data.username = "testuser"
    mock_user.data.name = "Test User"
    mock_user.data.profile_image_url = "https://example.com/avatar.jpg"
    mock_instance.get_user = MagicMock(return_value=mock_user)
    mock_instance.get_me = MagicMock(return_value=mock_user)
    mock_instance.get_users_tweets = MagicMock()
    mock_instance.create_tweet = MagicMock()

    _mock_client_instance = mock_instance
    return mock_instance


@pytest.fixture
def mock_v1_timeline_response():
    """Create a mock v1.1 API timeline response."""
    def create_mock_tweet(text, url=None, created_at=None):
        mock_tweet = MagicMock()
        mock_tweet.full_text = text
        mock_tweet.text = text
        mock_tweet.created_at = created_at or datetime.now()
        mock_tweet.id = 123456789

        if url:
            mock_tweet.entities = {
                'urls': [{'expanded_url': url}]
            }
        else:
            mock_tweet.entities = {'urls': []}

        return mock_tweet

    return [
        create_mock_tweet("First test tweet https://t.co/abc", "https://example.com/article1"),
        create_mock_tweet("Second test tweet", None),
        create_mock_tweet("Third test tweet https://t.co/def", "https://example.com/article2"),
    ]


@pytest.fixture
def mock_v2_timeline_response():
    """Create a mock v2 API timeline response."""
    def create_mock_tweet(text, url=None, created_at=None):
        mock_tweet = MagicMock()
        mock_tweet.text = text
        mock_tweet.created_at = created_at or datetime.now()
        mock_tweet.id = "123456789"

        if url:
            mock_tweet.entities = {
                'urls': [{'expanded_url': url}]
            }
        else:
            # Use empty dict instead of None to match API behavior
            mock_tweet.entities = {'urls': []}

        return mock_tweet

    mock_response = MagicMock()
    mock_response.data = [
        create_mock_tweet("First v2 tweet", "https://example.com/article1"),
        create_mock_tweet("Second v2 tweet", None),
    ]
    return mock_response


@pytest.fixture
def mock_tweet_post_response():
    """Create a mock tweet post response for v1.1 API."""
    mock_response = MagicMock()
    mock_response.id = 987654321
    mock_response.user = MagicMock()
    mock_response.user.screen_name = "testuser"
    mock_response.user.name = "Test User"
    mock_response.user.profile_image_url_https = "https://example.com/avatar.jpg"
    return mock_response


@pytest.fixture
def mock_tweet_v2_post_response():
    """Create a mock tweet post response for v2 API."""
    mock_response = MagicMock()
    mock_response.data = {'id': '987654321', 'text': 'Test tweet text'}
    return mock_response


@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = MagicMock()
    db.insert_social_post.return_value = 42
    return db


# =============================================================================
# Helper to create a TwitterService with mocked dependencies
# =============================================================================

def create_twitter_service(mock_settings, mock_db=None, mock_requests=None):
    """
    Create a TwitterService with mocked dependencies.

    This function:
    1. Reloads the module to pick up mocked tweepy
    2. Replaces module-level dependencies
    3. Creates and returns the service
    """
    import services.twitter_service as ts

    # Reload to ensure fresh module state with our mock tweepy
    importlib.reload(ts)

    # Replace module-level dependencies AFTER reload
    ts.settings = mock_settings
    ts.tweepy = mock_tweepy_module

    if mock_db is not None:
        ts.db = mock_db

    if mock_requests is not None:
        ts.requests = mock_requests

    # Create the service
    return ts.TwitterService()


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAuthentication:
    """Tests for Twitter authentication methods."""

    def test_setup_twitter_oauth_success(self, mock_settings_oauth, mock_v1_api):
        """OAuth 1.0a authentication succeeds."""
        service = create_twitter_service(mock_settings_oauth)

        mock_v1_api.verify_credentials.assert_called_once()
        assert service.client is not None
        assert isinstance(service.client, FakeAPI)

    def test_setup_twitter_bearer_success(self, mock_settings_bearer, mock_v2_client):
        """Bearer Token authentication succeeds."""
        service = create_twitter_service(mock_settings_bearer)

        mock_v2_client.get_user.assert_called_once_with(username="twitter")
        assert service.client is not None
        assert isinstance(service.client, FakeClient)

    def test_setup_twitter_oauth_failure(self, mock_settings_oauth, mock_v1_api):
        """Handles OAuth authentication failure."""
        mock_v1_api.verify_credentials.side_effect = Exception("Invalid credentials")

        service = create_twitter_service(mock_settings_oauth)
        mock_v1_api.verify_credentials.assert_called_once()

    def test_setup_twitter_bearer_failure(self, mock_settings_bearer, mock_v2_client):
        """Handles Bearer Token authentication failure."""
        mock_v2_client.get_user.side_effect = Exception("Invalid bearer token")

        service = create_twitter_service(mock_settings_bearer)
        mock_v2_client.get_user.assert_called_once()

    def test_setup_twitter_missing_credentials(self, mock_settings_missing):
        """Handles missing API keys."""
        service = create_twitter_service(mock_settings_missing)
        assert service.client is None

    def test_setup_twitter_network_error(self, mock_settings_oauth, mock_v1_api):
        """Handles network errors during auth."""
        mock_v1_api.verify_credentials.side_effect = ConnectionError("Network unreachable")

        service = create_twitter_service(mock_settings_oauth)
        mock_v1_api.verify_credentials.assert_called_once()

    def test_setup_twitter_authentication_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies AuthenticationError propagation."""
        mock_v1_api.verify_credentials.side_effect = AuthenticationError("Auth failed")

        with pytest.raises(AuthenticationError):
            create_twitter_service(mock_settings_oauth)


# =============================================================================
# Tweet Retrieval Tests
# =============================================================================

class TestTweetRetrieval:
    """Tests for retrieving recent tweets."""

    def test_get_recent_tweets_success(self, mock_settings_oauth, mock_v1_api, mock_v1_timeline_response):
        """Returns list of recent tweets."""
        mock_v1_api.user_timeline.return_value = mock_v1_timeline_response

        service = create_twitter_service(mock_settings_oauth)
        tweets = service.get_recent_tweets()

        assert len(tweets) == 3
        assert tweets[0].text == "First test tweet https://t.co/abc"
        assert tweets[0].url == "https://example.com/article1"
        assert tweets[1].url is None

    def test_get_recent_tweets_empty(self, mock_settings_oauth, mock_v1_api):
        """Handles empty timeline."""
        mock_v1_api.user_timeline.return_value = []

        service = create_twitter_service(mock_settings_oauth)
        tweets = service.get_recent_tweets()

        assert tweets == []

    def test_get_recent_tweets_limit(self, mock_settings_oauth, mock_v1_api):
        """Respects limit parameter."""
        mock_v1_api.user_timeline.return_value = []

        service = create_twitter_service(mock_settings_oauth)
        service.get_recent_tweets(limit=25)

        mock_v1_api.user_timeline.assert_called_with(count=25, tweet_mode="extended")

    def test_get_recent_tweets_not_authenticated(self, mock_settings_missing):
        """Handles unauthenticated state."""
        service = create_twitter_service(mock_settings_missing)
        tweets = service.get_recent_tweets()

        assert tweets == []

    def test_get_recent_tweets_api_error(self, mock_settings_oauth, mock_v1_api):
        """Handles Twitter API errors."""
        mock_v1_api.user_timeline.side_effect = Exception("API Error")

        service = create_twitter_service(mock_settings_oauth)
        tweets = service.get_recent_tweets()

        assert tweets == []

    def test_get_recent_tweets_v1_format(self, mock_settings_oauth, mock_v1_api, mock_v1_timeline_response):
        """Tests v1.1 API response format."""
        mock_v1_api.user_timeline.return_value = mock_v1_timeline_response

        service = create_twitter_service(mock_settings_oauth)
        tweets = service.get_recent_tweets()

        assert len(tweets) == 3
        assert tweets[0].text is not None
        assert tweets[0].timestamp is not None
        assert tweets[0].url == "https://example.com/article1"
        assert tweets[1].url is None

    def test_get_recent_tweets_v2_format(self, mock_settings_bearer, mock_v2_client, mock_v2_timeline_response):
        """Tests v2 API response format."""
        mock_v2_client.get_users_tweets.return_value = mock_v2_timeline_response

        service = create_twitter_service(mock_settings_bearer)
        tweets = service.get_recent_tweets()

        assert len(tweets) == 2
        assert tweets[0].text == "First v2 tweet"
        assert tweets[0].url == "https://example.com/article1"

    def test_get_recent_tweets_social_media_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies SocialMediaError propagation."""
        mock_v1_api.user_timeline.side_effect = SocialMediaError("API Error")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(SocialMediaError):
            service.get_recent_tweets()


# =============================================================================
# Posting Tests
# =============================================================================

class TestPosting:
    """Tests for posting tweets."""

    def test_post_tweet_success(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Posts tweet successfully."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet content",
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is True
        assert post_id == 42
        mock_v1_api.update_status.assert_called_once()

    def test_post_tweet_with_image(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Posts tweet with image media."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response
        mock_media = MagicMock()
        mock_media.media_id = 111222333
        mock_v1_api.media_upload.return_value = mock_media

        mock_requests = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_requests.get.return_value = mock_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db, mock_requests=mock_requests)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet with image",
            article_url="https://example.com/article",
            article_title="Test Article",
            article_image="https://example.com/image.jpg"
        )

        assert success is True
        mock_requests.get.assert_called_once()
        mock_v1_api.media_upload.assert_called_once()

    def test_post_tweet_text_truncation(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Truncates long tweets to character limit."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response

        long_text = "A" * 300

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text=long_text,
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is True
        call_args = mock_v1_api.update_status.call_args
        posted_text = call_args[1]['status']
        # The truncation accounts for Twitter's t.co URL shortening (23 chars)
        # So the text portion (before the URL) should be truncated
        # Available chars = 280 - 23 (URL) = 257, then minus 4 (padding) for "..." = 253
        # Text should be truncated to 253 chars + "..."
        assert "..." in posted_text
        # Verify the text was actually truncated (original was 300 chars)
        text_without_url = posted_text.rsplit(' ', 1)[0]  # Remove the URL part
        assert len(text_without_url) < 300

    def test_post_tweet_url_accounting(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Accounts for URL length in character limit."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response

        text = "B" * 250

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text=text,
            article_url="https://example.com/very/long/url/that/doesnt/matter",
            article_title="Test Article"
        )

        assert success is True

    def test_post_tweet_failure(self, mock_settings_oauth, mock_v1_api):
        """Returns False on API failure."""
        mock_v1_api.update_status.side_effect = Exception("API Error")

        service = create_twitter_service(mock_settings_oauth)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet content",
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is False
        assert post_id is None

    def test_post_tweet_db_integration(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Verifies database insert is called."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet content",
            article_url="https://example.com/article",
            article_title="Test Article",
            news_feed_id=123
        )

        assert success is True
        mock_db.insert_social_post.assert_called_once()
        call_args = mock_db.insert_social_post.call_args[0][0]
        assert isinstance(call_args, SocialPostData)
        assert call_args.platform == 'twitter'
        assert call_args.article_url == "https://example.com/article"
        assert call_args.news_feed_id == 123

    def test_post_tweet_not_authenticated(self, mock_settings_missing):
        """Handles posting when not authenticated."""
        service = create_twitter_service(mock_settings_missing)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet content",
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is False
        assert post_id is None

    def test_post_tweet_v2_api(self, mock_v2_client, mock_tweet_v2_post_response, mock_db):
        """Posts tweet using v2 API with OAuth credentials."""
        mock_settings = MagicMock()
        mock_settings.TWITTER_API_KEY = None
        mock_settings.TWITTER_API_KEY_SECRET = None
        mock_settings.TWITTER_ACCESS_TOKEN = "test-access-token"
        mock_settings.TWITTER_ACCESS_TOKEN_SECRET = "test-access-secret"
        mock_settings.TWITTER_BEARER_TOKEN = "test-bearer-token"
        mock_settings.TWITTER_FETCH_LIMIT = 50
        mock_settings.TWITTER_API_MAX_RESULTS = 100
        mock_settings.TWITTER_URL_LENGTH = 23
        mock_settings.TWITTER_CHARACTER_LIMIT = 280
        mock_settings.TWEET_TRUNCATION_PADDING = 4
        mock_settings.TWITTER_IMAGE_TIMEOUT = 10

        mock_v2_client.create_tweet.return_value = mock_tweet_v2_post_response

        service = create_twitter_service(mock_settings, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text="Test v2 tweet",
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is True
        mock_v2_client.create_tweet.assert_called_once()

    def test_post_tweet_posting_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies PostingError propagation."""
        mock_v1_api.update_status.side_effect = PostingError("Posting failed")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(PostingError):
            service.post_tweet(
                tweet_text="Test tweet content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )


# =============================================================================
# Rate Limiting Tests
# =============================================================================

class TestRateLimiting:
    """Tests for rate limit handling."""

    def test_rate_limit_error(self, mock_settings_oauth, mock_v1_api):
        """Raises RateLimitError when rate limited."""
        mock_v1_api.update_status.side_effect = RateLimitError("Rate limit exceeded")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(RateLimitError):
            service.post_tweet(
                tweet_text="Test tweet content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )

    def test_rate_limit_response_handling(self, mock_settings_oauth, mock_v1_api):
        """Handles 429 responses appropriately."""
        mock_v1_api.user_timeline.side_effect = RateLimitError("Too Many Requests")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(RateLimitError):
            service.get_recent_tweets()


# =============================================================================
# Media Upload Tests
# =============================================================================

class TestMediaUpload:
    """Tests for media upload functionality."""

    def test_upload_media_success(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Successfully uploads media."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response
        mock_media = MagicMock()
        mock_media.media_id = 111222333
        mock_v1_api.media_upload.return_value = mock_media

        mock_requests = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\x89PNG\r\n\x1a\n"
        mock_requests.get.return_value = mock_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db, mock_requests=mock_requests)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet with image",
            article_url="https://example.com/article",
            article_title="Test Article",
            article_image="https://example.com/image.png"
        )

        assert success is True
        mock_v1_api.media_upload.assert_called_once()

    def test_upload_media_failure(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Raises MediaUploadError on failure."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response
        mock_v1_api.media_upload.side_effect = MediaUploadError("Upload failed")

        mock_requests = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_requests.get.return_value = mock_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db, mock_requests=mock_requests)

        with pytest.raises(MediaUploadError):
            service.post_tweet(
                tweet_text="Test tweet with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.jpg"
            )

    def test_upload_media_download_failure(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response, mock_db):
        """Handles image download failure gracefully."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response

        mock_requests = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db, mock_requests=mock_requests)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet with image",
            article_url="https://example.com/article",
            article_title="Test Article",
            article_image="https://example.com/image.jpg"
        )

        assert success is True
        mock_v1_api.media_upload.assert_not_called()


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling and propagation."""

    def test_authentication_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies AuthenticationError propagation from setup."""
        mock_v1_api.verify_credentials.side_effect = AuthenticationError("Invalid credentials")

        with pytest.raises(AuthenticationError):
            create_twitter_service(mock_settings_oauth)

    def test_posting_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies PostingError propagation."""
        mock_v1_api.update_status.side_effect = PostingError("Rate limited")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(PostingError):
            service.post_tweet(
                tweet_text="Test content",
                article_url="https://example.com",
                article_title="Test"
            )

    def test_rate_limit_error_propagation(self, mock_settings_oauth, mock_v1_api):
        """Verifies RateLimitError propagation."""
        mock_v1_api.update_status.side_effect = RateLimitError("Rate limit exceeded")

        service = create_twitter_service(mock_settings_oauth)

        with pytest.raises(RateLimitError):
            service.post_tweet(
                tweet_text="Test content",
                article_url="https://example.com",
                article_title="Test"
            )

    def test_db_error_handled_gracefully(self, mock_settings_oauth, mock_v1_api, mock_tweet_post_response):
        """Database errors should not prevent successful post."""
        mock_v1_api.update_status.return_value = mock_tweet_post_response
        mock_db = MagicMock()
        mock_db.insert_social_post.side_effect = Exception("DB connection failed")

        service = create_twitter_service(mock_settings_oauth, mock_db=mock_db)
        success, post_id = service.post_tweet(
            tweet_text="Test tweet content",
            article_url="https://example.com/article",
            article_title="Test Article"
        )

        assert success is True
        assert post_id is None


# =============================================================================
# Integration Tests with Fixtures
# =============================================================================

class TestSocialPostDataFactory:
    """Tests using the social_post_data_factory fixture."""

    def test_factory_creates_valid_twitter_post(self, social_post_data_factory):
        """Factory creates valid Twitter post data."""
        post = social_post_data_factory(
            platform='twitter',
            post_text='Test tweet from factory',
            article_url='https://example.com/test'
        )

        assert post.platform == 'twitter'
        assert post.post_text == 'Test tweet from factory'
        assert post.article_url == 'https://example.com/test'
        assert 'twitter.com' in post.post_url

    def test_factory_with_custom_timestamp(self, social_post_data_factory):
        """Factory respects custom created_at timestamp."""
        custom_time = datetime(2024, 1, 15, 12, 0, 0)
        post = social_post_data_factory(
            platform='twitter',
            created_at=custom_time
        )

        assert post.created_at == custom_time


# =============================================================================
# Enabled/Disabled State Tests
# =============================================================================

class TestEnabledDisabledState:
    """Tests for enabled/disabled state handling."""

    def test_service_disabled_via_parameter(self):
        """Service can be disabled via enabled parameter."""
        import services.twitter_service as ts
        importlib.reload(ts)
        ts.settings = MagicMock()
        ts.settings.ENABLE_TWITTER = True  # Setting says enabled
        ts.tweepy = mock_tweepy_module

        # But we override with enabled=False
        service = ts.TwitterService(
            enabled=False,
            api_key="test",
            api_key_secret="test",
            access_token="test",
            access_token_secret="test"
        )

        assert service.enabled is False
        assert service.client is None

    def test_service_enabled_from_settings(self):
        """Service uses ENABLE_TWITTER from settings by default."""
        import services.twitter_service as ts
        importlib.reload(ts)

        mock_settings = MagicMock()
        mock_settings.ENABLE_TWITTER = False
        mock_settings.TWITTER_API_KEY = "test"
        mock_settings.TWITTER_API_KEY_SECRET = "test"
        mock_settings.TWITTER_ACCESS_TOKEN = "test"
        mock_settings.TWITTER_ACCESS_TOKEN_SECRET = "test"
        mock_settings.TWITTER_BEARER_TOKEN = None

        ts.settings = mock_settings
        ts.tweepy = mock_tweepy_module

        service = ts.TwitterService()

        assert service.enabled is False
        assert service.client is None

    def test_get_recent_tweets_when_disabled(self):
        """get_recent_tweets returns empty list when disabled."""
        import services.twitter_service as ts
        importlib.reload(ts)
        ts.settings = MagicMock()
        ts.settings.ENABLE_TWITTER = False
        ts.tweepy = mock_tweepy_module

        service = ts.TwitterService(enabled=False)
        tweets = service.get_recent_tweets()

        assert tweets == []

    def test_post_tweet_when_disabled(self):
        """post_tweet returns (False, None) when disabled."""
        import services.twitter_service as ts
        importlib.reload(ts)
        ts.settings = MagicMock()
        ts.settings.ENABLE_TWITTER = False
        ts.tweepy = mock_tweepy_module

        service = ts.TwitterService(enabled=False)
        success, post_id = service.post_tweet(
            tweet_text="Test",
            article_url="https://example.com",
            article_title="Test"
        )

        assert success is False
        assert post_id is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
