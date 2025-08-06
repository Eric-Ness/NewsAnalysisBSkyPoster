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
        DECLARE @TotalResults INT = 160;
        DECLARE @Cat1Target INT = CAST(@TotalResults * 0.5 AS INT); -- 50% for Category 1 (90)
        DECLARE @Cat2Target INT = CAST(@TotalResults * 0.4 AS INT); -- 40% for Category 2 (72)
        DECLARE @Cat3Target INT = @TotalResults - @Cat1Target - @Cat2Target; -- 10% for Category 3 (18)

        WITH AllSources AS (
            -- Get all eligible items and rank them by Source_Count within each category
            SELECT 
                URL, Title, Source_Count, News_Feed_ID, Used_In_BSky, Used_In_Twitter, Category_ID,
                ROW_NUMBER() OVER (PARTITION BY Category_ID ORDER BY Source_Count DESC, NEWID()) as RowNum
            FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
            WHERE Language_ID = 23
            AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
            AND [Published_Date] >= DATEADD(day, -1, GETDATE())
            AND Source_Count > 0
            AND Used_In_BSky = 0
            AND Used_In_Twitter = 0
        ),
        AvailableCounts AS (
            -- Count total available records for each category
            SELECT 
                Category_ID,
                COUNT(*) AS TotalCount
            FROM AllSources
            GROUP BY Category_ID
        ),
        -- Calculate how many to take from each category, with adjustments if needed
        CategoryAllocation AS (
            SELECT
                a.Category_ID,
                a.TotalCount,
                CASE
                    WHEN a.Category_ID = 1 THEN @Cat1Target
                    WHEN a.Category_ID = 2 THEN @Cat2Target
                    WHEN a.Category_ID = 3 THEN @Cat3Target
                END AS TargetCount,
                CASE
                    WHEN a.Category_ID = 1 AND a.TotalCount < @Cat1Target THEN a.TotalCount
                    WHEN a.Category_ID = 2 AND a.TotalCount < @Cat2Target THEN a.TotalCount
                    WHEN a.Category_ID = 3 AND a.TotalCount < @Cat3Target THEN a.TotalCount
                    WHEN a.Category_ID = 1 THEN @Cat1Target
                    WHEN a.Category_ID = 2 THEN @Cat2Target
                    WHEN a.Category_ID = 3 THEN @Cat3Target
                END AS AdjustedTarget
            FROM AvailableCounts a
        ),
        -- Calculate the shortfall
        Shortfall AS (
            SELECT
                SUM(TargetCount - AdjustedTarget) AS TotalShortfall
            FROM CategoryAllocation
            WHERE TargetCount > AdjustedTarget
        ),
        -- Calculate excess capacity for redistribution
        ExcessCapacity AS (
            SELECT
                ca.Category_ID,
                ca.AdjustedTarget AS BaseAllocation,
                CASE
                    WHEN ca.TotalCount > ca.AdjustedTarget THEN ca.TotalCount - ca.AdjustedTarget
                    ELSE 0
                END AS ExcessCapacity
            FROM CategoryAllocation ca
        ),
        TotalExcessCapacity AS (
            SELECT SUM(ExcessCapacity) AS TotalExcess FROM ExcessCapacity
        ),
        -- Final allocation with redistribution
        FinalCategoryAllocation AS (
            SELECT
                ec.Category_ID,
                ec.BaseAllocation + 
                    CASE
                        WHEN (SELECT TotalExcess FROM TotalExcessCapacity) > 0 AND (SELECT TotalShortfall FROM Shortfall) > 0
                        THEN CAST(ec.ExcessCapacity * (SELECT TotalShortfall FROM Shortfall) / 
                                (SELECT TotalExcess FROM TotalExcessCapacity) AS INT)
                        ELSE 0
                    END AS FinalAllocation
            FROM ExcessCapacity ec
        )
        -- Final selection with proper order
        SELECT * FROM (
            SELECT 
                a.News_Feed_ID, 
                a.Title, 
                a.URL, 
                a.Category_ID, 
                a.Source_Count,
                CASE WHEN a.Source_Count > 1 THEN 'TopSource' ELSE 'Remaining' END AS SourceType
            FROM AllSources a
            JOIN FinalCategoryAllocation fca ON a.Category_ID = fca.Category_ID
            WHERE a.RowNum <= fca.FinalAllocation
        ) AS Combined
        --order by Category_ID, Source_Count
        ORDER BY NEWID();
        """
        
        try:
            if not self.conn and not self.connect():
                return None
                
            return pd.read_sql(query, self.conn)
            
        except Exception as e:
            logger.error(f"Error retrieving news feed: {e}")
            return None
    
    def update_news_feed_bluesky(self, news_feed_id: int, article_text: str, bsky_tweet: str, 
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
            logger.info(f"Successfully updated database for BlueSky post - news_feed_id: {news_feed_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating news feed for BlueSky: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False
    
    def update_news_feed_twitter(self, news_feed_id: int, article_text: str, twitter_tweet: str, 
                          article_url: str, article_img: str) -> bool:
        """
        Update a news feed entry after posting to Twitter.
        
        Args:
            news_feed_id: The ID of the news feed item in the database.
            article_text: The full text of the article.
            twitter_tweet: The tweet text posted to Twitter.
            article_url: The URL of the article.
            article_img: The URL of the article's image.
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        query = """
        UPDATE [dbo].[tbl_News_Feed]
        SET [Article_Text] = ?,
            [Used_In_Twitter] = 1,
            [Twitter_Tweet] = ?,
            [Article_URL] = ?,
            [Article_Img] = ?
        WHERE [News_Feed_ID] = ?
        """
        
        if not self.conn and not self.connect():
            return False
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (article_text, twitter_tweet, article_url, article_img, news_feed_id))
            self.conn.commit()
            logger.info(f"Successfully updated database for Twitter post - news_feed_id: {news_feed_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating news feed for Twitter: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False
    
    def update_news_feed(self, news_feed_id: int, article_text: str, social_text: str, 
                         article_url: str, article_img: str, platform: str = "bluesky") -> bool:
        """
        Update a news feed entry after posting to social media.
        
        Args:
            news_feed_id: The ID of the news feed item in the database.
            article_text: The full text of the article.
            social_text: The text posted to social media.
            article_url: The URL of the article.
            article_img: The URL of the article's image.
            platform: The social media platform ("bluesky" or "twitter").
            
        Returns:
            bool: True if update was successful, False otherwise.
        """
        if platform.lower() == "twitter":
            return self.update_news_feed_twitter(news_feed_id, article_text, social_text, article_url, article_img)
        else:
            return self.update_news_feed_bluesky(news_feed_id, article_text, social_text, article_url, article_img)

# Create a default database instance for use throughout the application
db = DatabaseConnection()