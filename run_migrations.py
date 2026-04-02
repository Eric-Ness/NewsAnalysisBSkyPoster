"""Run database migrations for YouTube posting feature."""

import pyodbc
from config import settings


def run_migration_003():
    """Add Used_In_BSky column to tbl_YouTube_Video in YouTube database."""
    print("=== Migration 003: YouTube Database ===")
    conn = pyodbc.connect(settings.YOUTUBE_DB_CONNECTION_STRING)
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute(
        "SELECT 1 FROM sys.columns "
        "WHERE object_id = OBJECT_ID(N'[dbo].[tbl_YouTube_Video]') "
        "AND name = 'Used_In_BSky'"
    )
    if cursor.fetchone():
        print("Used_In_BSky column already exists, skipping.")
    else:
        cursor.execute(
            "ALTER TABLE [dbo].[tbl_YouTube_Video] "
            "ADD [Used_In_BSky] BIT NOT NULL "
            "CONSTRAINT [DF_YouTube_Video_Used_In_BSky] DEFAULT 0"
        )
        conn.commit()
        print("Added Used_In_BSky column to tbl_YouTube_Video.")

    # Check if index exists
    cursor.execute(
        "SELECT 1 FROM sys.indexes "
        "WHERE object_id = OBJECT_ID(N'[dbo].[tbl_YouTube_Video]') "
        "AND name = 'IX_YouTube_Video_Used_In_BSky'"
    )
    if cursor.fetchone():
        print("IX_YouTube_Video_Used_In_BSky index already exists, skipping.")
    else:
        cursor.execute(
            "CREATE NONCLUSTERED INDEX [IX_YouTube_Video_Used_In_BSky] "
            "ON [dbo].[tbl_YouTube_Video] ([Used_In_BSky], [Is_Short], [Is_Live], [Published_Date]) "
            "INCLUDE ([YouTube_Video_Key], [Title], [Thumbnail_URL], [View_Count], "
            "[Like_Count], [Comment_Count], [Duration_Seconds], [YouTube_Channel_ID])"
        )
        conn.commit()
        print("Created IX_YouTube_Video_Used_In_BSky index.")

    conn.close()
    print("Migration 003 complete.\n")


def run_migration_004():
    """Add YouTube_Video_ID column to tbl_Social_Posts in NewsAnalysis database."""
    print("=== Migration 004: NewsAnalysis Database ===")
    conn = pyodbc.connect(settings.DB_CONNECTION_STRING)
    conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute(
        "SELECT 1 FROM sys.columns "
        "WHERE object_id = OBJECT_ID(N'[dbo].[tbl_Social_Posts]') "
        "AND name = 'YouTube_Video_ID'"
    )
    if cursor.fetchone():
        print("YouTube_Video_ID column already exists, skipping.")
    else:
        cursor.execute(
            "ALTER TABLE [dbo].[tbl_Social_Posts] "
            "ADD [YouTube_Video_ID] INT NULL"
        )
        conn.commit()
        print("Added YouTube_Video_ID column to tbl_Social_Posts.")

    # Check if index exists
    cursor.execute(
        "SELECT 1 FROM sys.indexes "
        "WHERE object_id = OBJECT_ID(N'[dbo].[tbl_Social_Posts]') "
        "AND name = 'IX_Social_Posts_YouTube_Video_ID'"
    )
    if cursor.fetchone():
        print("IX_Social_Posts_YouTube_Video_ID index already exists, skipping.")
    else:
        cursor.execute(
            "CREATE NONCLUSTERED INDEX [IX_Social_Posts_YouTube_Video_ID] "
            "ON [dbo].[tbl_Social_Posts] ([YouTube_Video_ID]) "
            "WHERE [YouTube_Video_ID] IS NOT NULL"
        )
        conn.commit()
        print("Created IX_Social_Posts_YouTube_Video_ID filtered index.")

    conn.close()
    print("Migration 004 complete.\n")


if __name__ == "__main__":
    run_migration_003()
    run_migration_004()
    print("All migrations applied successfully!")
