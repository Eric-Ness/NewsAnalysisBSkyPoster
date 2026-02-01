"""
Tests for NewsPoster Main Application

Tests cover initialization, platform configuration, service integration,
and the main workflow orchestration.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import NewsPoster, create_news_poster
from services.article_service import ArticleService, ArticleContent
from services.ai_service import AIService
from services.social_service import SocialService
from services.twitter_service import TwitterService


# =============================================================================
# Initialization Tests
# =============================================================================

class TestNewsPosterInitialization:
    """Tests for NewsPoster initialization."""

    def test_init_with_defaults(self):
        """NewsPoster initializes with default services when ENABLE_TWITTER is True."""
        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = True
            mock_settings.ENABLE_BLUESKY = True

            with patch('main.ArticleService') as mock_article_cls, \
                 patch('main.AIService') as mock_ai_cls, \
                 patch('main.SocialService') as mock_social_cls, \
                 patch('main.TwitterService') as mock_twitter_cls:

                poster = NewsPoster(validate=False)

                # Verify all services were created
                mock_article_cls.assert_called_once()
                mock_ai_cls.assert_called_once()
                mock_social_cls.assert_called_once()
                mock_twitter_cls.assert_called_once()

    def test_init_twitter_disabled(self):
        """NewsPoster doesn't initialize Twitter service when ENABLE_TWITTER is False."""
        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = False
            mock_settings.ENABLE_BLUESKY = True

            with patch('main.ArticleService') as mock_article_cls, \
                 patch('main.AIService') as mock_ai_cls, \
                 patch('main.SocialService') as mock_social_cls, \
                 patch('main.TwitterService') as mock_twitter_cls:

                poster = NewsPoster(validate=False)

                # Verify Twitter service was NOT created
                mock_twitter_cls.assert_not_called()
                assert poster.twitter_service is None

    def test_init_with_injected_services(self):
        """NewsPoster accepts injected services."""
        mock_article_service = MagicMock(spec=ArticleService)
        mock_ai_service = MagicMock(spec=AIService)
        mock_social_service = MagicMock(spec=SocialService)
        mock_twitter_service = MagicMock(spec=TwitterService)

        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = True

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=mock_twitter_service,
                validate=False
            )

            assert poster.article_service is mock_article_service
            assert poster.ai_service is mock_ai_service
            assert poster.social_service is mock_social_service
            assert poster.twitter_service is mock_twitter_service

    def test_init_twitter_service_provided_when_disabled(self):
        """NewsPoster uses provided Twitter service even when ENABLE_TWITTER is False."""
        mock_twitter_service = MagicMock(spec=TwitterService)

        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = False

            poster = NewsPoster(
                twitter_service=mock_twitter_service,
                validate=False
            )

            assert poster.twitter_service is mock_twitter_service


# =============================================================================
# Platform Configuration Tests
# =============================================================================

class TestPlatformConfiguration:
    """Tests for platform enable/disable functionality."""

    def test_run_with_both_platforms_enabled(self):
        """Run proceeds with both platforms when both are enabled."""
        with patch('main.settings') as mock_settings, \
             patch('main.db') as mock_db:

            mock_settings.ENABLE_TWITTER = True
            mock_settings.ENABLE_BLUESKY = True
            mock_settings.DEFAULT_PLATFORMS = ["bluesky", "twitter"]
            mock_settings.MAX_ARTICLE_RETRIES = 5
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.BLOCKED_DOMAINS = []

            # Mock database to return no news feed
            mock_db.get_news_feed.return_value = None

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)
            mock_twitter_service = MagicMock(spec=TwitterService)

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=mock_twitter_service,
                validate=False
            )

            result = poster.run(test_mode=False)

            # Should return False because no news feed data
            assert result is False

    def test_run_with_twitter_disabled(self):
        """Run removes Twitter from platforms when service is None."""
        with patch('main.settings') as mock_settings, \
             patch('main.db') as mock_db:

            mock_settings.ENABLE_TWITTER = False
            mock_settings.ENABLE_BLUESKY = True
            mock_settings.DEFAULT_PLATFORMS = ["bluesky", "twitter"]
            mock_settings.MAX_ARTICLE_RETRIES = 5
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.BLOCKED_DOMAINS = []

            # Mock database to return no news feed
            mock_db.get_news_feed.return_value = None

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=None,  # Twitter service is None
                validate=False
            )

            # Mock logger to capture log messages
            with patch('main.logger') as mock_logger:
                result = poster.run(test_mode=False)

                # Verify Twitter removal was logged
                mock_logger.info.assert_any_call(
                    "Twitter is in platforms list but Twitter service is disabled, removing from platforms"
                )

    def test_run_with_no_platforms_available(self):
        """Run returns False when no platforms are available."""
        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = False
            mock_settings.ENABLE_BLUESKY = False
            mock_settings.DEFAULT_PLATFORMS = []

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=None,
                validate=False
            )

            with patch('main.logger') as mock_logger:
                result = poster.run(test_mode=False)

                assert result is False
                mock_logger.error.assert_called_with(
                    "No platforms available for posting. Check your platform configuration."
                )

    def test_run_logs_enabled_platforms(self):
        """Run logs which platforms are enabled at startup."""
        with patch('main.settings') as mock_settings, \
             patch('main.db') as mock_db:

            mock_settings.ENABLE_TWITTER = True
            mock_settings.ENABLE_BLUESKY = True
            mock_settings.DEFAULT_PLATFORMS = ["bluesky", "twitter"]
            mock_settings.MAX_ARTICLE_RETRIES = 5
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.BLOCKED_DOMAINS = []

            # Mock database to return no news feed
            mock_db.get_news_feed.return_value = None

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)
            mock_twitter_service = MagicMock(spec=TwitterService)

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=mock_twitter_service,
                validate=False
            )

            with patch('main.logger') as mock_logger:
                result = poster.run(test_mode=False)

                # Verify enabled platforms were logged
                mock_logger.info.assert_any_call(
                    "Enabled platforms for this run: bluesky, twitter"
                )

    def test_run_only_fetches_from_enabled_platforms(self):
        """Run only fetches recent posts from enabled platforms."""
        import pandas as pd

        with patch('main.settings') as mock_settings, \
             patch('main.db') as mock_db, \
             patch('main.is_domain_match') as mock_domain_match:

            mock_settings.ENABLE_TWITTER = False
            mock_settings.ENABLE_BLUESKY = True
            mock_settings.DEFAULT_PLATFORMS = ["bluesky"]
            mock_settings.MAX_ARTICLE_RETRIES = 5
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.BLOCKED_DOMAINS = []

            # Mock domain matching to return False (no paywalls)
            mock_domain_match.return_value = False

            # Mock database to return sample news feed
            news_data = pd.DataFrame([
                {
                    'URL': 'https://example.com/article1',
                    'Title': 'Test Article 1',
                    'News_Feed_ID': 1,
                    'Source_Count': 3
                }
            ])
            mock_db.get_news_feed.return_value = news_data

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)

            # Mock AI service to return no articles
            mock_ai_service.select_news_articles.return_value = []

            # Mock social service to return posts
            mock_social_service.get_recent_posts.return_value = [
                MagicMock(text="Old post", url=None)
            ]

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=None,  # Twitter disabled
                validate=False
            )

            result = poster.run(test_mode=False)

            # Verify only BlueSky posts were fetched
            mock_social_service.get_recent_posts.assert_called_once()

    def test_run_only_posts_to_enabled_platforms(self):
        """Run only posts to enabled platforms."""
        import pandas as pd

        with patch('main.settings') as mock_settings, \
             patch('main.db') as mock_db, \
             patch('main.is_domain_match') as mock_domain_match, \
             patch('main.extract_base_domain') as mock_extract_domain:

            mock_settings.ENABLE_TWITTER = False
            mock_settings.ENABLE_BLUESKY = True
            mock_settings.DEFAULT_PLATFORMS = ["bluesky"]
            mock_settings.MAX_ARTICLE_RETRIES = 5
            mock_settings.PAYWALL_DOMAINS = []
            mock_settings.BLOCKED_DOMAINS = []

            # Mock domain matching and extraction
            mock_domain_match.return_value = False
            mock_extract_domain.return_value = "example.com"

            # Mock database to return sample news feed
            news_data = pd.DataFrame([
                {
                    'URL': 'https://example.com/article1',
                    'Title': 'Test Article 1',
                    'News_Feed_ID': 1,
                    'Source_Count': 3
                }
            ])
            mock_db.get_news_feed.return_value = news_data

            mock_article_service = MagicMock(spec=ArticleService)
            mock_ai_service = MagicMock(spec=AIService)
            mock_social_service = MagicMock(spec=SocialService)

            # Mock services to return successful data
            mock_ai_service.select_news_articles.return_value = [
                {
                    'URL': 'https://example.com/article1',
                    'Title': 'Test Article 1',
                    'News_Feed_ID': 1,
                    'Source_Count': 3
                }
            ]
            mock_article_service.is_url_in_history.return_value = False
            mock_article_service.fetch_article.return_value = ArticleContent(
                url='https://example.com/article1',
                title='Test Article 1',
                text='Article content',
                top_image=None,
                summary='Summary',
                news_feed_id=1
            )
            mock_ai_service.check_content_similarity.return_value = False
            mock_ai_service.generate_tweet.return_value = {
                'tweet_text': 'Test tweet'
            }
            mock_social_service.post_to_social.return_value = (True, 42)
            mock_social_service.get_recent_posts.return_value = []

            poster = NewsPoster(
                article_service=mock_article_service,
                ai_service=mock_ai_service,
                social_service=mock_social_service,
                twitter_service=None,  # Twitter disabled
                validate=False
            )

            result = poster.run(test_mode=False)

            # Verify only BlueSky post was made
            mock_social_service.post_to_social.assert_called_once()


# =============================================================================
# Factory Function Tests
# =============================================================================

class TestCreateNewsPoster:
    """Tests for create_news_poster factory function."""

    def test_create_news_poster_with_defaults(self):
        """create_news_poster creates NewsPoster with defaults."""
        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = True

            with patch('main.ArticleService') as mock_article_cls, \
                 patch('main.AIService') as mock_ai_cls, \
                 patch('main.SocialService') as mock_social_cls, \
                 patch('main.TwitterService') as mock_twitter_cls, \
                 patch('main.NewsPoster') as mock_poster_cls:

                poster = create_news_poster()

                mock_poster_cls.assert_called_once()

    def test_create_news_poster_with_custom_services(self):
        """create_news_poster accepts custom services."""
        mock_article_service = MagicMock(spec=ArticleService)
        mock_ai_service = MagicMock(spec=AIService)

        with patch('main.settings') as mock_settings:
            mock_settings.ENABLE_TWITTER = True

            with patch('main.NewsPoster') as mock_poster_cls:
                poster = create_news_poster(
                    article_service=mock_article_service,
                    ai_service=mock_ai_service
                )

                mock_poster_cls.assert_called_once_with(
                    article_service=mock_article_service,
                    ai_service=mock_ai_service,
                    social_service=None,
                    twitter_service=None,
                    validate=True
                )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
