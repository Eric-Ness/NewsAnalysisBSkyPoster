-- Migration 004: Add YouTube_Video_ID column to tbl_Social_Posts
-- Database: [NewsAnalysis]
-- Purpose: Link social posts to YouTube videos (cross-database logical reference)
-- Date: 2026-03-31

USE [NewsAnalysis]
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID(N'[dbo].[tbl_Social_Posts]')
    AND name = 'YouTube_Video_ID'
)
BEGIN
    ALTER TABLE [dbo].[tbl_Social_Posts]
    ADD [YouTube_Video_ID] INT NULL;

    PRINT 'Added YouTube_Video_ID column to tbl_Social_Posts.';
END
GO

-- Index for querying social posts by YouTube video
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'[dbo].[tbl_Social_Posts]')
    AND name = 'IX_Social_Posts_YouTube_Video_ID'
)
BEGIN
    CREATE NONCLUSTERED INDEX [IX_Social_Posts_YouTube_Video_ID]
        ON [dbo].[tbl_Social_Posts] ([YouTube_Video_ID])
        WHERE [YouTube_Video_ID] IS NOT NULL;

    PRINT 'Created IX_Social_Posts_YouTube_Video_ID filtered index.';
END
GO
