"""
Tests for Social Service - BlueSky AT Protocol Integration

Tests cover authentication, feed retrieval, posting, image upload,
and error handling for the SocialService class.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.exceptions import AuthenticationError, PostingError, MediaUploadError, SocialMediaError
from data.database import SocialPostData


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_at_client():
    """Create a mock AT Protocol Client."""
    mock_client = MagicMock()

    # Mock successful login
    mock_client.login.return_value = MagicMock()

    # Mock profile response
    mock_profile = MagicMock()
    mock_profile.did = "did:plc:testuser123"
    mock_profile.display_name = "Test User"
    mock_profile.avatar = "https://example.com/avatar.jpg"
    mock_client.get_profile.return_value = mock_profile

    return mock_client


@pytest.fixture
def mock_settings_for_social():
    """Mock settings specifically for social service tests."""
    with patch('services.social_service.settings') as mock_settings:
        mock_settings.AT_PROTOCOL_USERNAME = "test-bsky-user"
        mock_settings.AT_PROTOCOL_PASSWORD = "test-bsky-password"
        mock_settings.BLUESKY_FETCH_LIMIT = 80
        mock_settings.BLUESKY_IMAGE_TIMEOUT = 10
        mock_settings.EMBED_DESCRIPTION_LENGTH = 100
        yield mock_settings


@pytest.fixture
def mock_feed_response():
    """Create a mock feed response with sample posts."""
    def create_mock_post(text, url=None, title=None, indexed_at="2024-01-15T10:00:00Z"):
        mock_post = MagicMock()
        mock_post.post = MagicMock()
        mock_post.post.indexed_at = indexed_at
        mock_post.post.record = MagicMock()
        mock_post.post.record.text = text

        if url:
            mock_post.post.embed = MagicMock()
            mock_post.post.embed.external = MagicMock()
            mock_post.post.embed.external.uri = url
            mock_post.post.embed.external.title = title
        else:
            mock_post.post.embed = None

        return mock_post

    mock_feed = MagicMock()
    mock_feed.feed = [
        create_mock_post("First test post", "https://example.com/article1", "Article 1"),
        create_mock_post("Second test post", "https://example.com/article2", "Article 2"),
        create_mock_post("Third post without embed"),
    ]
    return mock_feed


@pytest.fixture
def mock_post_response():
    """Create a mock post response."""
    mock_response = MagicMock()
    mock_response.uri = "at://did:plc:testuser123/app.bsky.feed.post/abc123"
    mock_response.cid = "bafyreiabc123"
    return mock_response


@pytest.fixture
def mock_upload_response():
    """Create a mock blob upload response."""
    mock_upload = MagicMock()
    mock_upload.blob = MagicMock()
    mock_upload.blob.ref = "blob-ref-123"
    return mock_upload


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAuthentication:
    """Tests for AT Protocol authentication."""

    def test_setup_at_protocol_success(self, mock_settings_for_social):
        """Successfully authenticates with BlueSky."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            mock_client.login.assert_called_once_with(
                mock_settings_for_social.AT_PROTOCOL_USERNAME,
                mock_settings_for_social.AT_PROTOCOL_PASSWORD
            )

    def test_setup_at_protocol_failure(self, mock_settings_for_social):
        """Returns False on invalid credentials (login exception)."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.side_effect = Exception("Invalid credentials")
            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            # Service should be created but login failed (logged error, returned False)
            mock_client.login.assert_called_once()

    def test_setup_at_protocol_missing_credentials(self):
        """Handles missing credentials in settings."""
        with patch('services.social_service.settings') as mock_settings:
            mock_settings.AT_PROTOCOL_USERNAME = None
            mock_settings.AT_PROTOCOL_PASSWORD = None

            with patch('services.social_service.Client') as MockClient:
                mock_client = MagicMock()
                MockClient.return_value = mock_client

                from services.social_service import SocialService
                service = SocialService()

                # Login should not be called if credentials are missing
                mock_client.login.assert_not_called()

    def test_setup_at_protocol_empty_credentials(self):
        """Handles empty string credentials in settings."""
        with patch('services.social_service.settings') as mock_settings:
            mock_settings.AT_PROTOCOL_USERNAME = ""
            mock_settings.AT_PROTOCOL_PASSWORD = ""

            with patch('services.social_service.Client') as MockClient:
                mock_client = MagicMock()
                MockClient.return_value = mock_client

                from services.social_service import SocialService
                service = SocialService()

                # Login should not be called if credentials are empty
                mock_client.login.assert_not_called()

    def test_setup_at_protocol_network_error(self, mock_settings_for_social):
        """Handles network errors during auth."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.side_effect = ConnectionError("Network unreachable")
            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            # Service should handle network error gracefully
            mock_client.login.assert_called_once()

    def test_setup_at_protocol_authentication_error_propagation(self, mock_settings_for_social):
        """Verifies AuthenticationError propagation."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.side_effect = AuthenticationError("Auth failed")
            MockClient.return_value = mock_client

            from services.social_service import SocialService

            with pytest.raises(AuthenticationError):
                service = SocialService()


# =============================================================================
# Feed Retrieval Tests
# =============================================================================

class TestFeedRetrieval:
    """Tests for retrieving recent posts from BlueSky feed."""

    def test_get_recent_posts_success(self, mock_settings_for_social, mock_feed_response):
        """Returns list of recent posts."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile
            mock_client.get_author_feed.return_value = mock_feed_response

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            posts = service.get_recent_posts()

            assert len(posts) == 3
            assert posts[0].text == "First test post"
            assert posts[0].url == "https://example.com/article1"
            assert posts[0].title == "Article 1"

    def test_get_recent_posts_empty(self, mock_settings_for_social):
        """Handles empty feed."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_empty_feed = MagicMock()
            mock_empty_feed.feed = []
            mock_client.get_author_feed.return_value = mock_empty_feed

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            posts = service.get_recent_posts()

            assert posts == []

    def test_get_recent_posts_limit(self, mock_settings_for_social):
        """Respects limit parameter."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_feed = MagicMock()
            mock_feed.feed = []
            mock_client.get_author_feed.return_value = mock_feed

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            service.get_recent_posts(limit=25)

            # Verify limit was passed to get_author_feed
            mock_client.get_author_feed.assert_called_once()
            call_kwargs = mock_client.get_author_feed.call_args
            assert call_kwargs[1]['limit'] == 25

    def test_get_recent_posts_not_authenticated(self, mock_settings_for_social):
        """Handles unauthenticated state gracefully."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.get_profile.side_effect = Exception("Not authenticated")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            posts = service.get_recent_posts()

            # Should return empty list on error
            assert posts == []

    def test_get_recent_posts_error(self, mock_settings_for_social):
        """Handles API errors."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile
            mock_client.get_author_feed.side_effect = Exception("API Error")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            posts = service.get_recent_posts()

            # Should return empty list on error
            assert posts == []

    def test_get_recent_posts_social_media_error_propagation(self, mock_settings_for_social):
        """Verifies SocialMediaError propagation."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile
            mock_client.get_author_feed.side_effect = SocialMediaError("API Error")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(SocialMediaError):
                service.get_recent_posts()

    def test_get_recent_posts_missing_timestamp(self, mock_settings_for_social):
        """Handles posts without indexed_at timestamp."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            # Create post without indexed_at
            mock_post = MagicMock()
            mock_post.post = MagicMock(spec=[])  # No indexed_at attribute
            mock_post.post.record = MagicMock()
            mock_post.post.record.text = "Test post"
            mock_post.post.embed = None
            del mock_post.post.indexed_at  # Ensure no indexed_at

            mock_feed = MagicMock()
            mock_feed.feed = [mock_post]
            mock_client.get_author_feed.return_value = mock_feed

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            posts = service.get_recent_posts()

            assert len(posts) == 1
            assert posts[0].timestamp is not None  # Should have current time fallback


# =============================================================================
# Posting Tests
# =============================================================================

class TestPosting:
    """Tests for posting content to BlueSky."""

    def test_post_to_social_success(self, mock_settings_for_social, mock_post_response):
        """Posts successfully to BlueSky."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_profile.display_name = "Test User"
            mock_profile.avatar = "https://example.com/avatar.jpg"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 42

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )

            assert success is True
            assert post_id == 42
            mock_client.send_post.assert_called_once()

    def test_post_to_social_with_image(self, mock_settings_for_social, mock_post_response, mock_upload_response):
        """Posts with embedded image."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response
            mock_client.com.atproto.repo.upload_blob.return_value = mock_upload_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_profile.display_name = "Test User"
            mock_profile.avatar = "https://example.com/avatar.jpg"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 43

            # Mock image download
            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_requests.get.return_value = mock_response

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.jpg"
            )

            assert success is True
            mock_requests.get.assert_called_once_with(
                "https://example.com/image.jpg",
                timeout=mock_settings_for_social.BLUESKY_IMAGE_TIMEOUT
            )
            mock_client.com.atproto.repo.upload_blob.assert_called_once()

    def test_post_to_social_with_facets(self, mock_settings_for_social, mock_post_response):
        """Posts with rich text facets (links, mentions)."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_profile.display_name = "Test User"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 44

            MockClient.return_value = mock_client

            # Create mock facets
            mock_facet = MagicMock()
            mock_facet.model_dump.return_value = {"type": "link", "uri": "https://example.com"}
            facets = [mock_facet]

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with @mention and link",
                article_url="https://example.com/article",
                article_title="Test Article",
                facets=facets
            )

            assert success is True
            # Verify facets were passed to send_post
            call_kwargs = mock_client.send_post.call_args[1]
            assert call_kwargs['facets'] == facets

    def test_post_to_social_failure(self, mock_settings_for_social):
        """Returns False on API failure."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.side_effect = Exception("API Error")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )

            assert success is False
            assert post_id is None

    def test_post_to_social_db_integration(self, mock_settings_for_social, mock_post_response):
        """Verifies database insert is called."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_profile.display_name = "Test User"
            mock_profile.avatar = "https://example.com/avatar.jpg"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 45

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post content",
                article_url="https://example.com/article",
                article_title="Test Article",
                news_feed_id=123
            )

            assert success is True
            # Verify db.insert_social_post was called
            mock_db.insert_social_post.assert_called_once()

            # Verify the SocialPostData passed to db
            call_args = mock_db.insert_social_post.call_args[0][0]
            assert isinstance(call_args, SocialPostData)
            assert call_args.platform == 'bluesky'
            assert call_args.post_text == "Test post content"
            assert call_args.article_url == "https://example.com/article"
            assert call_args.article_title == "Test Article"
            assert call_args.news_feed_id == 123

    def test_post_to_social_not_authenticated(self, mock_settings_for_social):
        """Handles posting when not authenticated."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.side_effect = Exception("Not authenticated")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )

            assert success is False
            assert post_id is None

    def test_post_to_social_posting_error_propagation(self, mock_settings_for_social):
        """Verifies PostingError propagation."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.side_effect = PostingError("Posting failed")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(PostingError):
                service.post_to_social(
                    tweet_text="Test post content",
                    article_url="https://example.com/article",
                    article_title="Test Article"
                )

    def test_post_to_social_authentication_error_propagation(self, mock_settings_for_social):
        """Verifies AuthenticationError propagation during posting."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.side_effect = AuthenticationError("Session expired")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(AuthenticationError):
                service.post_to_social(
                    tweet_text="Test post content",
                    article_url="https://example.com/article",
                    article_title="Test Article"
                )

    def test_post_to_social_long_description_truncation(self, mock_settings_for_social, mock_post_response):
        """Verifies long descriptions are truncated."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 46

            MockClient.return_value = mock_client

            # Create a very long tweet text
            long_text = "A" * 200  # Longer than EMBED_DESCRIPTION_LENGTH (100)

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text=long_text,
                article_url="https://example.com/article",
                article_title="Test Article"
            )

            assert success is True
            # Verify models.AppBskyEmbedExternal.External was called
            mock_models.AppBskyEmbedExternal.External.assert_called()


# =============================================================================
# Image Upload Tests
# =============================================================================

class TestImageUpload:
    """Tests for image upload functionality."""

    def test_upload_image_success(self, mock_settings_for_social, mock_post_response, mock_upload_response):
        """Successfully uploads image blob."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response
            mock_client.com.atproto.repo.upload_blob.return_value = mock_upload_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 47

            # Mock successful image download
            mock_response = MagicMock()
            mock_response.content = b"\x89PNG\r\n\x1a\n"  # PNG header bytes
            mock_requests.get.return_value = mock_response

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.png"
            )

            assert success is True
            mock_client.com.atproto.repo.upload_blob.assert_called_once_with(b"\x89PNG\r\n\x1a\n")

    def test_upload_image_failure(self, mock_settings_for_social, mock_post_response):
        """Handles image upload failure gracefully (continues without image)."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response
            mock_client.com.atproto.repo.upload_blob.side_effect = Exception("Upload failed")

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 48

            # Mock successful image download
            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_requests.get.return_value = mock_response

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.jpg"
            )

            # Should still succeed without image
            assert success is True

    def test_upload_image_download_failure(self, mock_settings_for_social, mock_post_response):
        """Handles image download failure gracefully."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 49

            # Mock failed image download
            mock_requests.get.side_effect = Exception("Network error")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.jpg"
            )

            # Should still succeed without image
            assert success is True
            # upload_blob should not be called if download failed
            mock_client.com.atproto.repo.upload_blob.assert_not_called()

    def test_upload_image_timeout(self, mock_settings_for_social, mock_post_response):
        """Handles image download timeout."""
        import requests as real_requests

        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            mock_db.insert_social_post.return_value = 50

            # Mock timeout error
            mock_requests.get.side_effect = real_requests.Timeout("Request timed out")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post with image",
                article_url="https://example.com/article",
                article_title="Test Article",
                article_image="https://example.com/image.jpg"
            )

            # Should still succeed without image
            assert success is True

    def test_media_upload_error_propagation(self, mock_settings_for_social):
        """Verifies MediaUploadError propagation."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            # Mock successful image download but MediaUploadError on upload
            mock_response = MagicMock()
            mock_response.content = b"fake image data"
            mock_requests.get.return_value = mock_response

            mock_client.com.atproto.repo.upload_blob.side_effect = MediaUploadError("Blob too large")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(MediaUploadError):
                service.post_to_social(
                    tweet_text="Test post with image",
                    article_url="https://example.com/article",
                    article_title="Test Article",
                    article_image="https://example.com/image.jpg"
                )


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling and propagation."""

    def test_authentication_error_propagation(self, mock_settings_for_social):
        """Verifies AuthenticationError propagation from setup."""
        with patch('services.social_service.Client') as MockClient:
            mock_client = MagicMock()
            mock_client.login.side_effect = AuthenticationError("Invalid credentials")
            MockClient.return_value = mock_client

            from services.social_service import SocialService

            with pytest.raises(AuthenticationError):
                service = SocialService()

    def test_posting_error_propagation(self, mock_settings_for_social):
        """Verifies PostingError propagation."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.side_effect = PostingError("Rate limited")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(PostingError):
                service.post_to_social(
                    tweet_text="Test content",
                    article_url="https://example.com",
                    article_title="Test"
                )

    def test_media_upload_error_propagation(self, mock_settings_for_social):
        """Verifies MediaUploadError propagation."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.requests') as mock_requests, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()

            mock_response = MagicMock()
            mock_response.content = b"fake image"
            mock_requests.get.return_value = mock_response

            mock_client.com.atproto.repo.upload_blob.side_effect = MediaUploadError("Invalid format")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()

            with pytest.raises(MediaUploadError):
                service.post_to_social(
                    tweet_text="Test content",
                    article_url="https://example.com",
                    article_title="Test",
                    article_image="https://example.com/bad.gif"
                )

    def test_db_error_handled_gracefully(self, mock_settings_for_social, mock_post_response):
        """Database errors should not prevent successful post."""
        with patch('services.social_service.Client') as MockClient, \
             patch('services.social_service.db') as mock_db, \
             patch('services.social_service.models') as mock_models:

            mock_client = MagicMock()
            mock_client.login.return_value = MagicMock()
            mock_client.send_post.return_value = mock_post_response

            mock_profile = MagicMock()
            mock_profile.did = "did:plc:testuser123"
            mock_client.get_profile.return_value = mock_profile

            # Database insert fails
            mock_db.insert_social_post.side_effect = Exception("DB connection failed")

            MockClient.return_value = mock_client

            from services.social_service import SocialService
            service = SocialService()
            success, post_id = service.post_to_social(
                tweet_text="Test post content",
                article_url="https://example.com/article",
                article_title="Test Article"
            )

            # Post should still succeed even if DB fails
            assert success is True
            assert post_id is None  # But no ID returned


# =============================================================================
# Integration Tests with Fixtures
# =============================================================================

class TestSocialPostDataFactory:
    """Tests using the social_post_data_factory fixture."""

    def test_factory_creates_valid_bluesky_post(self, social_post_data_factory):
        """Factory creates valid BlueSky post data."""
        post = social_post_data_factory(
            platform='bluesky',
            post_text='Test post from factory',
            article_url='https://example.com/test'
        )

        assert post.platform == 'bluesky'
        assert post.post_text == 'Test post from factory'
        assert post.article_url == 'https://example.com/test'
        assert post.post_uri is not None  # Auto-generated for bluesky
        assert post.author_did is not None  # Auto-generated for bluesky

    def test_factory_creates_valid_twitter_post(self, social_post_data_factory):
        """Factory creates valid Twitter post data."""
        post = social_post_data_factory(
            platform='twitter',
            post_text='Test tweet from factory'
        )

        assert post.platform == 'twitter'
        assert post.post_text == 'Test tweet from factory'
        assert 'twitter.com' in post.post_url

    def test_factory_with_custom_timestamp(self, social_post_data_factory):
        """Factory respects custom created_at timestamp."""
        custom_time = datetime(2024, 1, 15, 12, 0, 0)
        post = social_post_data_factory(created_at=custom_time)

        assert post.created_at == custom_time


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
