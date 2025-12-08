-- Migration: Create tbl_Social_Posts table for storing social media post data
-- Purpose: Enable embedding/reproducing posts on third-party websites
-- Database: NewsAnalysis (MSSQL)
-- Date: 2024

USE [NewsAnalysis]
GO

-- Create the Social Posts table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tbl_Social_Posts')
BEGIN
    CREATE TABLE [dbo].[tbl_Social_Posts] (
        -- Primary Key
        [Social_Post_ID]        INT IDENTITY(1,1) NOT NULL,

        -- Platform Identification
        [Platform]              NVARCHAR(20) NOT NULL,          -- 'bluesky' or 'twitter'
        [Post_ID]               NVARCHAR(255) NOT NULL,         -- Platform's unique post ID
        [Post_URI]              NVARCHAR(500) NULL,             -- Full URI (BlueSky uses at:// URIs)
        [Post_URL]              NVARCHAR(500) NULL,             -- Direct web URL to the post

        -- Author Information (for embedding)
        [Author_Handle]         NVARCHAR(100) NOT NULL,         -- @handle
        [Author_Display_Name]   NVARCHAR(200) NULL,             -- Display name
        [Author_Avatar_URL]     NVARCHAR(500) NULL,             -- Profile picture URL
        [Author_DID]            NVARCHAR(255) NULL,             -- BlueSky DID (decentralized identifier)

        -- Post Content
        [Post_Text]             NVARCHAR(MAX) NOT NULL,         -- The actual post text
        [Post_Facets]           NVARCHAR(MAX) NULL,             -- JSON: Rich text facets (hashtags, mentions, links)

        -- Link Card / Embed Data
        [Article_URL]           NVARCHAR(500) NULL,             -- External link URL
        [Article_Title]         NVARCHAR(500) NULL,             -- Link card title
        [Article_Description]   NVARCHAR(1000) NULL,            -- Link card description
        [Article_Image_URL]     NVARCHAR(500) NULL,             -- Link card thumbnail
        [Article_Image_Blob]    NVARCHAR(255) NULL,             -- BlueSky blob reference for uploaded image

        -- Timestamps
        [Created_At]            DATETIME2 NOT NULL,             -- When post was created on platform
        [Indexed_At]            DATETIME2 NULL,                 -- When platform indexed the post
        [Stored_At]             DATETIME2 NOT NULL DEFAULT GETDATE(), -- When we stored this record

        -- Engagement Metrics (can be updated periodically)
        [Like_Count]            INT NULL DEFAULT 0,
        [Repost_Count]          INT NULL DEFAULT 0,
        [Reply_Count]           INT NULL DEFAULT 0,
        [Quote_Count]           INT NULL DEFAULT 0,
        [Metrics_Updated_At]    DATETIME2 NULL,                 -- Last time metrics were fetched

        -- Relationship to News Feed
        [News_Feed_ID]          INT NULL,                       -- FK to tbl_News_Feed (nullable for manual posts)

        -- Additional Metadata
        [Language]              NVARCHAR(10) NULL,              -- Language code (e.g., 'en')
        [Is_Reply]              BIT NOT NULL DEFAULT 0,         -- Is this a reply to another post?
        [Reply_To_Post_ID]      NVARCHAR(255) NULL,             -- Parent post ID if reply
        [Is_Repost]             BIT NOT NULL DEFAULT 0,         -- Is this a repost/retweet?
        [Raw_Response]          NVARCHAR(MAX) NULL,             -- JSON: Full API response for debugging

        -- Constraints
        CONSTRAINT [PK_tbl_Social_Posts] PRIMARY KEY CLUSTERED ([Social_Post_ID] ASC),
        CONSTRAINT [FK_tbl_Social_Posts_News_Feed] FOREIGN KEY ([News_Feed_ID])
            REFERENCES [dbo].[tbl_News_Feed] ([News_Feed_ID]),
        CONSTRAINT [UQ_Platform_PostID] UNIQUE ([Platform], [Post_ID])
    );

    -- Create indexes for common queries
    CREATE NONCLUSTERED INDEX [IX_Social_Posts_Platform]
        ON [dbo].[tbl_Social_Posts] ([Platform]);

    CREATE NONCLUSTERED INDEX [IX_Social_Posts_Created_At]
        ON [dbo].[tbl_Social_Posts] ([Created_At] DESC);

    CREATE NONCLUSTERED INDEX [IX_Social_Posts_News_Feed_ID]
        ON [dbo].[tbl_Social_Posts] ([News_Feed_ID]);

    CREATE NONCLUSTERED INDEX [IX_Social_Posts_Author_Handle]
        ON [dbo].[tbl_Social_Posts] ([Author_Handle]);

    PRINT 'Table tbl_Social_Posts created successfully.';
END
ELSE
BEGIN
    PRINT 'Table tbl_Social_Posts already exists.';
END
GO
