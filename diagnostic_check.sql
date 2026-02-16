-- Diagnostic query to check why get_news_feed() returns no results

USE [NewsAnalysis]
GO

-- Check 1: Total records in tbl_News_Feed
SELECT 'Total Records' AS CheckType, COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed];

-- Check 2: Records by Language_ID
SELECT 'By Language' AS CheckType, Language_ID, COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
GROUP BY Language_ID
ORDER BY Count DESC;

-- Check 3: Records by Category_ID
SELECT 'By Category' AS CheckType, Category_ID, COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
GROUP BY Category_ID
ORDER BY Category_ID;

-- Check 4: Records by Published_Date (last 7 days)
SELECT 'By Publish Date' AS CheckType,
       CAST(Published_Date AS DATE) AS PublishDate,
       COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -7, GETDATE())
GROUP BY CAST(Published_Date AS DATE)
ORDER BY PublishDate DESC;

-- Check 5: Records by Used_In_BSky and Used_In_Twitter
SELECT 'By Used Status' AS CheckType,
       Used_In_BSky,
       Used_In_Twitter,
       COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0
GROUP BY Used_In_BSky, Used_In_Twitter;

-- Check 6: Full filter check (what the app is looking for)
SELECT 'Matches Full Filter' AS CheckType, COUNT(*) AS Count
FROM [dbo].[tbl_News_Feed]
WHERE Language_ID = 23
  AND (Category_ID = 1 OR Category_ID = 2 OR Category_ID = 3)
  AND Published_Date >= DATEADD(day, -1, GETDATE())
  AND Source_Count > 0
  AND Used_In_BSky = 0
  AND Used_In_Twitter = 0;

-- Check 7: Sample of recent records
SELECT TOP 10
    News_Feed_ID,
    Title,
    Published_Date,
    Language_ID,
    Category_ID,
    Source_Count,
    Used_In_BSky,
    Used_In_Twitter
FROM [dbo].[tbl_News_Feed]
ORDER BY Published_Date DESC;
