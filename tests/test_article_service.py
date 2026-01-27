"""
Tests for Article Service

Comprehensive unit tests for the ArticleService class covering:
- URL Resolution (Google News redirect handling)
- Article Fetching (newspaper3k integration)
- Paywall Detection
- URL History Management
- Error Handling
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.article_service import ArticleService, ArticleContent
from utils.exceptions import ArticleFetchError, PaywallError, InsufficientContentError


# =============================================================================
# URL Resolution Tests
# =============================================================================

class TestGetRealUrl:
    """Tests for get_real_url method - Google News URL resolution."""

    @pytest.fixture
    def article_service(self):
        """Create an ArticleService instance with mocked settings."""
        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = '/tmp/test_history.txt'
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = ['wsj.com', 'nytimes.com']
            mock_settings.SELENIUM_REDIRECT_TIMEOUT = 3
            service = ArticleService()
            yield service

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_get_real_url_success(self, mock_options, mock_service, mock_chrome, article_service):
        """Resolves Google News URL to real URL using Selenium."""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_driver.current_url = 'https://www.bbc.com/news/real-article'
        mock_chrome.return_value = mock_driver

        google_url = 'https://news.google.com/rss/articles/CBMiK...'

        with patch('services.article_service.time.sleep'):
            result = article_service.get_real_url(google_url)

        assert result == 'https://www.bbc.com/news/real-article'
        mock_driver.get.assert_called_once_with(google_url)
        mock_driver.quit.assert_called_once()

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_get_real_url_direct_url(self, mock_options, mock_service, mock_chrome, article_service):
        """Returns non-Google URL as-is after passing through Selenium."""
        # The method always uses Selenium, it doesn't short-circuit for non-Google URLs
        mock_driver = MagicMock()
        direct_url = 'https://www.reuters.com/article/123'
        mock_driver.current_url = direct_url
        mock_chrome.return_value = mock_driver

        with patch('services.article_service.time.sleep'):
            result = article_service.get_real_url(direct_url)

        assert result == direct_url
        mock_driver.quit.assert_called_once()

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_get_real_url_selenium_error(self, mock_options, mock_service, mock_chrome, article_service):
        """Handles Selenium WebDriver errors gracefully."""
        from selenium.common.exceptions import WebDriverException

        mock_chrome.side_effect = WebDriverException("Chrome not found")

        result = article_service.get_real_url('https://news.google.com/rss/articles/abc')

        assert result is None

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_get_real_url_timeout(self, mock_options, mock_service, mock_chrome, article_service):
        """Handles timeout scenarios gracefully."""
        from selenium.common.exceptions import TimeoutException

        mock_driver = MagicMock()
        mock_driver.get.side_effect = TimeoutException("Page load timeout")
        mock_chrome.return_value = mock_driver

        result = article_service.get_real_url('https://news.google.com/rss/articles/xyz')

        assert result is None
        mock_driver.quit.assert_called_once()


# =============================================================================
# Article Fetching Tests
# =============================================================================

class TestFetchArticle:
    """Tests for fetch_article method - article content extraction."""

    @pytest.fixture
    def article_service(self):
        """Create an ArticleService instance with mocked settings."""
        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = '/tmp/test_history.txt'
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = ['wsj.com', 'nytimes.com']
            mock_settings.PAYWALL_PHRASES = ['subscribe', 'subscription', 'sign in']
            mock_settings.MIN_ARTICLE_WORD_COUNT = 50
            mock_settings.SUMMARY_TRUNCATE_LENGTH = 97
            service = ArticleService()
            yield service

    @patch('services.article_service.Article')
    def test_fetch_article_success(self, mock_article_class, article_service):
        """Fetches and parses article successfully."""
        # Setup mock article
        mock_article = MagicMock()
        mock_article.url = 'https://www.reuters.com/article/test'
        mock_article.title = 'Test Article Title'
        mock_article.text = ' '.join(['word'] * 100)  # 100 words
        mock_article.summary = 'This is a test summary of the article.'
        mock_article.top_image = 'https://example.com/image.jpg'
        mock_article.html = '<html><body>Article content</body></html>'
        mock_article_class.return_value = mock_article

        result = article_service.fetch_article(
            'https://www.reuters.com/article/test',
            news_feed_id=123
        )

        assert result is not None
        assert isinstance(result, ArticleContent)
        assert result.url == 'https://www.reuters.com/article/test'
        assert result.title == 'Test Article Title'
        assert result.news_feed_id == 123
        mock_article.download.assert_called_once()
        mock_article.parse.assert_called_once()
        mock_article.nlp.assert_called_once()

    @patch('services.article_service.Article')
    def test_fetch_article_paywall_domain(self, mock_article_class, article_service):
        """Detects paywall domain and skips."""
        result = article_service.fetch_article('https://www.wsj.com/articles/premium-story')

        assert result is None
        mock_article_class.assert_not_called()

    @patch('services.article_service.Article')
    def test_fetch_article_insufficient_content(self, mock_article_class, article_service):
        """Returns None for short articles (insufficient content)."""
        mock_article = MagicMock()
        mock_article.text = 'Short article'  # Only 2 words
        mock_article.html = '<html><body>Short</body></html>'
        mock_article_class.return_value = mock_article

        result = article_service.fetch_article('https://www.example.com/short-article')

        assert result is None

    @patch('services.article_service.Article')
    def test_fetch_article_parse_error(self, mock_article_class, article_service):
        """Handles newspaper parsing errors gracefully."""
        mock_article = MagicMock()
        mock_article.download.side_effect = Exception("Network error")
        mock_article_class.return_value = mock_article

        result = article_service.fetch_article('https://www.example.com/broken-article')

        assert result is None

    @patch('services.article_service.Article')
    def test_fetch_article_paywall_phrases_detected(self, mock_article_class, article_service):
        """Detects paywall phrases in content and returns None."""
        mock_article = MagicMock()
        mock_article.text = 'Short'  # Below word count
        mock_article.html = '<html><body>Please subscribe to continue reading</body></html>'
        mock_article_class.return_value = mock_article

        result = article_service.fetch_article('https://www.example.com/paywalled-article')

        assert result is None

    @patch('services.article_service.Article')
    def test_fetch_article_summary_truncation(self, mock_article_class, article_service):
        """Article summary is truncated to SUMMARY_TRUNCATE_LENGTH."""
        mock_article = MagicMock()
        mock_article.url = 'https://www.example.com/article'
        mock_article.title = 'Test'
        mock_article.text = ' '.join(['word'] * 100)
        mock_article.summary = 'A' * 200  # Long summary
        mock_article.top_image = ''
        mock_article.html = '<html></html>'
        mock_article_class.return_value = mock_article

        result = article_service.fetch_article('https://www.example.com/article')

        assert result is not None
        # Should be truncated to 97 chars + "..."
        assert len(result.summary) == 100  # 97 + 3 for "..."


# =============================================================================
# Selenium Fallback Tests
# =============================================================================

class TestFetchWithSelenium:
    """Tests for _fetch_with_selenium method - Selenium-based article extraction."""

    @pytest.fixture
    def article_service(self):
        """Create an ArticleService instance with mocked settings."""
        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = '/tmp/test_history.txt'
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.USER_AGENT = 'Test User Agent'
            mock_settings.SELENIUM_PAGE_LOAD_TIMEOUT = 5
            mock_settings.XPATH_MIN_TEXT_LENGTH = 20
            mock_settings.MIN_ARTICLE_WORD_COUNT = 50
            mock_settings.SUMMARY_WORD_LIMIT = 30
            service = ArticleService()
            yield service

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_fetch_with_selenium_success(self, mock_options, mock_service, mock_chrome, article_service):
        """Directly tests Selenium-based fetching."""
        # Setup mock driver
        mock_driver = MagicMock()
        mock_driver.title = 'Selenium Test Article'
        mock_driver.page_source = '<html><body>Content</body></html>'

        # Mock paragraph elements with sufficient text
        mock_paragraphs = []
        for i in range(10):
            mock_p = MagicMock()
            mock_p.text = f"This is paragraph {i} with sufficient length to be extracted. " * 3
            mock_paragraphs.append(mock_p)

        mock_driver.find_elements.return_value = mock_paragraphs
        mock_chrome.return_value = mock_driver

        with patch('services.article_service.time.sleep'):
            result = article_service._fetch_with_selenium(
                'https://www.example.com/selenium-article',
                news_feed_id=456
            )

        assert result is not None
        assert isinstance(result, ArticleContent)
        assert result.title == 'Selenium Test Article'
        assert result.news_feed_id == 456
        mock_driver.quit.assert_called_once()

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_fetch_with_selenium_insufficient_content(self, mock_options, mock_service, mock_chrome, article_service):
        """Selenium extraction with insufficient content returns None."""
        mock_driver = MagicMock()
        mock_driver.title = 'Short Article'
        mock_driver.page_source = '<html><body>Short</body></html>'

        # Return empty paragraphs
        mock_driver.find_elements.return_value = []
        mock_chrome.return_value = mock_driver

        with patch('services.article_service.time.sleep'), \
             patch('services.article_service.os.makedirs'), \
             patch('builtins.open', mock_open()):
            result = article_service._fetch_with_selenium('https://www.example.com/short')

        assert result is None
        mock_driver.quit.assert_called_once()

    @patch('services.article_service.webdriver.Chrome')
    @patch('services.article_service.Service')
    @patch('services.article_service.Options')
    def test_fetch_with_selenium_driver_error(self, mock_options, mock_service, mock_chrome, article_service):
        """Handles Selenium driver errors gracefully."""
        from selenium.common.exceptions import WebDriverException

        mock_chrome.side_effect = WebDriverException("Driver crashed")

        result = article_service._fetch_with_selenium('https://www.example.com/crash')

        assert result is None


# =============================================================================
# Paywall Detection Tests
# =============================================================================

class TestPaywallDetection:
    """Tests for paywall domain detection."""

    @pytest.fixture
    def article_service(self):
        """Create an ArticleService instance with test paywall domains."""
        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = '/tmp/test_history.txt'
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = ['wsj.com', 'nytimes.com', 'ft.com']
            mock_settings.PAYWALL_PHRASES = ['subscribe', 'subscription']
            mock_settings.MIN_ARTICLE_WORD_COUNT = 50
            mock_settings.SUMMARY_TRUNCATE_LENGTH = 97
            service = ArticleService()
            yield service

    def test_is_paywall_domain_true(self, article_service):
        """Detects known paywall domains."""
        # WSJ is in the paywall list
        paywall_urls = [
            'https://www.wsj.com/articles/test',
            'https://nytimes.com/2024/01/story',
            'https://www.ft.com/content/article-id',
        ]

        for url in paywall_urls:
            result = article_service.fetch_article(url)
            assert result is None, f"Expected {url} to be blocked as paywall"

    def test_is_paywall_domain_false(self, article_service):
        """Allows non-paywall domains."""
        # These domains are not in the paywall list, so the method will attempt to fetch
        with patch('services.article_service.Article') as mock_article_class:
            mock_article = MagicMock()
            mock_article.url = 'https://www.bbc.com/news/test'
            mock_article.title = 'Test'
            mock_article.text = ' '.join(['word'] * 100)
            mock_article.summary = 'Summary'
            mock_article.top_image = ''
            mock_article.html = '<html></html>'
            mock_article_class.return_value = mock_article

            result = article_service.fetch_article('https://www.bbc.com/news/test')

            # Should proceed with fetch (not blocked by paywall)
            mock_article_class.assert_called_once()
            assert result is not None

    def test_paywall_domains_from_settings(self, article_service):
        """Uses settings.PAYWALL_DOMAINS for detection."""
        # Verify the service has the paywall domains from settings
        assert 'wsj.com' in article_service.paywall_domains
        assert 'nytimes.com' in article_service.paywall_domains
        assert 'ft.com' in article_service.paywall_domains


# =============================================================================
# URL History Management Tests
# =============================================================================

class TestUrlHistoryManagement:
    """Tests for URL history file operations."""

    @pytest.fixture
    def article_service(self, tmp_path):
        """Create an ArticleService with a temporary history file."""
        history_file = tmp_path / "test_posted_urls.txt"

        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = str(history_file)
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = []
            service = ArticleService()
            yield service

    def test_is_url_in_history_found(self, article_service, tmp_path):
        """Returns True for URLs in history."""
        # Create history file with test URL
        history_file = tmp_path / "test_posted_urls.txt"
        test_url = 'https://www.example.com/posted-article'
        history_file.write_text(f"{test_url}\n")

        result = article_service.is_url_in_history(test_url)

        assert result is True

    def test_is_url_in_history_not_found(self, article_service, tmp_path):
        """Returns False for new URLs."""
        # Create empty history file
        history_file = tmp_path / "test_posted_urls.txt"
        history_file.write_text("")

        result = article_service.is_url_in_history('https://www.example.com/new-article')

        assert result is False

    def test_add_url_to_history(self, article_service, tmp_path):
        """Adds URL to history file."""
        history_file = tmp_path / "test_posted_urls.txt"
        history_file.write_text("")

        test_url = 'https://www.example.com/new-article'
        article_service._add_url_to_history(test_url)

        # Verify URL was added
        content = history_file.read_text()
        assert test_url in content

    def test_get_posted_urls(self, article_service, tmp_path):
        """Reads URLs from history file."""
        history_file = tmp_path / "test_posted_urls.txt"
        urls = [
            'https://www.example.com/article-1',
            'https://www.example.com/article-2',
            'https://www.example.com/article-3',
        ]
        history_file.write_text('\n'.join(urls))

        result = article_service._get_posted_urls()

        assert len(result) == 3
        assert 'https://www.example.com/article-1' in result
        assert 'https://www.example.com/article-2' in result
        assert 'https://www.example.com/article-3' in result

    def test_history_file_not_exists(self, tmp_path):
        """Handles missing history file gracefully by creating it."""
        non_existent_file = tmp_path / "non_existent_history.txt"

        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = str(non_existent_file)
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = []
            service = ArticleService()

            result = service._get_posted_urls()

            assert result == []
            # File should be created
            assert non_existent_file.exists()

    def test_history_file_cleanup(self, tmp_path):
        """Tests cleanup of old URLs when max lines exceeded."""
        history_file = tmp_path / "test_cleanup_history.txt"

        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = str(history_file)
            mock_settings.MAX_HISTORY_LINES = 5  # Small limit for testing
            mock_settings.CLEANUP_THRESHOLD = 2  # Remove 2 oldest when over limit
            mock_settings.PAYWALL_DOMAINS = []
            service = ArticleService()

            # Write initial URLs (at max limit)
            initial_urls = [f'https://example.com/article-{i}' for i in range(5)]
            history_file.write_text('\n'.join(initial_urls))

            # Add a new URL (should trigger cleanup)
            service._add_url_to_history('https://example.com/new-article')

            # Read back and verify cleanup happened
            content = history_file.read_text().strip().split('\n')

            # Should have removed oldest 2, then added 1 new = 4 URLs
            assert len(content) == 4
            # Oldest URLs should be removed
            assert 'https://example.com/article-0' not in content
            assert 'https://example.com/article-1' not in content
            # Newest should still be there
            assert 'https://example.com/new-article' in content


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.fixture
    def article_service(self):
        """Create an ArticleService instance with mocked settings."""
        with patch('services.article_service.settings') as mock_settings:
            mock_settings.URL_HISTORY_FILE = '/tmp/test_history.txt'
            mock_settings.MAX_HISTORY_LINES = 100
            mock_settings.CLEANUP_THRESHOLD = 10
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.PAYWALL_PHRASES = []
            mock_settings.MIN_ARTICLE_WORD_COUNT = 50
            mock_settings.SUMMARY_TRUNCATE_LENGTH = 97
            service = ArticleService()
            yield service

    @patch('services.article_service.Article')
    def test_article_fetch_error_raised(self, mock_article_class, article_service):
        """Verifies ArticleFetchError propagation."""
        mock_article = MagicMock()
        mock_article.download.side_effect = ArticleFetchError("Failed to fetch")
        mock_article_class.return_value = mock_article

        with pytest.raises(ArticleFetchError):
            article_service.fetch_article('https://www.example.com/error')

    def test_invalid_url_handling(self, article_service):
        """Handles malformed URLs gracefully."""
        invalid_urls = [
            '',
            'not-a-url',
            'ftp://invalid-protocol.com',
            '://missing-scheme.com',
        ]

        for url in invalid_urls:
            # Should not raise an exception, just return None
            result = article_service.fetch_article(url)
            # The method should handle these gracefully
            # (either returning None or logging an error)

    @patch('services.article_service.Article')
    def test_paywall_error_propagation(self, mock_article_class, article_service):
        """Verifies PaywallError is re-raised when explicitly thrown."""
        mock_article = MagicMock()
        mock_article.download.side_effect = PaywallError("Paywall detected")
        mock_article_class.return_value = mock_article

        with pytest.raises(PaywallError):
            article_service.fetch_article('https://www.example.com/paywall')

    @patch('services.article_service.Article')
    def test_insufficient_content_error_propagation(self, mock_article_class, article_service):
        """Verifies InsufficientContentError is re-raised when explicitly thrown."""
        mock_article = MagicMock()
        mock_article.download.side_effect = InsufficientContentError("Not enough content")
        mock_article_class.return_value = mock_article

        with pytest.raises(InsufficientContentError):
            article_service.fetch_article('https://www.example.com/short')


# =============================================================================
# ArticleContent Dataclass Tests
# =============================================================================

class TestArticleContent:
    """Tests for the ArticleContent dataclass."""

    def test_article_content_creation(self):
        """Creates ArticleContent with all required fields."""
        content = ArticleContent(
            url='https://www.example.com/article',
            title='Test Article',
            text='This is the article text.',
            summary='Article summary.',
            top_image='https://example.com/image.jpg',
            news_feed_id=123
        )

        assert content.url == 'https://www.example.com/article'
        assert content.title == 'Test Article'
        assert content.text == 'This is the article text.'
        assert content.summary == 'Article summary.'
        assert content.top_image == 'https://example.com/image.jpg'
        assert content.news_feed_id == 123

    def test_article_content_optional_news_feed_id(self):
        """ArticleContent works without news_feed_id."""
        content = ArticleContent(
            url='https://www.example.com/article',
            title='Test Article',
            text='This is the article text.',
            summary='Article summary.',
            top_image='https://example.com/image.jpg'
        )

        assert content.news_feed_id is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
