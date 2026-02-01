"""
Shared Test Fixtures for News Poster Application

This module provides common fixtures used across all test modules.
Fixtures include mocks for settings, database connections, logging,
HTTP responses, and data factories for test objects.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from typing import Optional, Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Settings Fixtures
# =============================================================================

@pytest.fixture
def mock_settings():
    """
    Mock the settings module with test configuration values.

    This fixture patches the config.settings module with safe test values,
    preventing tests from accessing real API keys or database credentials.

    Usage:
        def test_something(mock_settings):
            mock_settings.GOOGLE_AI_API_KEY = "custom-test-key"
            # ... test code

    Returns:
        MagicMock: A mock settings object with default test values.
    """
    with patch('config.settings') as mock_settings_module:
        # API Keys (use obvious test values)
        mock_settings_module.GOOGLE_AI_API_KEY = "test-google-api-key"
        mock_settings_module.AT_PROTOCOL_USERNAME = "test-bsky-user"
        mock_settings_module.AT_PROTOCOL_PASSWORD = "test-bsky-password"
        mock_settings_module.TWITTER_API_KEY = "test-twitter-api-key"
        mock_settings_module.TWITTER_API_KEY_SECRET = "test-twitter-api-secret"
        mock_settings_module.TWITTER_ACCESS_TOKEN = "test-twitter-access-token"
        mock_settings_module.TWITTER_ACCESS_TOKEN_SECRET = "test-twitter-access-secret"
        mock_settings_module.TWITTER_BEARER_TOKEN = "test-twitter-bearer"

        # Database Settings
        mock_settings_module.DB_SERVER = "test-server"
        mock_settings_module.DB_NAME = "test-db"
        mock_settings_module.DB_USER = "test-user"
        mock_settings_module.DB_PASSWORD = "test-password"
        mock_settings_module.DB_CONNECTION_STRING = "DRIVER={Test};SERVER=test-server;DATABASE=test-db;"

        # Application Settings
        mock_settings_module.APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        mock_settings_module.URL_HISTORY_FILE = "/tmp/test_posted_urls.txt"
        mock_settings_module.MAX_HISTORY_LINES = 100
        mock_settings_module.CLEANUP_THRESHOLD = 10
        mock_settings_module.MAX_ARTICLE_RETRIES = 30

        # AI Model Settings
        mock_settings_module.DEFAULT_AI_MODELS = ['gemini-2.0-flash', 'gemini-2.0-flash-lite']
        mock_settings_module.CANDIDATE_SELECTION_LIMIT = 60
        mock_settings_module.SIMILARITY_CHECK_POSTS_LIMIT = 72
        mock_settings_module.MIN_KEYWORD_LENGTH = 3
        mock_settings_module.TITLE_SIMILARITY_THRESHOLD = 0.5
        mock_settings_module.AI_COMPARISON_TEXT_LENGTH = 500

        # Content Processing Settings
        mock_settings_module.MIN_ARTICLE_WORD_COUNT = 50
        mock_settings_module.SUMMARY_TRUNCATE_LENGTH = 97
        mock_settings_module.SUMMARY_WORD_LIMIT = 30
        mock_settings_module.ARTICLE_TEXT_TRUNCATE_LENGTH = 4000
        mock_settings_module.TWEET_CHARACTER_LIMIT = 260

        # Selenium Settings
        mock_settings_module.SELENIUM_REDIRECT_TIMEOUT = 3
        mock_settings_module.SELENIUM_PAGE_LOAD_TIMEOUT = 5
        mock_settings_module.XPATH_MIN_TEXT_LENGTH = 20

        # Platform Enable/Disable Settings
        mock_settings_module.ENABLE_BLUESKY = True
        mock_settings_module.ENABLE_TWITTER = True

        # Social Media Platform Settings
        mock_settings_module.DEFAULT_PLATFORMS = ["bluesky", "twitter"]
        mock_settings_module.BLUESKY_FETCH_LIMIT = 80
        mock_settings_module.BLUESKY_IMAGE_TIMEOUT = 10
        mock_settings_module.EMBED_DESCRIPTION_LENGTH = 100
        mock_settings_module.TWITTER_FETCH_LIMIT = 50
        mock_settings_module.TWITTER_API_MAX_RESULTS = 100
        mock_settings_module.TWITTER_URL_LENGTH = 23
        mock_settings_module.TWITTER_CHARACTER_LIMIT = 280
        mock_settings_module.TWEET_TRUNCATION_PADDING = 4
        mock_settings_module.TWITTER_IMAGE_TIMEOUT = 10

        # Database Query Settings
        mock_settings_module.DB_TOTAL_NEWS_FEED_RESULTS = 160
        mock_settings_module.DB_CAT1_ALLOCATION = 0.5
        mock_settings_module.DB_CAT2_ALLOCATION = 0.4

        # Web Scraping Settings
        mock_settings_module.USER_AGENT = 'Test User Agent'
        mock_settings_module.REQUEST_HEADERS = {'User-Agent': 'Test User Agent'}
        mock_settings_module.PAYWALL_PHRASES = ["subscribe", "subscription"]
        mock_settings_module.PAYWALL_DOMAINS = ["wsj.com", "nytimes.com"]
        mock_settings_module.BLOCKED_DOMAINS = ["infowars.com", "breitbart.com"]
        mock_settings_module.PR_TITLE_PATTERNS = [r"^statement\s+(regarding|on|about)"]

        yield mock_settings_module


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture
def mock_db_connection():
    """
    Mock pyodbc database connection and cursor.

    This fixture provides a mock database connection that simulates
    pyodbc behavior without requiring an actual database connection.

    Usage:
        def test_database(mock_db_connection):
            conn, cursor = mock_db_connection
            cursor.fetchall.return_value = [('row1',), ('row2',)]
            # ... test code

    Returns:
        tuple: A tuple of (mock_connection, mock_cursor).
    """
    mock_cursor = MagicMock()
    mock_cursor.description = [('column1',), ('column2',)]
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_cursor.rowcount = 0

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    mock_conn.close.return_value = None

    with patch('pyodbc.connect', return_value=mock_conn):
        yield mock_conn, mock_cursor


@pytest.fixture
def mock_db_with_data(mock_db_connection):
    """
    Mock database connection with sample data pre-configured.

    Extends mock_db_connection with common test data patterns.

    Returns:
        tuple: A tuple of (mock_connection, mock_cursor) with sample data.
    """
    mock_conn, mock_cursor = mock_db_connection

    # Sample news feed data
    mock_cursor.fetchall.return_value = [
        {
            'News_Feed_ID': 1,
            'Title': 'Test Article 1',
            'URL': 'https://example.com/article-1',
            'Category_ID': 1,
            'Source_Count': 3
        },
        {
            'News_Feed_ID': 2,
            'Title': 'Test Article 2',
            'URL': 'https://example.com/article-2',
            'Category_ID': 2,
            'Source_Count': 1
        }
    ]

    return mock_conn, mock_cursor


# =============================================================================
# Logging Fixtures
# =============================================================================

@pytest.fixture
def mock_logger():
    """
    Suppress logging output during tests.

    This fixture patches the logging module to prevent log output
    from cluttering test results while still allowing log calls
    to be inspected.

    Usage:
        def test_with_logging(mock_logger):
            # Logs are suppressed but can be inspected
            mock_logger.info.assert_called_with("expected message")

    Returns:
        MagicMock: A mock logger object that captures all log calls.
    """
    mock_log = MagicMock()

    with patch('logging.getLogger') as mock_get_logger:
        mock_get_logger.return_value = mock_log
        yield mock_log


@pytest.fixture
def capture_logs():
    """
    Capture log messages for assertion in tests.

    Unlike mock_logger which completely mocks logging, this fixture
    captures actual log records for inspection.

    Returns:
        list: A list that will contain captured log records.
    """
    import logging

    class LogCapture(logging.Handler):
        def __init__(self):
            super().__init__()
            self.records = []

        def emit(self, record):
            self.records.append(record)

    handler = LogCapture()
    handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    original_level = root_logger.level
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    yield handler.records

    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


# =============================================================================
# HTTP Response Fixtures
# =============================================================================

@pytest.fixture
def mock_http_response():
    """
    Factory fixture for creating mock HTTP responses.

    This fixture returns a factory function that creates mock response
    objects with configurable status codes, content, and headers.

    Usage:
        def test_http_request(mock_http_response):
            response = mock_http_response(
                status_code=200,
                json_data={'key': 'value'},
                headers={'Content-Type': 'application/json'}
            )
            # ... test code

    Returns:
        callable: A factory function for creating mock responses.
    """
    def _create_response(
        status_code: int = 200,
        content: bytes = b'',
        text: str = '',
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        url: str = 'https://example.com',
        raise_for_status: bool = False
    ) -> MagicMock:
        """
        Create a mock HTTP response object.

        Args:
            status_code: HTTP status code (default 200).
            content: Raw bytes content.
            text: Text content (will be auto-generated from json_data if not provided).
            json_data: Dictionary to return from response.json().
            headers: Response headers dictionary.
            url: The URL of the response.
            raise_for_status: If True, raise_for_status() will raise an exception.

        Returns:
            MagicMock: A mock response object mimicking requests.Response.
        """
        import json

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.content = content
        mock_response.url = url
        mock_response.headers = headers or {'Content-Type': 'text/html'}
        mock_response.ok = 200 <= status_code < 300

        # Set text content
        if text:
            mock_response.text = text
        elif json_data:
            mock_response.text = json.dumps(json_data)
        else:
            mock_response.text = content.decode('utf-8') if content else ''

        # Configure json() method
        if json_data is not None:
            mock_response.json.return_value = json_data
        else:
            mock_response.json.side_effect = ValueError("No JSON data")

        # Configure raise_for_status
        if raise_for_status or status_code >= 400:
            from requests.exceptions import HTTPError
            mock_response.raise_for_status.side_effect = HTTPError(
                f"{status_code} Error",
                response=mock_response
            )
        else:
            mock_response.raise_for_status.return_value = None

        return mock_response

    return _create_response


@pytest.fixture
def mock_requests(mock_http_response):
    """
    Mock the requests library for HTTP testing.

    Usage:
        def test_api_call(mock_requests):
            mock_requests.get.return_value = mock_requests.response(
                json_data={'status': 'ok'}
            )
            # ... test code

    Returns:
        MagicMock: A mock requests module with response factory attached.
    """
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('requests.put') as mock_put, \
         patch('requests.delete') as mock_delete:

        mock_req = MagicMock()
        mock_req.get = mock_get
        mock_req.post = mock_post
        mock_req.put = mock_put
        mock_req.delete = mock_delete
        mock_req.response = mock_http_response

        yield mock_req


# =============================================================================
# Data Model Factories
# =============================================================================

@pytest.fixture
def social_post_data_factory():
    """
    Factory fixture for creating SocialPostData test objects.

    This fixture returns a factory function that creates SocialPostData
    instances with configurable fields and sensible defaults.

    Usage:
        def test_social_post(social_post_data_factory):
            post = social_post_data_factory(
                platform='bluesky',
                post_text='Test post content'
            )
            # ... test code

    Returns:
        callable: A factory function for creating SocialPostData objects.
    """
    from data.database import SocialPostData

    def _create_social_post(
        platform: str = 'bluesky',
        post_id: str = 'test-post-id-123',
        post_text: str = 'Test post content for unit testing.',
        author_handle: str = '@testuser',
        created_at: Optional[datetime] = None,
        post_uri: Optional[str] = None,
        post_url: Optional[str] = None,
        author_display_name: Optional[str] = 'Test User',
        author_avatar_url: Optional[str] = None,
        author_did: Optional[str] = None,
        post_facets: Optional[str] = None,
        article_url: Optional[str] = 'https://example.com/article',
        article_title: Optional[str] = 'Test Article Title',
        article_description: Optional[str] = 'Test article description.',
        article_image_url: Optional[str] = None,
        article_image_blob: Optional[str] = None,
        news_feed_id: Optional[int] = 1,
        raw_response: Optional[str] = None,
        **kwargs
    ) -> SocialPostData:
        """
        Create a SocialPostData instance for testing.

        Args:
            platform: Social media platform ('bluesky' or 'twitter').
            post_id: Unique post identifier.
            post_text: The text content of the post.
            author_handle: Author's handle (e.g., @username).
            created_at: Post creation timestamp (defaults to now).
            post_uri: Full URI for the post (BlueSky at:// URIs).
            post_url: Direct web URL to the post.
            author_display_name: Author's display name.
            author_avatar_url: URL to author's avatar image.
            author_did: BlueSky DID identifier.
            post_facets: JSON string of facets.
            article_url: URL of the linked article.
            article_title: Title of the linked article.
            article_description: Description of the linked article.
            article_image_url: URL of the article's image.
            article_image_blob: Blob data for article image.
            news_feed_id: Database ID of the news feed item.
            raw_response: JSON string of full API response.
            **kwargs: Additional fields (ignored, for forward compatibility).

        Returns:
            SocialPostData: A configured SocialPostData instance.
        """
        if created_at is None:
            created_at = datetime.now()

        if post_uri is None and platform == 'bluesky':
            post_uri = f'at://did:plc:test/{post_id}'

        if post_url is None:
            if platform == 'bluesky':
                post_url = f'https://bsky.app/profile/testuser/post/{post_id}'
            else:
                post_url = f'https://twitter.com/testuser/status/{post_id}'

        if author_did is None and platform == 'bluesky':
            author_did = 'did:plc:testuser123'

        return SocialPostData(
            platform=platform,
            post_id=post_id,
            post_text=post_text,
            author_handle=author_handle,
            created_at=created_at,
            post_uri=post_uri,
            post_url=post_url,
            author_display_name=author_display_name,
            author_avatar_url=author_avatar_url,
            author_did=author_did,
            post_facets=post_facets,
            article_url=article_url,
            article_title=article_title,
            article_description=article_description,
            article_image_url=article_image_url,
            article_image_blob=article_image_blob,
            news_feed_id=news_feed_id,
            raw_response=raw_response
        )

    return _create_social_post


@pytest.fixture
def candidate_article_factory():
    """
    Factory fixture for creating candidate article dictionaries.

    Creates article dictionaries in the format used by the AI service
    for candidate selection.

    Usage:
        def test_article_selection(candidate_article_factory):
            article = candidate_article_factory(
                id=1,
                source_count=5,
                title='Breaking News'
            )
            # ... test code

    Returns:
        callable: A factory function for creating article dictionaries.
    """
    def _create_candidate(
        id: int = 1,
        source_count: int = 1,
        title: Optional[str] = None,
        url: Optional[str] = None,
        category_id: int = 1
    ) -> Dict[str, Any]:
        """
        Create a candidate article dictionary for testing.

        Args:
            id: News feed ID.
            source_count: Number of sources reporting this story.
            title: Article title (auto-generated if not provided).
            url: Article URL (auto-generated if not provided).
            category_id: Category ID (1=World, 2=National, 3=Business).

        Returns:
            dict: A candidate article dictionary.
        """
        return {
            'News_Feed_ID': id,
            'Title': title or f'Test Article {id}',
            'URL': url or f'https://example.com/article-{id}',
            'Source_Count': source_count,
            'Category_ID': category_id
        }

    return _create_candidate


# =============================================================================
# AI Service Fixtures
# =============================================================================

@pytest.fixture
def mock_genai():
    """
    Mock the Google Generative AI library.

    This fixture patches the google.genai module to prevent
    actual API calls during testing.

    Returns:
        MagicMock: A mock genai module.
    """
    with patch('google.genai') as mock_genai_module:
        # Mock the Client
        mock_client = MagicMock()
        mock_genai_module.Client.return_value = mock_client

        # Mock the model list
        mock_model = MagicMock()
        mock_model.name = 'models/gemini-2.0-flash'
        mock_client.models.list.return_value = [mock_model]

        # Mock the generate_content response
        mock_response = MagicMock()
        mock_response.text = "Generated test content"
        mock_client.models.generate_content.return_value = mock_response

        yield mock_genai_module


# =============================================================================
# File System Fixtures
# =============================================================================

@pytest.fixture
def temp_url_history(tmp_path):
    """
    Create a temporary URL history file for testing.

    Returns:
        pathlib.Path: Path to the temporary history file.
    """
    history_file = tmp_path / "posted_urls.txt"
    history_file.write_text("")
    return history_file


@pytest.fixture
def temp_url_history_with_data(tmp_path):
    """
    Create a temporary URL history file with sample data.

    Returns:
        pathlib.Path: Path to the temporary history file with data.
    """
    history_file = tmp_path / "posted_urls.txt"
    sample_urls = [
        "https://example.com/old-article-1",
        "https://example.com/old-article-2",
        "https://example.com/old-article-3",
    ]
    history_file.write_text("\n".join(sample_urls))
    return history_file


# =============================================================================
# Dependency Injection Fixtures
# =============================================================================

class MockPostStorage:
    """Mock implementation of PostStorage protocol for testing.

    This class implements the PostStorage protocol interface, allowing
    services to be tested without real database connections.

    Usage:
        def test_with_di(mock_post_storage):
            service = SocialService(post_storage=mock_post_storage)
            # ... test code
            assert mock_post_storage.insert_called
    """

    def __init__(self):
        """Initialize the mock storage with empty tracking lists."""
        self.posts = []
        self.insert_calls = []
        self.get_calls = []
        self._next_id = 1

    def insert_social_post(self, post_data) -> Optional[int]:
        """Mock insert that tracks calls and returns incrementing IDs.

        Args:
            post_data: SocialPostData object to insert.

        Returns:
            int: Mock post ID.
        """
        self.insert_calls.append(post_data)
        self.posts.append({'id': self._next_id, 'data': post_data})
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def get_social_post_by_id(self, social_post_id: int) -> Optional[Dict]:
        """Mock get by ID.

        Args:
            social_post_id: ID to look up.

        Returns:
            dict or None: Mock post data if found.
        """
        self.get_calls.append(('by_id', social_post_id))
        for post in self.posts:
            if post['id'] == social_post_id:
                return {'Social_Post_ID': post['id'], **vars(post['data'])}
        return None

    def get_recent_social_posts(
        self,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> Optional[List[Dict]]:
        """Mock get recent posts.

        Args:
            platform: Optional platform filter.
            limit: Maximum number of posts.

        Returns:
            list: Mock post data list.
        """
        self.get_calls.append(('recent', platform, limit))
        results = []
        for post in self.posts[-limit:]:
            if platform is None or post['data'].platform == platform:
                results.append({'Social_Post_ID': post['id'], **vars(post['data'])})
        return results

    @property
    def insert_called(self) -> bool:
        """Check if insert was called."""
        return len(self.insert_calls) > 0

    def reset(self):
        """Reset all tracking data."""
        self.posts.clear()
        self.insert_calls.clear()
        self.get_calls.clear()
        self._next_id = 1


@pytest.fixture
def mock_post_storage():
    """
    Provide a mock PostStorage implementation for DI testing.

    This fixture creates a MockPostStorage instance that implements
    the PostStorage protocol, enabling services to be tested without
    a real database connection.

    Usage:
        def test_service_with_di(mock_post_storage):
            service = SocialService(post_storage=mock_post_storage)
            service.post_to_social("text", "url", "title")
            assert mock_post_storage.insert_called

    Returns:
        MockPostStorage: A mock storage implementation.
    """
    return MockPostStorage()


@pytest.fixture
def article_service_with_di(tmp_path):
    """
    Create an ArticleService with DI configuration for testing.

    This fixture creates an ArticleService instance with:
    - A temporary URL history file
    - Custom configuration values for testing

    Usage:
        def test_article_service(article_service_with_di):
            service, history_file = article_service_with_di
            # ... test code

    Returns:
        tuple: (ArticleService instance, path to history file)
    """
    from services.article_service import ArticleService

    history_file = tmp_path / "test_history.txt"
    history_file.write_text("")

    service = ArticleService(
        url_history_file=str(history_file),
        max_history_lines=50,
        cleanup_threshold=5,
        paywall_domains=["test-paywall.com"]
    )

    return service, history_file


@pytest.fixture
def mock_social_service(mock_post_storage):
    """
    Create a mocked SocialService for DI testing.

    This fixture provides a SocialService with:
    - A mock AT Protocol client (no real authentication)
    - Mock post storage

    Note: The service is not fully initialized (no login),
    suitable for testing posting logic in isolation.

    Returns:
        tuple: (SocialService instance, mock AT client, mock post storage)
    """
    from services.social_service import SocialService

    mock_client = MagicMock()
    mock_client.login.return_value = True

    # Create service with injected dependencies
    service = SocialService(
        at_client=mock_client,
        username="test-user",
        password="test-password",
        post_storage=mock_post_storage
    )

    return service, mock_client, mock_post_storage


@pytest.fixture
def mock_twitter_service(mock_post_storage):
    """
    Create a mocked TwitterService for DI testing.

    This fixture provides a TwitterService with:
    - A mock Tweepy client (no real authentication)
    - Mock post storage

    Returns:
        tuple: (TwitterService instance, mock client, mock post storage)
    """
    from services.twitter_service import TwitterService

    mock_client = MagicMock()

    # Create service with injected dependencies
    service = TwitterService(
        api_key="test-api-key",
        api_key_secret="test-api-secret",
        access_token="test-access-token",
        access_token_secret="test-access-secret",
        post_storage=mock_post_storage,
        client=mock_client
    )

    return service, mock_client, mock_post_storage
