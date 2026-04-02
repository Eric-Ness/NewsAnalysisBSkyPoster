"""
Tests for YouTube Database Module

Tests the YouTubeDatabaseConnection class including connection setup,
candidate fetching, and video posting tracking.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pandas as pd

from data.youtube_database import YouTubeDatabaseConnection


class TestYouTubeDatabaseConnection:
    """Tests for YouTubeDatabaseConnection."""

    def test_connect_success(self):
        """Should return True on successful connection."""
        with patch('data.youtube_database.pyodbc') as mock_pyodbc, \
             patch('data.youtube_database.settings') as mock_settings:
            mock_settings.YOUTUBE_DB_CONNECTION_STRING = "DRIVER={Test};SERVER=test;"
            mock_conn = MagicMock()
            mock_pyodbc.connect.return_value = mock_conn

            db = YouTubeDatabaseConnection()
            result = db.connect()

            assert result is True
            assert db.conn is not None

    def test_connect_failure(self):
        """Should return False on connection failure."""
        with patch('data.youtube_database.pyodbc') as mock_pyodbc, \
             patch('data.youtube_database.settings') as mock_settings:
            mock_settings.YOUTUBE_DB_CONNECTION_STRING = "DRIVER={Test};SERVER=test;"
            mock_pyodbc.connect.side_effect = Exception("Connection failed")

            db = YouTubeDatabaseConnection()
            result = db.connect()

            assert result is False
            assert db.conn is None

    def test_close_connection(self):
        """Should close the connection cleanly."""
        db = YouTubeDatabaseConnection()
        mock_conn = MagicMock()
        db.conn = mock_conn

        db.close()

        mock_conn.close.assert_called_once()
        assert db.conn is None

    def test_mark_video_posted_executes_update(self):
        """Should execute UPDATE query with correct video ID."""
        db = YouTubeDatabaseConnection()
        mock_cursor = MagicMock()
        db.conn = MagicMock()
        db.conn.cursor.return_value = mock_cursor

        result = db.mark_video_posted(42)

        assert result is True
        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args
        assert 'Used_In_BSky' in args[0][0]
        assert args[0][1] == (42,)
        db.conn.commit.assert_called_once()

    def test_mark_video_posted_rollback_on_error(self):
        """Should rollback on error during mark_video_posted."""
        db = YouTubeDatabaseConnection()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Update failed")
        db.conn = MagicMock()
        db.conn.cursor.return_value = mock_cursor

        result = db.mark_video_posted(42)

        assert result is False
        db.conn.rollback.assert_called_once()

    def test_get_youtube_candidates_returns_dataframe(self):
        """Should return a DataFrame from the candidate query."""
        db = YouTubeDatabaseConnection()
        db.conn = MagicMock()

        mock_df = pd.DataFrame([{
            'YouTube_Video_ID': 1,
            'YouTube_Video_Key': 'abc123def45',
            'Title': 'Test Video',
        }])

        with patch('data.youtube_database.pd.read_sql', return_value=mock_df):
            result = db.get_youtube_candidates()

        assert result is not None
        assert len(result) == 1
        assert result.iloc[0]['Title'] == 'Test Video'

    def test_get_youtube_candidates_returns_none_on_error(self):
        """Should return None when query fails."""
        db = YouTubeDatabaseConnection()
        db.conn = MagicMock()

        with patch('data.youtube_database.pd.read_sql', side_effect=Exception("Query failed")):
            result = db.get_youtube_candidates()

        assert result is None

    def test_get_video_by_key_returns_dict(self):
        """Should return video as dict when found."""
        db = YouTubeDatabaseConnection()
        mock_cursor = MagicMock()
        mock_cursor.description = [('YouTube_Video_ID',), ('Title',)]
        mock_cursor.fetchone.return_value = (1, 'Test Video')
        db.conn = MagicMock()
        db.conn.cursor.return_value = mock_cursor

        result = db.get_video_by_key('abc123def45')

        assert result is not None
        assert result['YouTube_Video_ID'] == 1
        assert result['Title'] == 'Test Video'

    def test_get_video_by_key_returns_none_when_not_found(self):
        """Should return None when video not found."""
        db = YouTubeDatabaseConnection()
        mock_cursor = MagicMock()
        mock_cursor.description = [('YouTube_Video_ID',)]
        mock_cursor.fetchone.return_value = None
        db.conn = MagicMock()
        db.conn.cursor.return_value = mock_cursor

        result = db.get_video_by_key('nonexistent')

        assert result is None
