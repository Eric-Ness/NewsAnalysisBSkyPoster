"""
Database Module for News Poster Application

This module handles all database connections and operations for the News Poster application.
It provides functions for connecting to the database, executing queries, and managing
news feed data.
"""

import pyodbc
import pandas as pd
import logging
from typing import Optional, List, Dict, Union, Any

from config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager for the News Poster application."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.conn = None
        pyodbc.pooling = False
    
    def connect(self) -> bool:
        """
        Establish a connection to the database.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        try:
            self.conn = pyodbc.connect(settings.DB_CONNECTION_STRING)
            self.conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
            logger.info("Successfully connected to database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.conn = None
            return False
    
    def close(self) -> None:
        """Close the database connection."""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[List[Dict]]:
        """
        Execute a SQL query and return the results.
        
        Args:
            query: The SQL query to execute.
            params: Query parameters (optional).
            
        Returns:
            Optional[List[Dict]]: Query results as a list of dictionaries, or None if an error occurred.
        """
        if not self.conn and not self.connect():
            return None
            
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Check if this is a SELECT query with results
            if cursor.description:
                columns = [column[0] for column in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return results
            else:
                self.conn.commit()
                return []
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            return None

    def get_news_feed(self) -> Optional[pd.DataFrame]:
        """
        Retrieve news feed data from the database.
        
        Returns:
            Optional[pd.DataFrame]: DataFrame containing news feed data, or None if an error occurred.
        """
        # SQL query to retrieve news feed data
        query = """
        WITH TopSources AS (
            -- Get all items with the highest Source_Count value
            SELECT URL, Title, Source_Count, News_Feed_ID
            FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
            WHERE Language_ID = 23
            AND (Category_ID = 2 OR Category_ID = 1 OR Category_ID = 3)
            AND [Published_Date] >= DATEADD(day, -1, GETDATE())
            AND Source_Count > 1
        ),
        RemainingItems AS (
            -- Get items that don't have the highest Source_Count
            SELECT URL, Title, Source_Count, News_Feed_ID
            FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
            WHERE Language_ID = 23
            AND (Category_ID = 2 OR Category_ID = 1 OR Category_ID = 3)
            AND [Published_Date] >= DATEADD(day, -1, GETDATE())
            AND Source_Count > 0
            AND Source_Count < (
                SELECT MAX(Source_Count)
                FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
                WHERE Language_ID = 23
                AND (Category_ID = 2 OR Category_ID = 1 OR Category_ID = 3)
                AND [Published_Date] >= DATEADD(day, -1, GETDATE())
                AND Source_Count > 0
            )
        )
        -- Combine the two sets with top items first, then random selection from remaining
        SELECT * FROM (
            SELECT News_Feed_ID, Title, URL
            FROM TopSources
            UNION ALL
            SELECT TOP(160 - (SELECT COUNT(*) FROM TopSources)) News_Feed_ID, Title, URL
            FROM RemainingItems
            ORDER BY NEWID()
        ) AS Combined
        ORDER BY  NEWID();
        """
        
        try:
            if not self.conn and not self.connect():
                return None
                
            return pd.read_sql(query, self.conn)
            
        except Exception as e:
            logger.error(f"Error retrieving news feed: {e}")
            return None
    
    def update_news_feed(self, news_feed_id: int, article_text: str, bsky_tweet: str, 
                         article_url: str, article_img: str) -> bool:
        """
        Update a news feed entry after posting to BSky.
        
        Args:
            news_feed_id: The ID of the news feed item in the database.
            article_text: The full text of the article.
            bsky_tweet: The tweet text posted to BSky.
            article_url: The URL of the article.
            article_img: The URL of the article's image.
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        query = """
        UPDATE [dbo].[tbl_News_Feed]
        SET [Article_Text] = ?,
            [Used_In_BSky] = 1,
            [BSky_Tweet] = ?,
            [Article_URL] = ?,
            [Article_Img] = ?
        WHERE [News_Feed_ID] = ?
        """
        
        if not self.conn and not self.connect():
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (article_text, bsky_tweet, article_url, article_img, news_feed_id))
            self.conn.commit()
            logger.info(f"Successfully updated database for news_feed_id: {news_feed_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating news feed: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False

# Create a default database instance for use throughout the application
db = DatabaseConnection() 