# News Poster

A Python application that automatically selects and posts newsworthy articles and YouTube videos to BlueSky (AT Protocol). Supports multi-provider AI fallback (Gemini + Arli AI) and ships with a WAF-bypass HTTP transport for BlueSky's edge restrictions.

## Overview

News Poster automates the selection, processing, and posting of news content to BlueSky. Two entry points run on independent schedules:

- **`main.py`** — picks the most newsworthy article from a candidate pool, fetches its content, generates a social media post, and publishes it
- **`youtube_poster.py`** — picks a newsworthy video from a YouTube candidate pool (with channel quality tiers) and publishes it

Both flows share the same AI service, BlueSky integration, and post-storage logic.

## Features

### Content selection

- **AI-powered article + video selection** using Google Gemini, with **Arli AI (Mistral/Qwen) as fallback** when Gemini fails or 503s
- **Content similarity detection** — skips posts too similar to recent posts
- **PR/promotional title filtering** — pattern-based exclusion of corporate PR, gaming announcements, deal roundups
- **Paywall + bot-block detection** — skips paywalled URLs and publishers that 403 our crawler
- **URL history tracking** — avoids duplicates across runs
- **YouTube channel quality tiers** — 4-tier system (wire services → state propaganda) with per-tier per-channel caps that limit opinion-heavy channels' share of the pool

### AI provider fallback

- **Multi-provider chain** — Gemini 2.5 (lite → flash) → Arli AI (Mistral), configurable via `AI_PRIMARY_PROVIDER`
- **Hybrid routing** — article/video selection always uses Gemini first (Mistral truncates large structured outputs); similarity check and tweet generation honor the primary-provider setting
- **Thinking-budget control** — disable Gemini's invisible chain-of-thought reasoning via `GEMINI_THINKING_BUDGET=0` to reduce output token costs

### Reliability + infrastructure

- **BlueSky WAF bypass** — uses `curl_cffi` (Chrome impersonation) instead of Python's stdlib TLS, which BlueSky's AWS WAF blocks
- **Multi-platform posting** — BlueSky and optional Twitter
- **Social post storage** — `tbl_Social_Posts` captures everything needed for external embed rendering
- **Daily metrics** — follower count, post count, engagement stored per day in `tbl_BlueSky_Daily_Metrics`

## Project Structure

```text
news-poster/
├── config/
│   ├── domain_lists.py        # Paywall/blocked domains, PR title patterns
│   ├── settings.py            # Centralized configuration
│   └── validators.py          # Config validation logic
├── data/
│   ├── database.py            # Primary DB (NewsAnalysis) operations
│   ├── youtube_database.py    # YouTube DB (NewsAnalysis.YouTube) operations
│   ├── models.py              # Dataclasses (article candidates, post data, metrics)
│   └── protocols.py           # Storage protocol interfaces (for DI)
├── migrations/
│   ├── 001_create_social_posts_table.sql
│   ├── 002_create_bluesky_daily_metrics_table.sql
│   ├── 003_add_used_in_bsky_to_youtube_video.sql
│   └── 004_add_youtube_video_id_to_social_posts.sql
├── services/
│   ├── article_service.py     # Article fetching and content extraction
│   ├── ai_service.py          # Multi-provider AI (Gemini + Arli fallback)
│   ├── social_service.py      # BlueSky (AT Protocol) integration
│   ├── twitter_service.py     # Twitter API integration
│   ├── youtube_service.py     # YouTube candidate management + channel tiers
│   └── protocols.py           # Service protocol interfaces
├── utils/
│   ├── atproto_transport.py   # curl_cffi monkey-patch for BlueSky WAF bypass
│   ├── logger.py              # Centralized logging
│   ├── helpers.py             # Helper functions
│   └── exceptions.py          # Custom exception classes
├── tests/                     # 226 tests covering all services
├── main.py                    # News article posting entry point
├── youtube_poster.py          # YouTube video posting entry point
├── run_migrations.py          # Database migration runner
├── .env.example               # Environment variables template
└── README.md
```

## Installation

1. Clone the repository:

   ```sh
   git clone <repository-url>
   cd news-poster
   ```

2. Create a virtual environment and install dependencies:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration (see `.env.example` for template)

4. Run database migrations:

   ```sh
   python run_migrations.py
   ```

## Usage

### News article posting

```sh
python main.py
```

Command-line arguments:

- `--test` — dry-run mode, no posts published
- `--log-file FILE` — custom log file path (default: `news_poster.log`)
- `--log-level LEVEL` — `DEBUG`, `INFO`, `WARNING`, `ERROR`

### YouTube video posting

```sh
python youtube_poster.py
```

Same `--test`, `--log-file`, `--log-level`, plus `--max-posts N`.

Both are typically run on a scheduler (Windows Task Scheduler or cron) — news ~every 20 min, YouTube hourly.

## Dependencies

- Python 3.8+
- `google-genai` — Gemini API client
- `openai` — Used for Arli AI (OpenAI-compatible API)
- `curl_cffi` — Browser-fingerprint TLS for BlueSky WAF bypass
- `atproto` — BlueSky AT Protocol client
- `tweepy` — Twitter API client
- `newspaper3k` — Article extraction
- `selenium` + `webdriver-manager` — Google News redirect resolution
- `pyodbc`, `pandas` — SQL Server connectivity + data handling

## Configuration

Copy `.env.example` to `.env` and fill in values:

### Database (SQL Server)

- `server`, `db`, `user`, `pwd` — primary `NewsAnalysis` DB connection
- `YOUTUBE_DB_NAME` — defaults to `NewsAnalysis.YouTube`

### AI providers

- `GOOGLE_AI_API_KEY` — Google Gemini API key
- `ARLI_API_KEY`, `ARLI_BASE_URL`, `ARLI_MODEL` — Arli AI (OpenAI-compatible) fallback
- `AI_PRIMARY_PROVIDER` — `gemini` (default) or `arli` — which provider runs first
- `GEMINI_THINKING_BUDGET` — `0` (default, disables thinking for cost control), `-1` (Google default), or a positive token count

### BlueSky / Twitter

- `AT_PROTOCOL_USERNAME`, `AT_PROTOCOL_PASSWORD` — BlueSky credentials (app password recommended)
- `TWITTER_API_KEY`, `TWITTER_API_KEY_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` — Twitter OAuth 1.0a
- `TWITTER_BEARER_TOKEN` — optional OAuth 2.0 bearer token
- `ENABLE_BLUESKY`, `ENABLE_TWITTER` — toggle platforms on/off
- `ENABLE_YOUTUBE_POSTING` — toggle YouTube poster

## Database Schema

Tables in `NewsAnalysis`:

- **`tbl_News_Feed`** — news article candidates and processing status (populated by an external ingestion job)
- **`tbl_Social_Posts`** — full record of every post made, including facets, author info, link card data, and platform IDs — used for external embed rendering
- **`tbl_BlueSky_Daily_Metrics`** — daily snapshots of follower count, post count, engagement totals

Tables in `NewsAnalysis.YouTube`:

- **`tbl_YouTube_Video`** — video candidates (title, description, view/like/comment counts, duration)
- **`tbl_YouTube_Channel`** — channel metadata used by the tier classification system

## Testing

```sh
python -m pytest
```

226 tests cover all services, including AI provider fallback, channel tier resolution, content filtering, and database operations.

## Change Log

- **2026.06.25** – Disabled Gemini chain-of-thought reasoning by default (`GEMINI_THINKING_BUDGET=0`) — invisible "thinking" tokens were inflating output token charges on `gemini-2.5-flash` fallback calls (~$0.50–$1.20/day).
- **2026.06.23** – Hybrid AI routing: article + video selection always route to Gemini first regardless of `AI_PRIMARY_PROVIDER` (Mistral consistently truncates the large structured output).
- **2026.06.22** – Added `AI_PRIMARY_PROVIDER` env toggle to flip which AI provider runs first; bumped `ARLI_MAX_TOKENS` to 5000 for larger structured outputs.
- **2026.06.18** – Multi-provider AI fallback: added Arli AI (OpenAI-compatible API, Mistral/Qwen) as final fallback after all Gemini models fail.
- **2026.06.08** – Extended PR-title filter with gaming-industry patterns: launches, platform reveals, DLC/Season Pass drops, Xbox/PlayStation/Nintendo showcases, gameplay trailers.
- **2026.05.17** – Bypassed BlueSky's TLS-fingerprint WAF block by replacing atproto's `httpx` client with `curl_cffi` (Chrome 131 impersonation).
- **2026.04.23** – Tier-weighted YouTube channel quality system: 4 tiers (wire services → state propaganda) with per-tier per-channel caps; pruned deprecated Gemini 2.0 models from the fallback chain.
- **2026.04.11** – Filter non-English YouTube video titles and descriptions.
- **2026.04.03** – Increased YouTube candidate selection limit to allow better filter headroom.
- **2026.04.02** – YouTube video posting feature added (`youtube_poster.py`); per-channel diversity cap; principle-based opinion-title filter; refined social-post prompt for originality; tuned similarity thresholds.
- **2026.03.01** – Reduced BlueSky posting failures from ~9.3% to ~5% via improved error handling and retry behavior.
- **2026.02.01** – Migrated from deprecated `google.generativeai` to `google.genai`; added Twitter platform enable/disable config.
- **2026.01.27** – Implemented dependency injection for better testability: added Protocol interfaces, refactored all services for constructor injection, added MockPostStorage for testing.
- **2026.01.27** – Added URL validation and sanitization to prevent SSRF attacks.
- **2026.01.26** – Refactored large configuration and database files for better maintainability.
- **2026.01.26** – Added comprehensive test coverage for all services (151 tests).
- **2026.01.08** – Improved AI article selection: added domain blocklist for religious/fake news/biased sites, pre-filter .gov/.mil URLs, pass Source_Count to AI for breaking news prioritization.
- **2025.12.18** – Configuration cleanup: extracted magic numbers to settings.py, added config validation, created custom exception classes.
- **2025.12.08** – Added social posts storage for embed support (`tbl_Social_Posts` table).
- **2025.09.25** – Updated Gemini Models List.
- **2025.08.05** – feat: Add PR Newswire to paywall domains list and increase total results in SQL query.
- **2025.07.06** – Blacklisted a couple of sites and trying to avoid sales articles like Amazon Prime Day.
- **2025.04.21** – Updated data retrieval – world news 50%, national 40%, business 10%.
- **2025.04.19** – Re-added hashtag creation.
- **2025.04.18** – Bug fix for paywalled sites. Added government sites to block.
- **2025.04.14** – Major restructure, no longer a monolith py file.
- **2025.04.13** – Keep track of bsky posts, extracted article text, and pertinent URLs.
- **2025.04.11** – Increased amount of news LLM could choose from 120 to 160 news items.
- **2025.04.10** – Added business news to the data feed.
