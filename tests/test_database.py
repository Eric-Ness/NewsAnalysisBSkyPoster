"""
Tests for DatabaseConnection Class

Tests for the database module including connection management, query execution,
news feed operations, and social post operations.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import DatabaseConnection, SocialPostData
from utils.exceptions import DatabaseError, QueryError
from utils.exceptions import ConnectionError as DatabaseConnectionError


class TestConnectionManagement:
    """Tests for database connection management."""

    def test_connect_success(self, mock_db_connection, mock_settings):
        """
        Test successful database connection establishment.

        Verifies that connect() returns True and sets the connection
        when pyodbc.connect() succeeds.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        result = db.connect()

        assert result is True
        assert db.conn is not None

    def test_connect_failure(self, mock_settings):
        """
        Test connection failure handling.

        Verifies that connect() returns False and conn remains None
        when pyodbc.connect() raises an exception.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            db = DatabaseConnection()
            result = db.connect()

            assert result is False
            assert db.conn is None

    def test_connect_raises_database_connection_error(self, mock_settings):
        """
        Test that DatabaseConnectionError is re-raised without being caught.

        Verifies that specific DatabaseConnectionError exceptions are
        propagated to the caller rather than being handled internally.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = DatabaseConnectionError("Auth failed")

            db = DatabaseConnection()
            with pytest.raises(DatabaseConnectionError):
                db.connect()

    def test_close_success(self, mock_db_connection, mock_settings):
        """
        Test successful database connection close.

        Verifies that close() properly closes the connection and
        sets conn to None.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()
        db.close()

        mock_conn.close.assert_called_once()
        assert db.conn is None

    def test_close_when_not_connected(self, mock_settings):
        """
        Test closing when no connection exists.

        Verifies that close() handles the case where conn is None
        without raising an exception.
        """
        db = DatabaseConnection()
        # conn is already None
        db.close()  # Should not raise

        assert db.conn is None

    def test_close_handles_exception(self, mock_db_connection, mock_settings):
        """
        Test that close() handles exceptions during closing.

        Verifies that close() logs errors but doesn't raise exceptions
        when the underlying close operation fails.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_conn.close.side_effect = Exception("Close failed")

        db = DatabaseConnection()
        db.connect()

        # Should not raise, just log the error
        db.close()

    def test_context_manager(self, mock_db_connection, mock_settings):
        """
        Test DatabaseConnection as a context manager (with statement).

        Note: DatabaseConnection does not currently implement __enter__ and __exit__.
        This test documents the expected behavior if context manager support is added.
        """
        # DatabaseConnection does not have __enter__/__exit__ yet
        # This test verifies the expected manual usage pattern
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        try:
            db.connect()
            assert db.conn is not None
        finally:
            db.close()
            assert db.conn is None


class TestQueryExecution:
    """Tests for query execution functionality."""

    def test_execute_query_success(self, mock_db_connection, mock_settings):
        """
        Test successful query execution.

        Verifies that execute_query() returns results as a list of
        dictionaries when a SELECT query succeeds.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'Test'), (2, 'Test2')]

        db = DatabaseConnection()
        db.connect()
        result = db.execute_query("SELECT * FROM test_table")

        assert result is not None
        assert len(result) == 2
        assert result[0] == {'id': 1, 'name': 'Test'}
        assert result[1] == {'id': 2, 'name': 'Test2'}

    def test_execute_query_with_params(self, mock_db_connection, mock_settings):
        """
        Test query execution with parameters.

        Verifies that execute_query() correctly passes parameters
        to the cursor.execute() method.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'Test')]

        db = DatabaseConnection()
        db.connect()
        result = db.execute_query("SELECT * FROM test WHERE id = ?", (1,))

        mock_cursor.execute.assert_called_with("SELECT * FROM test WHERE id = ?", (1,))
        assert result is not None
        assert len(result) == 1

    def test_execute_query_failure(self, mock_db_connection, mock_settings):
        """
        Test query execution failure handling.

        Verifies that execute_query() returns None and performs a rollback
        when the query execution raises an exception.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("SQL Error")

        db = DatabaseConnection()
        db.connect()
        result = db.execute_query("SELECT * FROM invalid_table")

        assert result is None
        mock_conn.rollback.assert_called_once()

    def test_execute_query_raises_query_error(self, mock_db_connection, mock_settings):
        """
        Test that QueryError is re-raised without being caught.

        Verifies that specific QueryError exceptions are propagated
        to the caller.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = QueryError("Invalid query")

        db = DatabaseConnection()
        db.connect()

        with pytest.raises(QueryError):
            db.execute_query("SELECT * FROM test")

    def test_execute_query_raises_database_error(self, mock_db_connection, mock_settings):
        """
        Test that DatabaseError is re-raised without being caught.

        Verifies that specific DatabaseError exceptions are propagated
        to the caller.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = DatabaseError("Database issue")

        db = DatabaseConnection()
        db.connect()

        with pytest.raises(DatabaseError):
            db.execute_query("SELECT * FROM test")

    def test_execute_query_not_connected(self, mock_settings):
        """
        Test query execution when not connected.

        Verifies that execute_query() attempts to connect and returns
        None if connection fails.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            db = DatabaseConnection()
            result = db.execute_query("SELECT * FROM test")

            assert result is None

    def test_execute_query_auto_connects(self, mock_db_connection, mock_settings):
        """
        Test that execute_query() automatically connects if not connected.

        Verifies that the method establishes a connection before
        executing the query when conn is None.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [('id',)]
        mock_cursor.fetchall.return_value = [(1,)]

        db = DatabaseConnection()
        # Don't call connect() explicitly
        result = db.execute_query("SELECT * FROM test")

        assert result is not None
        assert db.conn is not None

    def test_execute_query_non_select(self, mock_db_connection, mock_settings):
        """
        Test execution of non-SELECT queries (INSERT, UPDATE, DELETE).

        Verifies that execute_query() returns an empty list and commits
        when the query doesn't return results (cursor.description is None).
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = None  # Non-SELECT query

        db = DatabaseConnection()
        db.connect()
        result = db.execute_query("UPDATE test SET name = ? WHERE id = ?", ('NewName', 1))

        assert result == []
        mock_conn.commit.assert_called_once()


class TestNewsFeedOperations:
    """Tests for news feed database operations."""

    def test_get_news_feed_success(self, mock_db_connection, mock_settings):
        """
        Test successful retrieval of news feed data.

        Verifies that get_news_feed() returns a pandas DataFrame
        when the query succeeds.
        """
        mock_conn, mock_cursor = mock_db_connection

        with patch('pandas.read_sql') as mock_read_sql:
            expected_df = pd.DataFrame({
                'News_Feed_ID': [1, 2],
                'Title': ['Article 1', 'Article 2'],
                'URL': ['https://example.com/1', 'https://example.com/2']
            })
            mock_read_sql.return_value = expected_df

            db = DatabaseConnection()
            db.connect()
            result = db.get_news_feed()

            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2

    def test_get_news_feed_empty(self, mock_db_connection, mock_settings):
        """
        Test retrieval of empty news feed.

        Verifies that get_news_feed() returns an empty DataFrame
        when no results are found.
        """
        mock_conn, mock_cursor = mock_db_connection

        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.return_value = pd.DataFrame()

            db = DatabaseConnection()
            db.connect()
            result = db.get_news_feed()

            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_news_feed_error(self, mock_db_connection, mock_settings):
        """
        Test error handling in get_news_feed().

        Verifies that get_news_feed() returns None when an exception
        occurs during the query.
        """
        mock_conn, mock_cursor = mock_db_connection

        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.side_effect = Exception("Query failed")

            db = DatabaseConnection()
            db.connect()
            result = db.get_news_feed()

            assert result is None

    def test_get_news_feed_raises_query_error(self, mock_db_connection, mock_settings):
        """
        Test that QueryError is propagated from get_news_feed().

        Verifies that specific QueryError exceptions are re-raised.
        """
        mock_conn, mock_cursor = mock_db_connection

        with patch('pandas.read_sql') as mock_read_sql:
            mock_read_sql.side_effect = QueryError("Invalid SQL")

            db = DatabaseConnection()
            db.connect()

            with pytest.raises(QueryError):
                db.get_news_feed()

    def test_get_news_feed_not_connected(self, mock_settings):
        """
        Test get_news_feed() when not connected.

        Verifies that the method returns None if connection cannot
        be established.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            db = DatabaseConnection()
            result = db.get_news_feed()

            assert result is None

    def test_update_news_feed_bluesky(self, mock_db_connection, mock_settings):
        """
        Test successful update of news feed after BlueSky post.

        Verifies that update_news_feed_bluesky() executes the correct
        update query and commits the transaction.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()
        result = db.update_news_feed_bluesky(
            news_feed_id=123,
            article_text="Article content",
            bsky_tweet="Posted to BlueSky",
            article_url="https://example.com/article",
            article_img="https://example.com/image.jpg"
        )

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_update_news_feed_bluesky_failure(self, mock_db_connection, mock_settings):
        """
        Test update failure for BlueSky post.

        Verifies that update_news_feed_bluesky() returns False and
        performs a rollback when the update fails.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Update failed")

        db = DatabaseConnection()
        db.connect()
        result = db.update_news_feed_bluesky(
            news_feed_id=123,
            article_text="Content",
            bsky_tweet="Tweet",
            article_url="https://example.com",
            article_img="https://example.com/img.jpg"
        )

        assert result is False
        mock_conn.rollback.assert_called_once()

    def test_update_news_feed_twitter(self, mock_db_connection, mock_settings):
        """
        Test successful update of news feed after Twitter post.

        Verifies that update_news_feed_twitter() executes the correct
        update query and commits the transaction.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()
        result = db.update_news_feed_twitter(
            news_feed_id=456,
            article_text="Article content",
            twitter_tweet="Posted to Twitter",
            article_url="https://example.com/article",
            article_img="https://example.com/image.jpg"
        )

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_update_news_feed_twitter_failure(self, mock_db_connection, mock_settings):
        """
        Test update failure for Twitter post.

        Verifies that update_news_feed_twitter() returns False and
        performs a rollback when the update fails.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Update failed")

        db = DatabaseConnection()
        db.connect()
        result = db.update_news_feed_twitter(
            news_feed_id=456,
            article_text="Content",
            twitter_tweet="Tweet",
            article_url="https://example.com",
            article_img="https://example.com/img.jpg"
        )

        assert result is False
        mock_conn.rollback.assert_called_once()

    def test_update_news_feed_delegates_to_bluesky(self, mock_db_connection, mock_settings):
        """
        Test that update_news_feed() delegates to BlueSky by default.

        Verifies that the generic update_news_feed() method calls
        update_news_feed_bluesky() when platform is 'bluesky'.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()

        with patch.object(db, 'update_news_feed_bluesky', return_value=True) as mock_bsky:
            result = db.update_news_feed(
                news_feed_id=1,
                article_text="Text",
                social_text="Social",
                article_url="https://example.com",
                article_img="https://example.com/img.jpg",
                platform="bluesky"
            )

            mock_bsky.assert_called_once()
            assert result is True

    def test_update_news_feed_delegates_to_twitter(self, mock_db_connection, mock_settings):
        """
        Test that update_news_feed() delegates to Twitter.

        Verifies that the generic update_news_feed() method calls
        update_news_feed_twitter() when platform is 'twitter'.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()

        with patch.object(db, 'update_news_feed_twitter', return_value=True) as mock_twitter:
            result = db.update_news_feed(
                news_feed_id=1,
                article_text="Text",
                social_text="Social",
                article_url="https://example.com",
                article_img="https://example.com/img.jpg",
                platform="twitter"
            )

            mock_twitter.assert_called_once()
            assert result is True

    def test_update_news_feed_not_connected(self, mock_settings):
        """
        Test update_news_feed_bluesky() when not connected.

        Verifies that the method returns False if connection cannot
        be established.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            db = DatabaseConnection()
            result = db.update_news_feed_bluesky(
                news_feed_id=1,
                article_text="Text",
                bsky_tweet="Tweet",
                article_url="https://example.com",
                article_img="https://example.com/img.jpg"
            )

            assert result is False


class TestSocialPostOperations:
    """Tests for social post database operations."""

    def test_insert_social_post_success(self, mock_db_connection, mock_settings, social_post_data_factory):
        """
        Test successful insertion of a social post.

        Verifies that insert_social_post() executes the insert query,
        commits the transaction, and returns the inserted ID.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = (42,)  # Simulated inserted ID

        db = DatabaseConnection()
        db.connect()

        post_data = social_post_data_factory()
        result = db.insert_social_post(post_data)

        assert result == 42
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_insert_social_post_failure(self, mock_db_connection, mock_settings, social_post_data_factory):
        """
        Test insert failure handling.

        Verifies that insert_social_post() returns None and performs
        a rollback when the insert fails.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Insert failed")

        db = DatabaseConnection()
        db.connect()

        post_data = social_post_data_factory()
        result = db.insert_social_post(post_data)

        assert result is None
        mock_conn.rollback.assert_called_once()

    def test_insert_social_post_no_id_returned(self, mock_db_connection, mock_settings, social_post_data_factory):
        """
        Test insert when no ID is returned from OUTPUT clause.

        Verifies that insert_social_post() returns None when
        fetchone() returns None.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None

        db = DatabaseConnection()
        db.connect()

        post_data = social_post_data_factory()
        result = db.insert_social_post(post_data)

        assert result is None

    def test_insert_social_post_raises_query_error(self, mock_db_connection, mock_settings, social_post_data_factory):
        """
        Test that QueryError is propagated from insert_social_post().

        Verifies that specific QueryError exceptions are re-raised.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = QueryError("Query failed")

        db = DatabaseConnection()
        db.connect()

        post_data = social_post_data_factory()

        with pytest.raises(QueryError):
            db.insert_social_post(post_data)

    def test_get_social_post_by_id_found(self, mock_db_connection, mock_settings):
        """
        Test retrieval of a social post by ID when found.

        Verifies that get_social_post_by_id() returns the post data
        as a dictionary when a matching record exists.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('Social_Post_ID',), ('Platform',), ('Post_Text',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'bluesky', 'Test post content')
        ]

        db = DatabaseConnection()
        db.connect()
        result = db.get_social_post_by_id(1)

        assert result is not None
        assert result['Social_Post_ID'] == 1
        assert result['Platform'] == 'bluesky'
        assert result['Post_Text'] == 'Test post content'

    def test_get_social_post_by_id_not_found(self, mock_db_connection, mock_settings):
        """
        Test retrieval of a social post by ID when not found.

        Verifies that get_social_post_by_id() returns None when
        no matching record exists.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [('Social_Post_ID',)]
        mock_cursor.fetchall.return_value = []

        db = DatabaseConnection()
        db.connect()
        result = db.get_social_post_by_id(999)

        assert result is None

    def test_get_recent_social_posts(self, mock_db_connection, mock_settings):
        """
        Test retrieval of recent social posts with limit.

        Verifies that get_recent_social_posts() returns the correct
        number of posts ordered by created_at descending.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('Social_Post_ID',), ('Platform',), ('Post_Text',), ('Created_At',)
        ]
        mock_cursor.fetchall.return_value = [
            (3, 'bluesky', 'Post 3', datetime(2024, 1, 3)),
            (2, 'twitter', 'Post 2', datetime(2024, 1, 2)),
            (1, 'bluesky', 'Post 1', datetime(2024, 1, 1)),
        ]

        db = DatabaseConnection()
        db.connect()
        result = db.get_recent_social_posts(limit=3)

        assert result is not None
        assert len(result) == 3
        mock_cursor.execute.assert_called_once()

    def test_get_recent_social_posts_with_platform_filter(self, mock_db_connection, mock_settings):
        """
        Test retrieval of recent posts filtered by platform.

        Verifies that get_recent_social_posts() correctly filters
        results by the specified platform.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('Social_Post_ID',), ('Platform',), ('Post_Text',)
        ]
        mock_cursor.fetchall.return_value = [
            (3, 'bluesky', 'Post 3'),
            (1, 'bluesky', 'Post 1'),
        ]

        db = DatabaseConnection()
        db.connect()
        result = db.get_recent_social_posts(platform='bluesky', limit=10)

        assert result is not None
        assert len(result) == 2
        # Verify query includes platform parameter
        call_args = mock_cursor.execute.call_args
        assert 'Platform' in call_args[0][0]

    def test_get_recent_social_posts_empty(self, mock_db_connection, mock_settings):
        """
        Test retrieval of recent posts when none exist.

        Verifies that get_recent_social_posts() returns an empty list
        when no posts are found.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [('Social_Post_ID',)]
        mock_cursor.fetchall.return_value = []

        db = DatabaseConnection()
        db.connect()
        result = db.get_recent_social_posts()

        assert result is not None
        assert len(result) == 0

    def test_get_social_posts_by_news_feed_id(self, mock_db_connection, mock_settings):
        """
        Test retrieval of social posts by news feed ID.

        Verifies that get_social_posts_by_news_feed_id() returns all
        posts associated with a given news feed item.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.description = [
            ('Social_Post_ID',), ('Platform',), ('News_Feed_ID',)
        ]
        mock_cursor.fetchall.return_value = [
            (1, 'bluesky', 100),
            (2, 'twitter', 100),
        ]

        db = DatabaseConnection()
        db.connect()
        result = db.get_social_posts_by_news_feed_id(100)

        assert result is not None
        assert len(result) == 2
        assert all(r['News_Feed_ID'] == 100 for r in result)

    def test_insert_social_post_not_connected(self, mock_settings, social_post_data_factory):
        """
        Test insert_social_post() when not connected.

        Verifies that the method returns None if connection cannot
        be established.
        """
        with patch('pyodbc.connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            db = DatabaseConnection()
            post_data = social_post_data_factory()
            result = db.insert_social_post(post_data)

            assert result is None


class TestSocialPostDataClass:
    """Tests for the SocialPostData dataclass."""

    def test_social_post_data_required_fields(self):
        """
        Test SocialPostData with only required fields.

        Verifies that SocialPostData can be created with minimum
        required fields and optional fields default to None.
        """
        post = SocialPostData(
            platform='bluesky',
            post_id='test-123',
            post_text='Test content',
            author_handle='@testuser',
            created_at=datetime.now()
        )

        assert post.platform == 'bluesky'
        assert post.post_id == 'test-123'
        assert post.post_text == 'Test content'
        assert post.author_handle == '@testuser'
        assert post.post_uri is None
        assert post.post_url is None
        assert post.news_feed_id is None

    def test_social_post_data_all_fields(self):
        """
        Test SocialPostData with all fields populated.

        Verifies that SocialPostData correctly stores all provided values.
        """
        created = datetime(2024, 1, 15, 12, 30, 0)
        post = SocialPostData(
            platform='twitter',
            post_id='tweet-456',
            post_text='Full test content',
            author_handle='@fulltest',
            created_at=created,
            post_uri='at://did:plc:test/post/123',
            post_url='https://twitter.com/test/status/456',
            author_display_name='Full Test User',
            author_avatar_url='https://example.com/avatar.jpg',
            author_did='did:plc:testuser',
            post_facets='{"links": []}',
            article_url='https://example.com/article',
            article_title='Test Article',
            article_description='Article description',
            article_image_url='https://example.com/img.jpg',
            article_image_blob='base64data',
            news_feed_id=42,
            raw_response='{"full": "response"}'
        )

        assert post.platform == 'twitter'
        assert post.author_display_name == 'Full Test User'
        assert post.news_feed_id == 42
        assert post.raw_response == '{"full": "response"}'


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_multiple_connect_calls(self, mock_db_connection, mock_settings):
        """
        Test calling connect() multiple times.

        Verifies behavior when connect() is called on an already
        connected instance.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        result1 = db.connect()
        result2 = db.connect()

        assert result1 is True
        assert result2 is True
        assert db.conn is not None

    def test_rollback_failure_during_error_handling(self, mock_db_connection, mock_settings):
        """
        Test that rollback failures are handled gracefully.

        Verifies that when execute_query() fails and rollback also fails,
        the error is handled without raising additional exceptions.
        """
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.execute.side_effect = Exception("Query failed")
        mock_conn.rollback.side_effect = Exception("Rollback failed")

        db = DatabaseConnection()
        db.connect()

        # Should not raise additional exception
        result = db.execute_query("SELECT * FROM test")
        assert result is None

    def test_pyodbc_pooling_disabled(self, mock_settings):
        """
        Test that pyodbc pooling is disabled on initialization.

        Verifies that DatabaseConnection sets pyodbc.pooling to False
        to prevent connection pooling issues.
        """
        with patch('pyodbc.connect'):
            import pyodbc
            db = DatabaseConnection()
            assert pyodbc.pooling is False

    def test_connection_encoding_set(self, mock_db_connection, mock_settings):
        """
        Test that UTF-8 encoding is set on connection.

        Verifies that connect() calls setdecoding() to configure
        UTF-8 encoding for character data.
        """
        mock_conn, mock_cursor = mock_db_connection

        db = DatabaseConnection()
        db.connect()

        mock_conn.setdecoding.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
