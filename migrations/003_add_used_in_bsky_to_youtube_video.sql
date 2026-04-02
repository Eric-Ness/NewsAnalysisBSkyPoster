-- Migration 003: Add Used_In_BSky column to tbl_YouTube_Video
-- Database: [NewsAnalysis.YouTube]
-- Purpose: Track which YouTube videos have been posted to BlueSky
-- Date: 2026-03-31

USE [NewsAnalysis.YouTube]
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.columns
    WHERE object_id = OBJECT_ID(N'[dbo].[tbl_YouTube_Video]')
    AND name = 'Used_In_BSky'
)
BEGIN
    ALTER TABLE [dbo].[tbl_YouTube_Video]
    ADD [Used_In_BSky] BIT NOT NULL CONSTRAINT [DF_YouTube_Video_Used_In_BSky] DEFAULT 0;

    PRINT 'Added Used_In_BSky column to tbl_YouTube_Video.';
END
GO

-- Index for efficient candidate queries (filter by Used_In_BSky = 0)
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'[dbo].[tbl_YouTube_Video]')
    AND name = 'IX_YouTube_Video_Used_In_BSky'
)
BEGIN
    CREATE NONCLUSTERED INDEX [IX_YouTube_Video_Used_In_BSky]
        ON [dbo].[tbl_YouTube_Video] ([Used_In_BSky], [Is_Short], [Is_Live], [Published_Date])
        INCLUDE ([YouTube_Video_Key], [Title], [Thumbnail_URL], [View_Count], [Like_Count], [Comment_Count], [Duration_Seconds], [YouTube_Channel_ID]);

    PRINT 'Created IX_YouTube_Video_Used_In_BSky index.';
END
GO
