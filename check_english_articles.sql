-- Check for recent English articles specifically

USE [NewsAnalysis]
GO

-- Find most recent English articles (Language_ID = 23)
SELECT TOP 20
    News_Feed_ID,
    Title,
    Published_Date,
    Category_ID,
    Source_Count,
    Used_In_BSky,
    Used_In_Twitter,
    DATEDIFF(hour, Published_Date, GETDATE()) AS HoursOld
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
ORDER BY Published_Date DESC;

-- Count of English articles in last 24 hours by Used status
SELECT
    'Last 24 Hours' AS TimeFrame,
    Used_In_BSky,
    Used_In_Twitter,
    COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
GROUP BY Used_In_BSky, Used_In_Twitter;

-- Count of English articles with Source_Count > 0 in last 24 hours
SELECT
    'With Source_Count > 0' AS CheckType,
    COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0;

-- Show breakdown by each filter
SELECT 'Total English (Lang 23)' AS FilterStep, COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23

UNION ALL

SELECT 'After Category Filter (1/2/3)', COUNT(*)
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)

UNION ALL

SELECT 'After Published_Date (last 24h)', COUNT(*)
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())

UNION ALL

SELECT 'After Source_Count > 0', COUNT(*)
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0

UNION ALL

SELECT 'After Used_In_BSky = 0', COUNT(*)
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0
  AND Used_In_BSky = 0

UNION ALL

SELECT 'Final (All Filters)', COUNT(*)
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0
  AND Used_In_BSky = 0
  AND Used_In_Twitter = 0;
