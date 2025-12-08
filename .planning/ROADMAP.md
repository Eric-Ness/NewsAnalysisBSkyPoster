# NewsAnalysisBSkyPoster - Roadmap

## Milestone: v1.1 - Code Quality & Maintainability

Focus: Clean up technical debt, improve code structure, add safety nets.

---

### Phase 01: Configuration Cleanup
**Status:** Not Started
**Goal:** Centralize magic numbers and improve configurability

**Scope:**
- Extract hardcoded values to settings.py (article limits, char limits, timeouts)
- Add configuration validation on startup
- Document all configuration options

**Files:** `config/settings.py`, `main.py`, `services/*.py`

---

### Phase 02: Error Handling Standardization
**Status:** Not Started
**Goal:** Consistent error handling and logging across all services

**Scope:**
- Audit all try/except blocks for silent failures
- Create custom exception classes for different failure types
- Standardize logging format and levels
- Add correlation IDs for tracing request flow

**Files:** `utils/exceptions.py` (new), all service files

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
**Status:** In Progress (migration script created)
**Goal:** Complete the social posts storage feature

**Scope:**
- Run migration on production database
- Verify post storage working end-to-end
- Add engagement metrics update function (for future use)

**Files:** `migrations/001_create_social_posts_table.sql`, `data/database.py`

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
|-------|--------|---------|-----------|
| 01 - Configuration | Not Started | - | - |
| 02 - Error Handling | Not Started | - | - |
| 03 - Service Abstraction | Not Started | - | - |
| 04 - Testing | Not Started | - | - |
| 05 - DB Migration | In Progress | 2024-12-08 | - |
| 06 - Retry Logic | Not Started | - | - |
| 07 - Monitoring | Not Started | - | - |
| 08 - Embed Rendering | Not Started | - | - |
| 09 - Analytics | Not Started | - | - |
