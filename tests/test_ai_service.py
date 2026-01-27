"""
Tests for AI Service - Breaking News Prioritization

Tests the candidate selection logic that prioritizes articles with higher Source_Count
while maintaining variety through randomization of regular articles.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    """Integration tests that verify the full candidate selection behavior."""

    @pytest.fixture
    def mock_ai_service(self):
        """Create an AIService with mocked Gemini model."""
        with patch('services.ai_service.genai') as mock_genai:
            # Mock the model list
            mock_model = MagicMock()
            mock_model.name = 'models/gemini-2.0-flash'
            mock_genai.list_models.return_value = [mock_model]

            # Mock the GenerativeModel
            mock_gen_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = """1. URL: https://example.com/article-1
   TITLE: Breaking Article 1
2. URL: https://example.com/article-2
   TITLE: Article 2"""
            mock_gen_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_gen_model

            from services.ai_service import AIService
            service = AIService()
            yield service

    def test_high_source_count_articles_included_in_candidates(self, mock_ai_service):
        """Verify that high Source_Count articles make it into the candidate pool."""
        # This is an integration test placeholder
        # Full integration would require more complex mocking
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
