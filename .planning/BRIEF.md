# NewsAnalysisBSkyPoster - Project Brief

## Vision

An automated news curation and social media posting system that intelligently selects newsworthy articles and posts them to BlueSky and Twitter with AI-generated summaries.

## Current State (Working Application)

The application is **production-ready and operational**. Core functionality:

- Fetches news candidates from MSSQL database (160 articles, weighted by category)
- AI-powered article selection via Google Gemini (ranks 60 candidates, returns top 30)
- Content extraction with paywall detection (newspaper3k + Selenium fallback)
- Similarity checking against recent posts (keyword + AI semantic check)
- AI-generated social posts (<260 chars) with hashtags
- Dual-platform posting: BlueSky (AT Protocol) and Twitter (Tweepy)
- Database tracking of posted articles and social post metadata

### Recent Addition (In Progress)
- `tbl_Social_Posts` table for storing full post data (for future embed rendering)
- Migration script at `migrations/001_create_social_posts_table.sql`
- Services updated to capture and store post IDs, URIs, author info

## Architecture

```
main.py (NewsPoster orchestrator)
    ├── data/database.py          # MSSQL via pyodbc
    ├── services/
    │   ├── ai_service.py         # Gemini AI integration
    │   ├── article_service.py    # Content extraction
    │   ├── social_service.py     # BlueSky/AT Protocol
    │   └── twitter_service.py    # Twitter/X
    ├── config/settings.py        # Environment config
    └── utils/logger.py           # Logging
```

## Known Issues / Technical Debt

### Code Smells to Address
1. **Duplicate code patterns** - Twitter and BlueSky services have similar structure
2. **Mixed concerns** - Some services do too much (fetch + process + post)
3. **Error handling inconsistency** - Some places swallow exceptions silently
4. **Magic numbers** - Hardcoded values (160 articles, 260 chars, etc.)
5. **Test coverage** - No automated tests currently

### Improvement Opportunities
1. **Configuration** - Move magic numbers to settings.py
2. **Abstraction** - Create base SocialService class
3. **Retry logic** - More robust API failure handling
4. **Monitoring** - Add metrics/observability
5. **Embed rendering** - Use stored posts to render embeds on external sites

## Success Metrics

- Application runs reliably without manual intervention
- Code is maintainable and easy to extend
- New platforms can be added with minimal duplication
- Clear separation of concerns
- Automated tests catch regressions

## Constraints

- MSSQL database (existing infrastructure)
- Python ecosystem
- Must maintain backward compatibility with existing database schema
- Zero-downtime changes preferred

## Owner

Solo developer project - plan for autonomous Claude execution with human verification checkpoints.
