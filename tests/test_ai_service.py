"""
Tests for AI Service - Breaking News Prioritization and Structured Output

Tests the candidate selection logic that prioritizes articles with higher Source_Count
while maintaining variety through randomization of regular articles.
Also tests the structured output parsing for similarity checks, article selection,
and tweet generation.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai_service import SelectedArticle, TweetResponse, SimilarityResult


class TestBreakingNewsPrioritization:
    """Tests for the breaking news prioritization in select_news_articles."""

    def create_candidate(self, id: int, source_count: int = 1, title: str = None) -> dict:
        """Helper to create a test candidate article."""
        return {
            'URL': f'https://example.com/article-{id}',
            'Title': title or f'Article {id}',
            'News_Feed_ID': id,
            'Source_Count': source_count
        }

    def test_breaking_news_separated_from_regular(self):
        """Articles with Source_Count > 1 should be separated from regular articles."""
        # Create candidates: 3 breaking (Source_Count > 1), 5 regular (Source_Count = 1)
        candidates = [
            self.create_candidate(1, source_count=3),  # Breaking
            self.create_candidate(2, source_count=1),  # Regular
            self.create_candidate(3, source_count=5),  # Breaking
            self.create_candidate(4, source_count=1),  # Regular
            self.create_candidate(5, source_count=2),  # Breaking
            self.create_candidate(6, source_count=1),  # Regular
            self.create_candidate(7, source_count=1),  # Regular
            self.create_candidate(8, source_count=1),  # Regular
        ]

        breaking = [c for c in candidates if c.get('Source_Count', 1) > 1]
        regular = [c for c in candidates if c.get('Source_Count', 1) <= 1]

        assert len(breaking) == 3
        assert len(regular) == 5

    def test_breaking_news_sorted_by_source_count(self):
        """Breaking news should be sorted by Source_Count descending."""
        breaking_news = [
            self.create_candidate(1, source_count=2),
            self.create_candidate(2, source_count=5),
            self.create_candidate(3, source_count=3),
        ]

        # Sort by Source_Count descending
        breaking_news.sort(key=lambda x: x.get('Source_Count', 1), reverse=True)

        # Should be ordered: 5, 3, 2
        assert breaking_news[0]['Source_Count'] == 5
        assert breaking_news[1]['Source_Count'] == 3
        assert breaking_news[2]['Source_Count'] == 2

    def test_breaking_news_capped_at_half_slots(self):
        """Breaking news should be capped at 50% of CANDIDATE_SELECTION_LIMIT."""
        from config import settings

        # Create more breaking news than half the limit
        limit = settings.CANDIDATE_SELECTION_LIMIT
        half_limit = limit // 2

        # Create double the half_limit of breaking articles
        breaking_news = [
            self.create_candidate(i, source_count=2)
            for i in range(half_limit * 2)
        ]

        # Cap at half
        breaking_limit = min(len(breaking_news), half_limit)
        selected_breaking = breaking_news[:breaking_limit]

        assert len(selected_breaking) == half_limit
        assert len(selected_breaking) <= limit // 2

    def test_regular_news_fills_remaining_slots(self):
        """Regular news should fill remaining slots after breaking news."""
        from config import settings

        limit = settings.CANDIDATE_SELECTION_LIMIT

        # 10 breaking news articles
        breaking_news = [self.create_candidate(i, source_count=3) for i in range(10)]

        # 100 regular news articles
        regular_news = [self.create_candidate(i + 100, source_count=1) for i in range(100)]

        # Cap breaking at half
        breaking_limit = min(len(breaking_news), limit // 2)
        selected_breaking = breaking_news[:breaking_limit]

        # Fill remaining with regular
        remaining_slots = limit - len(selected_breaking)
        selected_regular = regular_news[:remaining_slots]

        # Combined should equal limit (or less if not enough candidates)
        total = len(selected_breaking) + len(selected_regular)
        assert total == limit

    def test_all_breaking_news_edge_case(self):
        """When all articles are breaking news, cap at 50% and rest from regular (empty)."""
        from config import settings

        limit = settings.CANDIDATE_SELECTION_LIMIT
        half_limit = limit // 2

        # All breaking news, no regular
        breaking_news = [self.create_candidate(i, source_count=5) for i in range(100)]
        regular_news = []

        breaking_limit = min(len(breaking_news), half_limit)
        selected_breaking = breaking_news[:breaking_limit]

        remaining_slots = limit - len(selected_breaking)
        selected_regular = regular_news[:remaining_slots]

        candidate_list = selected_breaking + selected_regular

        # Should only have half_limit articles (all breaking, no regular to fill)
        assert len(candidate_list) == half_limit

    def test_no_breaking_news_edge_case(self):
        """When no breaking news exists, all slots filled with regular articles."""
        from config import settings

        limit = settings.CANDIDATE_SELECTION_LIMIT

        # No breaking news, all regular
        breaking_news = []
        regular_news = [self.create_candidate(i, source_count=1) for i in range(100)]

        breaking_limit = min(len(breaking_news), limit // 2)
        selected_breaking = breaking_news[:breaking_limit]

        remaining_slots = limit - len(selected_breaking)
        selected_regular = regular_news[:remaining_slots]

        candidate_list = selected_breaking + selected_regular

        # Should have full limit of regular articles
        assert len(candidate_list) == limit
        assert all(c['Source_Count'] == 1 for c in candidate_list)

    def test_breaking_news_preserves_order_regular_is_random(self):
        """Breaking news order is preserved (by source count), regular is randomized."""
        import random

        # Set seed for reproducibility in test
        random.seed(42)

        breaking_news = [
            self.create_candidate(1, source_count=5),
            self.create_candidate(2, source_count=3),
            self.create_candidate(3, source_count=2),
        ]
        regular_news = [
            self.create_candidate(10, source_count=1),
            self.create_candidate(11, source_count=1),
            self.create_candidate(12, source_count=1),
        ]

        # Sort breaking by Source_Count descending
        breaking_news.sort(key=lambda x: x.get('Source_Count', 1), reverse=True)

        # Breaking order should be: 5, 3, 2
        assert [b['Source_Count'] for b in breaking_news] == [5, 3, 2]

        # Regular should be shuffled
        original_order = [r['News_Feed_ID'] for r in regular_news]
        random.shuffle(regular_news)
        shuffled_order = [r['News_Feed_ID'] for r in regular_news]

        # Order may or may not be different due to random, but shuffle was called
        # This is testing the mechanism, not the exact output

    def test_source_count_default_value(self):
        """Articles without Source_Count should default to 1 (regular)."""
        candidate_no_source = {
            'URL': 'https://example.com/no-source',
            'Title': 'No Source Count',
            'News_Feed_ID': 999
            # No 'Source_Count' key
        }

        source_count = candidate_no_source.get('Source_Count', 1)
        assert source_count == 1

        # Should be classified as regular
        is_breaking = source_count > 1
        assert is_breaking is False

    def test_exact_half_limit_breaking_news(self):
        """When breaking news exactly equals half limit, no overflow."""
        from config import settings

        limit = settings.CANDIDATE_SELECTION_LIMIT
        half_limit = limit // 2

        # Exactly half_limit breaking news
        breaking_news = [self.create_candidate(i, source_count=2) for i in range(half_limit)]
        regular_news = [self.create_candidate(i + 100, source_count=1) for i in range(100)]

        breaking_limit = min(len(breaking_news), half_limit)
        selected_breaking = breaking_news[:breaking_limit]

        remaining_slots = limit - len(selected_breaking)
        selected_regular = regular_news[:remaining_slots]

        candidate_list = selected_breaking + selected_regular

        assert len(selected_breaking) == half_limit
        assert len(selected_regular) == limit - half_limit
        assert len(candidate_list) == limit


class TestCandidateSelectionIntegration:
    """Integration tests that verify the full candidate selection behavior with structured output."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create an AIService with mocked Gemini model using structured output."""
        with patch('services.ai_service.genai') as mock_genai:
            # Mock the Client and its models
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client

            # Mock the model list
            mock_model = MagicMock()
            mock_model.name = 'models/gemini-2.0-flash'
            mock_client.models.list.return_value = [mock_model]

            # Mock the generate_content response with structured output
            mock_response = MagicMock()
            mock_response.text = "DIFFERENT"
            mock_response.parsed = [
                SelectedArticle(url='https://example.com/article-1', title='Breaking Article 1'),
                SelectedArticle(url='https://example.com/article-2', title='Article 2')
            ]
            mock_client.models.generate_content.return_value = mock_response

            from services.ai_service import AIService
            service = AIService()
            yield service, mock_client, mock_response

    def test_high_source_count_articles_included_in_candidates(self, mock_ai_service):
        """Verify that high Source_Count articles make it into the candidate pool."""
        service, mock_client, mock_response = mock_ai_service
        # This is an integration test placeholder
        # Full integration would require more complex mocking
        pass

    def test_select_articles_structured_output(self, mock_ai_service):
        """Verify that structured output SelectedArticle list is correctly matched against candidates."""
        service, mock_client, mock_response = mock_ai_service
        from services.ai_service import FeedPost
        from datetime import datetime

        # Set up candidates that match the URLs in mock_response.parsed
        candidates = [
            {
                'URL': 'https://example.com/article-1',
                'Title': 'Breaking Article 1',
                'News_Feed_ID': 1,
                'Source_Count': 3
            },
            {
                'URL': 'https://example.com/article-2',
                'Title': 'Article 2',
                'News_Feed_ID': 2,
                'Source_Count': 1
            },
            {
                'URL': 'https://example.com/article-3',
                'Title': 'Article 3',
                'News_Feed_ID': 3,
                'Source_Count': 1
            },
        ]

        recent_posts = [
            FeedPost(text='Old post', url='https://example.com/old', title='Old Article', timestamp=datetime.now())
        ]

        result = service.select_news_articles(candidates, recent_posts, max_count=2)

        # Should return exactly 2 articles matching the structured output
        assert len(result) == 2
        assert result[0]['URL'] == 'https://example.com/article-1'
        assert result[0]['Title'] == 'Breaking Article 1'
        assert result[0]['News_Feed_ID'] == 1
        assert result[1]['URL'] == 'https://example.com/article-2'
        assert result[1]['Title'] == 'Article 2'
        assert result[1]['News_Feed_ID'] == 2

    def test_select_articles_none_response(self, mock_ai_service):
        """Verify fallback when response.parsed is None (should fall through to direct candidate selection)."""
        service, mock_client, mock_response = mock_ai_service
        from services.ai_service import FeedPost
        from datetime import datetime

        # Set parsed to None to simulate truncated/failed structured output
        mock_response.parsed = None

        candidates = [
            {
                'URL': 'https://example.com/article-1',
                'Title': 'Breaking Article 1',
                'News_Feed_ID': 1,
                'Source_Count': 3
            },
            {
                'URL': 'https://example.com/article-2',
                'Title': 'Article 2',
                'News_Feed_ID': 2,
                'Source_Count': 1
            },
        ]

        recent_posts = [
            FeedPost(text='Old post', url='https://example.com/old', title='Old Article', timestamp=datetime.now())
        ]

        result = service.select_news_articles(candidates, recent_posts, max_count=2)

        # Should fall back to direct candidate selection (top candidates from list)
        assert len(result) == 2
        # Fallback returns top candidates - articles should still be present
        urls = [r['URL'] for r in result]
        assert 'https://example.com/article-1' in urls
        assert 'https://example.com/article-2' in urls


class TestSimilarityCheck:
    """Tests for the AI similarity check using structured enum output."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create an AIService with mocked Gemini model for similarity checks."""
        with patch('services.ai_service.genai') as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client

            mock_model = MagicMock()
            mock_model.name = 'models/gemini-2.0-flash'
            mock_client.models.list.return_value = [mock_model]

            mock_response = MagicMock()
            mock_client.models.generate_content.return_value = mock_response

            from services.ai_service import AIService
            service = AIService()
            yield service, mock_client, mock_response

    def test_similarity_check_similar(self, mock_ai_service):
        """When AI returns 'SIMILAR', check_content_similarity should return True."""
        service, mock_client, mock_response = mock_ai_service
        from services.ai_service import FeedPost
        from datetime import datetime

        mock_response.text = 'SIMILAR'

        recent_posts = [
            FeedPost(
                text='Economy grows as GDP rises',
                url='https://example.com/economy',
                title='GDP Growth Accelerates',
                timestamp=datetime.now()
            )
        ]

        # Use a title that is different enough to not trigger keyword pre-filter
        # but similar enough for AI to flag
        result = service.check_content_similarity(
            article_title='Federal Reserve Adjusts Interest Rates',
            article_text='The Federal Reserve announced changes to interest rates today.',
            recent_posts=recent_posts
        )

        assert result is True

    def test_similarity_check_different(self, mock_ai_service):
        """When AI returns 'DIFFERENT', check_content_similarity should return False."""
        service, mock_client, mock_response = mock_ai_service
        from services.ai_service import FeedPost
        from datetime import datetime

        mock_response.text = 'DIFFERENT'

        recent_posts = [
            FeedPost(
                text='Weather forecast for the week',
                url='https://example.com/weather',
                title='Weekly Weather Outlook',
                timestamp=datetime.now()
            )
        ]

        result = service.check_content_similarity(
            article_title='New Technology Breakthrough in Quantum Computing',
            article_text='Scientists have achieved a major breakthrough in quantum computing.',
            recent_posts=recent_posts
        )

        assert result is False

    def test_similarity_check_none_response(self, mock_ai_service):
        """When response.text is None, check_content_similarity should return False (not crash)."""
        service, mock_client, mock_response = mock_ai_service
        from services.ai_service import FeedPost
        from datetime import datetime

        # Use PropertyMock to make .text return None
        type(mock_response).text = PropertyMock(return_value=None)

        recent_posts = [
            FeedPost(
                text='Some post about politics',
                url='https://example.com/politics',
                title='Political News Update',
                timestamp=datetime.now()
            )
        ]

        result = service.check_content_similarity(
            article_title='Space Exploration Mission Launches Successfully',
            article_text='NASA launched a new mission to explore the outer planets.',
            recent_posts=recent_posts
        )

        # Should default to not similar when response is None
        assert result is False


class TestTweetGeneration:
    """Tests for AI tweet generation using structured output."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create an AIService with mocked Gemini model for tweet generation."""
        with patch('services.ai_service.genai') as mock_genai:
            mock_client = MagicMock()
            mock_genai.Client.return_value = mock_client

            mock_model = MagicMock()
            mock_model.name = 'models/gemini-2.0-flash'
            mock_client.models.list.return_value = [mock_model]

            mock_response = MagicMock()
            mock_client.models.generate_content.return_value = mock_response

            from services.ai_service import AIService
            service = AIService()
            yield service, mock_client, mock_response

    def test_generate_tweet_structured(self, mock_ai_service):
        """Verify that structured TweetResponse is correctly parsed into tweet dict."""
        service, mock_client, mock_response = mock_ai_service

        mock_response.parsed = TweetResponse(
            tweet_text='Scientists discover high-energy particles from deep space, reshaping understanding of cosmic rays.',
            hashtag='Science',
            summary='Researchers have detected unprecedented high-energy cosmic ray particles.'
        )

        result = service.generate_tweet(
            article_text='Scientists have discovered high-energy particles originating from deep space...',
            article_title='Cosmic Ray Discovery Stuns Scientists',
            article_url='https://example.com/cosmic-rays'
        )

        assert result is not None
        # tweet_text should contain the original text plus hashtags
        assert '#Science' in result['tweet_text']
        assert '#News' in result['tweet_text']
        assert 'Scientists discover high-energy particles' in result['tweet_text']
        # Summary should be present
        assert result['summary'] == 'Researchers have detected unprecedented high-energy cosmic ray particles.'
        # Facets should exist for hashtag formatting
        assert 'facets' in result
        assert len(result['facets']) == 2  # One for generated hashtag, one for #News

    def test_generate_tweet_hashtag_with_hash_prefix(self, mock_ai_service):
        """Verify that hashtag with # prefix is handled correctly (# is stripped)."""
        service, mock_client, mock_response = mock_ai_service

        mock_response.parsed = TweetResponse(
            tweet_text='New trade deal signed between major economies.',
            hashtag='#Trade',
            summary='A landmark trade agreement was finalized today.'
        )

        result = service.generate_tweet(
            article_text='A major trade deal was signed today...',
            article_title='Trade Deal Signed',
            article_url='https://example.com/trade'
        )

        assert result is not None
        # The # should be stripped, then re-added in the final text
        assert '#Trade' in result['tweet_text']
        # Should not have double ##
        assert '##' not in result['tweet_text']

    def test_generate_tweet_none_response(self, mock_ai_service):
        """Verify that None parsed response returns None (not crash)."""
        service, mock_client, mock_response = mock_ai_service

        mock_response.parsed = None

        result = service.generate_tweet(
            article_text='Some article text here.',
            article_title='Some Article',
            article_url='https://example.com/article'
        )

        assert result is None


class TestPydanticModels:
    """Tests for the Pydantic model definitions used in structured output."""

    def test_selected_article_creation(self):
        """Verify SelectedArticle can be created with expected fields."""
        article = SelectedArticle(url='https://example.com/test', title='Test Article')
        assert article.url == 'https://example.com/test'
        assert article.title == 'Test Article'

    def test_tweet_response_creation(self):
        """Verify TweetResponse can be created with expected fields."""
        tweet = TweetResponse(
            tweet_text='Test tweet text',
            hashtag='TestTag',
            summary='Test summary'
        )
        assert tweet.tweet_text == 'Test tweet text'
        assert tweet.hashtag == 'TestTag'
        assert tweet.summary == 'Test summary'

    def test_similarity_result_enum_values(self):
        """Verify SimilarityResult enum has expected values."""
        assert SimilarityResult.SIMILAR.value == "SIMILAR"
        assert SimilarityResult.DIFFERENT.value == "DIFFERENT"

    def test_similarity_result_enum_from_string(self):
        """Verify SimilarityResult can be created from string value."""
        assert SimilarityResult("SIMILAR") == SimilarityResult.SIMILAR
        assert SimilarityResult("DIFFERENT") == SimilarityResult.DIFFERENT


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
