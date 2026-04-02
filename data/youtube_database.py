"""
YouTube Database Module

This module handles database connections and operations for the YouTube database
([NewsAnalysis.YouTube]). It provides functions for fetching video candidates,
marking videos as posted, and managing YouTube-specific data.
"""

import pyodbc
import pandas as pd
import logging
from typing import Optional, Dict

from config import settings
from utils.exceptions import DatabaseError, QueryError
from utils.exceptions import ConnectionError as DatabaseConnectionError

logger = logging.getLogger(__name__)


class YouTubeDatabaseConnection:
    """Database connection manager for the YouTube database."""

    def __init__(self):
        """Initialize the YouTube database connection."""
        self.conn = None
        pyodbc.pooling = False

    def connect(self) -> bool:
        """
        Establish a connection to the YouTube database.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            self.conn = pyodbc.connect(settings.YOUTUBE_DB_CONNECTION_STRING)
            self.conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            logger.info("Successfully connected to YouTube database")
            return True
        except DatabaseConnectionError:
            raise
        except Exception as e:
            logger.error(f"Failed to connect to YouTube database: {e}")
            self.conn = None
            return False

    def close(self) -> None:
        """Close the database connection."""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                logger.info("YouTube database connection closed")
        except Exception as e:
            logger.error(f"Error closing YouTube database connection: {e}")

    def get_youtube_candidates(
        self,
        limit: int = settings.YOUTUBE_MAX_CANDIDATES,
        max_age_days: int = settings.YOUTUBE_MAX_AGE_DAYS,
        min_views: int = settings.YOUTUBE_MIN_VIEWS
    ) -> Optional[pd.DataFrame]:
        """
        Fetch candidate videos for posting from the YouTube database.

        Joins tbl_YouTube_Video with tbl_YouTube_Channel and applies filters:
        - Not already posted (Used_In_BSky = 0)
        - Not a Short (Is_Short = 0)
        - Not a live stream (Is_Live = 0)
        - Published within max_age_days
        - Minimum view count threshold
        - Channel is active

        Args:
            limit: Maximum number of candidates to return.
            max_age_days: Only consider videos from the last N days.
            min_views: Minimum view count threshold.

        Returns:
            Optional[pd.DataFrame]: DataFrame of video candidates, or None on error.
        """
        query = f"""
        SELECT TOP ({limit})
            v.[YouTube_Video_ID],
            v.[YouTube_Video_Key],
            v.[Title],
            v.[Description],
            v.[Published_Date],
            v.[Thumbnail_URL],
            v.[Duration_Seconds],
            v.[View_Count],
            v.[Like_Count],
            v.[Comment_Count],
            c.[Channel_Name],
            c.[Channel_Handle]
        FROM [dbo].[tbl_YouTube_Video] v
        INNER JOIN [dbo].[tbl_YouTube_Channel] c
            ON v.[YouTube_Channel_ID] = c.[YouTube_Channel_ID]
        WHERE v.[Used_In_BSky] = 0
            AND v.[Is_Short] = 0
            AND v.[Is_Live] = 0
            AND c.[Is_Active] = 1
            AND v.[Published_Date] >= DATEADD(day, -{max_age_days}, GETUTCDATE())
            AND v.[View_Count] >= {min_views}
        ORDER BY
            (v.[View_Count] + v.[Like_Count] * 10 + v.[Comment_Count] * 5) DESC,
            v.[Published_Date] DESC
        """

        try:
            if not self.conn and not self.connect():
                return None

            return pd.read_sql(query, self.conn)

        except (QueryError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Error fetching YouTube candidates: {e}")
            return None

    def mark_video_posted(self, youtube_video_id: int) -> bool:
        """
        Mark a video as posted to BlueSky.

        Args:
            youtube_video_id: The YouTube_Video_ID to mark as posted.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        query = """
        UPDATE [dbo].[tbl_YouTube_Video]
        SET [Used_In_BSky] = 1
        WHERE [YouTube_Video_ID] = ?
        """

        if not self.conn and not self.connect():
            return False

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (youtube_video_id,))
            self.conn.commit()
            logger.info(f"Marked YouTube video as posted - YouTube_Video_ID: {youtube_video_id}")
            return True
        except (QueryError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Error marking YouTube video as posted: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False

    def get_video_by_key(self, video_key: str) -> Optional[Dict]:
        """
        Look up a single video by its YouTube_Video_Key.

        Args:
            video_key: The 11-character YouTube video ID.

        Returns:
            Optional[Dict]: Video data as a dictionary, or None if not found.
        """
        query = """
        SELECT
            v.[YouTube_Video_ID],
            v.[YouTube_Video_Key],
            v.[Title],
            v.[Description],
            v.[Published_Date],
            v.[Thumbnail_URL],
            v.[Duration_Seconds],
            v.[View_Count],
            v.[Like_Count],
            v.[Comment_Count],
            v.[Used_In_BSky],
            c.[Channel_Name],
            c.[Channel_Handle]
        FROM [dbo].[tbl_YouTube_Video] v
        INNER JOIN [dbo].[tbl_YouTube_Channel] c
            ON v.[YouTube_Channel_ID] = c.[YouTube_Channel_ID]
        WHERE v.[YouTube_Video_Key] = ?
        """

        if not self.conn and not self.connect():
            return None

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (video_key,))
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    return dict(zip(columns, row))
            return None
        except (QueryError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Error looking up YouTube video by key: {e}")
            return None


# Create a default YouTube database instance
youtube_db = YouTubeDatabaseConnection()
