-- Migration: Create tbl_BlueSky_Daily_Metrics table for tracking daily BlueSky account metrics
-- Purpose: Store daily snapshots of BlueSky account stats (followers, posts, engagement, etc.)
-- Database: NewsAnalysis (MSSQL)
-- Date: 2026

USE [NewsAnalysis]
GO

-- Create the BlueSky Daily Metrics table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tbl_BlueSky_Daily_Metrics')
BEGIN
    CREATE TABLE [dbo].[tbl_BlueSky_Daily_Metrics] (
        -- Primary Key
        [Metric_ID]             INT IDENTITY(1,1) NOT NULL,

        -- Snapshot Date
        [Snapshot_Date]         DATE NOT NULL,                      -- The date this snapshot represents

        -- Account Metrics
        [Follower_Count]        INT NULL DEFAULT 0,                 -- Total followers as of this date
        [Following_Count]       INT NULL DEFAULT 0,                 -- Total accounts followed as of this date
        [Total_Posts_Count]     INT NULL DEFAULT 0,                 -- Total posts on the account as of this date

        -- Daily Activity
        [Stories_Posted]        INT NULL DEFAULT 0,                 -- Number of stories posted by the app on this date
        [Stories_Skipped]       INT NULL DEFAULT 0,                 -- Number of stories skipped (already posted, filtered, etc.)

        -- Daily Engagement (aggregated for posts made on this date)
        [Daily_Likes]           INT NULL DEFAULT 0,                 -- Total likes received on this date
        [Daily_Reposts]         INT NULL DEFAULT 0,                 -- Total reposts received on this date
        [Daily_Replies]         INT NULL DEFAULT 0,                 -- Total replies received on this date
        [Daily_Quotes]          INT NULL DEFAULT 0,                 -- Total quotes received on this date
        [Daily_Impressions]     INT NULL DEFAULT 0,                 -- Total impressions on this date (if available)

        -- Growth (computed or populated by app)
        [New_Followers]         INT NULL DEFAULT 0,                 -- Net new followers gained on this date
        [New_Unfollowers]       INT NULL DEFAULT 0,                 -- Followers lost on this date

        -- Audit
        [Created_At]            DATETIME2 NOT NULL DEFAULT GETDATE(),
        [Updated_At]            DATETIME2 NOT NULL DEFAULT GETDATE(),

        -- Constraints
        CONSTRAINT [PK_tbl_BlueSky_Daily_Metrics] PRIMARY KEY CLUSTERED ([Metric_ID] ASC),
        CONSTRAINT [UQ_BlueSky_Daily_Metrics_Date] UNIQUE ([Snapshot_Date])
    );

    -- Create indexes for common queries
    CREATE NONCLUSTERED INDEX [IX_BlueSky_Daily_Metrics_Snapshot_Date]
        ON [dbo].[tbl_BlueSky_Daily_Metrics] ([Snapshot_Date] DESC);

    PRINT 'Table tbl_BlueSky_Daily_Metrics created successfully.';
END
ELSE
BEGIN
    PRINT 'Table tbl_BlueSky_Daily_Metrics already exists.';
END
GO
