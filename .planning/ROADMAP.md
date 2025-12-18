# NewsAnalysisBSkyPoster - Roadmap

## Milestone: v1.1 - Code Quality & Maintainability

Focus: Clean up technical debt, improve code structure, add safety nets.

---

### Phase 01: Configuration Cleanup
**Status:** Complete
**Goal:** Centralize magic numbers and improve configurability

**Scope:**

- ✅ Extract hardcoded values to settings.py (article limits, char limits, timeouts)
- ✅ Add configuration validation on startup
- ✅ Document all configuration options with comments

**Files:** `config/settings.py`, `services/*.py`, `data/database.py`

**Settings Added:**
- Content Processing: `MIN_ARTICLE_WORD_COUNT`, `SUMMARY_TRUNCATE_LENGTH`, `SUMMARY_WORD_LIMIT`
- Selenium: `SELENIUM_REDIRECT_TIMEOUT`, `SELENIUM_PAGE_LOAD_TIMEOUT`, `XPATH_MIN_TEXT_LENGTH`
- AI Service: `SIMILARITY_CHECK_POSTS_LIMIT`, `MIN_KEYWORD_LENGTH`, `TITLE_SIMILARITY_THRESHOLD`, `AI_COMPARISON_TEXT_LENGTH`, `CANDIDATE_SELECTION_LIMIT`, `ARTICLE_TEXT_TRUNCATE_LENGTH`, `TWEET_CHARACTER_LIMIT`
- BlueSky: `BLUESKY_FETCH_LIMIT`, `BLUESKY_IMAGE_TIMEOUT`, `EMBED_DESCRIPTION_LENGTH`
- Twitter: `TWITTER_FETCH_LIMIT`, `TWITTER_API_MAX_RESULTS`, `TWITTER_URL_LENGTH`, `TWITTER_CHARACTER_LIMIT`, `TWEET_TRUNCATION_PADDING`, `TWITTER_IMAGE_TIMEOUT`
- Database: `DB_TOTAL_NEWS_FEED_RESULTS`, `DB_CAT1_ALLOCATION`, `DB_CAT2_ALLOCATION`

---

### Phase 02: Error Handling Standardization
**Status:** Complete
**Goal:** Consistent error handling and logging across all services

**Scope:**

- ✅ Audit all try/except blocks for silent failures
- ✅ Create custom exception classes for different failure types
- ✅ Fix bare `except:` clauses with proper logging
- ⬜ Add correlation IDs for tracing request flow (deferred)

**Files:** `utils/exceptions.py` (new), all service files

**Exceptions Created:**
- Base: `NewsPosterError`
- Configuration: `ConfigurationError`
- Article: `ArticleError`, `PaywallError`, `ArticleFetchError`, `ArticleParseError`, `InsufficientContentError`
- Social: `SocialMediaError`, `AuthenticationError`, `PostingError`, `RateLimitError`, `MediaUploadError`
- AI: `AIServiceError`, `DuplicateContentError`, `ArticleSelectionError`, `TweetGenerationError`
- Database: `DatabaseError`, `ConnectionError`, `QueryError`

---

### Phase 03: Service Abstraction
**Status:** Not Started
**Goal:** Reduce duplication between Twitter and BlueSky services

**Scope:**
- Create abstract `BaseSocialService` class
- Extract common patterns (post, get_recent, store_to_db)
- Refactor Twitter and BlueSky to inherit from base
- Simplify adding future platforms

**Files:** `services/base_social_service.py` (new), `services/social_service.py`, `services/twitter_service.py`

---

### Phase 04: Testing Foundation
**Status:** Not Started
**Goal:** Add automated tests for critical paths

**Scope:**
- Set up pytest infrastructure
- Add unit tests for AI service (mocked)
- Add unit tests for database operations
- Add integration test for posting flow (mocked APIs)

**Files:** `tests/` directory (new), `pytest.ini`, `requirements-dev.txt`

---

### Phase 05: Database Migration Completion
**Status:** Complete
**Goal:** Complete the social posts storage feature

**Scope:**

- ✅ Run migration on production database
- ✅ Verify post storage working end-to-end
- ⬜ Add engagement metrics update function (for future use) - deferred to Phase 08

**Files:** `migrations/001_create_social_posts_table.sql`, `data/database.py`

**Commit:** `76a6d73` - feat: Add social posts storage for embed support

---

## Milestone: v1.2 - Observability & Reliability

### Phase 06: Retry & Circuit Breaker
**Status:** Not Started
**Goal:** More resilient API interactions

**Scope:**
- Add retry decorator with exponential backoff
- Implement circuit breaker for external APIs
- Add health check endpoint

---

### Phase 07: Metrics & Monitoring
**Status:** Not Started
**Goal:** Visibility into application behavior

**Scope:**
- Add structured logging (JSON format option)
- Track key metrics (posts/day, failures, API latency)
- Optional: Prometheus metrics endpoint

---

## Milestone: v2.0 - New Features

### Phase 08: Embed Rendering System
**Status:** Not Started
**Goal:** Use stored posts to render embeds on external sites

**Scope:**
- API endpoint to fetch post data by ID
- HTML/CSS embed template generation
- oEmbed protocol support (optional)

---

### Phase 09: Analytics Dashboard
**Status:** Not Started
**Goal:** Visualize posting activity and engagement

**Scope:**
- Simple web dashboard showing recent posts
- Engagement metrics over time
- Category distribution charts

---

## Backlog (Unscheduled)

- [ ] Add Threads/Instagram support
- [ ] Scheduled posting (time-based)
- [ ] Manual post approval mode
- [ ] RSS feed output of posts
- [ ] Webhook notifications on post success/failure

---

## Progress Tracking

| Phase | Status | Started | Completed |
| ----- | ------ | ------- | --------- |
| 01 - Configuration | Complete | 2025-12-18 | 2025-12-18 |
| 02 - Error Handling | Complete | 2025-12-18 | 2025-12-18 |
| 03 - Service Abstraction | Not Started | - | - |
| 04 - Testing | Not Started | - | - |
| 05 - DB Migration | Complete | 2025-12-08 | 2025-12-08 |
| 06 - Retry Logic | Not Started | - | - |
| 07 - Monitoring | Not Started | - | - |
| 08 - Embed Rendering | Not Started | - | - |
| 09 - Analytics | Not Started | - | - |
