import db
import pandas as pd

def get_news_feed_data():
    """Fetch news feed data from the database.

    Returns:
        list: A list of tuples containing the URL and Title of the news feed items.
              Each tuple represents a row of data from the database.

    Raises:
        Exception: If there is an error fetching the news feed data from the database.
    """
    cursor = db.conn.cursor()

    query = '''
    WITH TopSources AS (
        -- Get all items with the highest Source_Count value
        SELECT URL, Title, Source_Count
        FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
        WHERE Language_ID = 23
        AND (Category_ID = 2 OR Category_ID = 1)
        AND [Published_Date] >= DATEADD(day, -1, GETDATE())
        AND Source_Count > 1
    ),
    RemainingItems AS (
        -- Get items that don't have the highest Source_Count
        SELECT URL, Title, Source_Count
        FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
        WHERE Language_ID = 23
        AND (Category_ID = 2 OR Category_ID = 1)
        AND [Published_Date] >= DATEADD(day, -1, GETDATE())
        AND Source_Count > 0
        AND Source_Count < (
            SELECT MAX(Source_Count)
            FROM [NewsAnalysis].[dbo].[tbl_News_Feed]
            WHERE Language_ID = 23
            AND (Category_ID = 2 OR Category_ID = 1)
            AND [Published_Date] >= DATEADD(day, -1, GETDATE())
            AND Source_Count > 0
        )
    )
    -- Combine the two sets with top items first, then random selection from remaining
    SELECT * FROM (
        SELECT URL, Title
        FROM TopSources
        UNION ALL
        SELECT TOP(120 - (SELECT COUNT(*) FROM TopSources)) URL, Title
        FROM RemainingItems
        ORDER BY NEWID()
    ) AS Combined
    ORDER BY  NEWID();
    '''
    
    try:
        cursor.execute(query)
        
        # Get column names from cursor description
        columns = [column[0] for column in cursor.description]
        
        # Fetch all results
        results = cursor.fetchall()
        
        print(f"Retrieved {len(results)} rows from the database")
        if results:
            print(f"Sample row: {results[0]}")
            print(f"Columns: {columns}")
        
        return results

    except Exception as e:
        print(f"Error fetching news feed data: {e}")
        return None
    finally:
        cursor.close()

# For testing
if __name__ == "__main__":
    news = get_news_feed_data()
    if news:
        print(f"\nTotal articles: {len(news)}")
        print(f"First article: {news[0]}")