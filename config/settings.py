"""
Configuration Settings for News Poster

This module centralizes all configuration settings for the News Poster application,
including environment variables, API keys, and application constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Determine the application root directory
APP_ROOT = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
# Use override=True to ensure .env values take precedence over system environment variables
load_dotenv(dotenv_path=os.path.join(APP_ROOT, '.env'), override=True)

# API Keys and Authentication
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# AT Protocol (BlueSky) Authentication
AT_PROTOCOL_USERNAME = os.getenv("AT_PROTOCOL_USERNAME")
AT_PROTOCOL_PASSWORD = os.getenv("AT_PROTOCOL_PASSWORD")

# Twitter API Authentication
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Database Settings
DB_SERVER = os.getenv("server", "")
DB_NAME = os.getenv("db", "")
DB_USER = os.getenv("user", "")
DB_PASSWORD = os.getenv("pwd", "")

# Build connection string safely (validation happens in validate_settings())
DB_CONNECTION_STRING = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}}; "
    f"SERVER={DB_SERVER}; "
    f"DATABASE={DB_NAME}; "
    f"UID={DB_USER}; "
    f"PWD={DB_PASSWORD}; "
    f"TrustServerCertificate=yes; MARS_Connection=yes;"
) if all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]) else ""

# Application Settings
URL_HISTORY_FILE = os.path.join(APP_ROOT, "posted_urls.txt")
MAX_HISTORY_LINES = 100
CLEANUP_THRESHOLD = 10
MAX_ARTICLE_RETRIES = 30

# Platform Enable/Disable Settings
ENABLE_BLUESKY = os.getenv("ENABLE_BLUESKY", "true").lower() in ("true", "1", "yes")
ENABLE_TWITTER = os.getenv("ENABLE_TWITTER", "false").lower() in ("true", "1", "yes")

# Social Media Platform Settings
# Dynamically build platform list based on enabled platforms
_enabled_platforms = []
if ENABLE_BLUESKY:
    _enabled_platforms.append("bluesky")
if ENABLE_TWITTER:
    _enabled_platforms.append("twitter")

DEFAULT_PLATFORMS = _enabled_platforms if _enabled_platforms else ["bluesky"]  # Fallback to bluesky if none enabled

# AI Model Settings
DEFAULT_AI_MODELS = [
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash'
]

# =============================================================================
# Content Processing Settings
# =============================================================================

# Article Content Thresholds
MIN_ARTICLE_WORD_COUNT = 50          # Minimum words for a valid article
SUMMARY_TRUNCATE_LENGTH = 97         # Max length for article summary (before "...")
SUMMARY_WORD_LIMIT = 30              # Maximum words in summary

# Selenium/Browser Settings
SELENIUM_REDIRECT_TIMEOUT = 3        # Seconds to wait for Google News redirect
SELENIUM_PAGE_LOAD_TIMEOUT = 5       # Seconds to wait for page JavaScript to load
XPATH_MIN_TEXT_LENGTH = 20           # Minimum text length for XPath paragraph extraction

# =============================================================================
# AI Service Settings
# =============================================================================

# Similarity Checking
SIMILARITY_CHECK_POSTS_LIMIT = 30    # Number of recent posts to compare for similarity
MIN_KEYWORD_LENGTH = 3               # Minimum word length for keyword matching (strict >; words 4+ chars kept)
TITLE_SIMILARITY_THRESHOLD = 0.6     # Ratio threshold for title word overlap (0-1)
AI_COMPARISON_TEXT_LENGTH = 500      # Article text length for AI similarity comparison

# Article Selection
CANDIDATE_SELECTION_LIMIT = 90       # Number of candidates to randomize from pool

# Tweet Generation
ARTICLE_TEXT_TRUNCATE_LENGTH = 4000  # Max article text length sent to AI for tweet
TWEET_CHARACTER_LIMIT = 260          # Character limit for generated tweet (excluding hashtags)

# =============================================================================
# Social Media Platform Settings
# =============================================================================

# BlueSky Settings
BLUESKY_FETCH_LIMIT = 80             # Default number of recent posts to fetch
BLUESKY_IMAGE_TIMEOUT = 10           # Seconds timeout for image upload
EMBED_DESCRIPTION_LENGTH = 100       # Max length for embed description

# Twitter Settings
TWITTER_FETCH_LIMIT = 50             # Default number of recent tweets to fetch
TWITTER_API_MAX_RESULTS = 100        # Twitter API max results per request
TWITTER_URL_LENGTH = 23              # t.co shortened URL length
TWITTER_CHARACTER_LIMIT = 280        # Twitter's character limit
TWEET_TRUNCATION_PADDING = 4         # Padding chars when truncating tweets ("...")
TWITTER_IMAGE_TIMEOUT = 10           # Seconds timeout for image download

# =============================================================================
# Database Query Settings
# =============================================================================

DB_TOTAL_NEWS_FEED_RESULTS = 300     # Total articles to fetch from news feed
DB_CAT1_ALLOCATION = 0.23            # Category 1 (World) ~23%
DB_CAT2_ALLOCATION = 0.23            # Category 2 (National) ~23%
DB_CAT3_ALLOCATION = 0.18            # Category 3 (Business) ~18%
DB_CAT4_ALLOCATION = 0.18            # Category 4 (Technology) ~18%
DB_CAT7_ALLOCATION = 0.18            # Category 7 (Science) ~18% (remainder)

# Web Scraping Settings
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
REQUEST_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# =============================================================================
# YouTube Settings
# =============================================================================

YOUTUBE_DB_NAME = os.getenv("YOUTUBE_DB_NAME", "NewsAnalysis.YouTube")

# Build YouTube connection string (same server/creds, different database)
YOUTUBE_DB_CONNECTION_STRING = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}}; "
    f"SERVER={DB_SERVER}; "
    f"DATABASE={YOUTUBE_DB_NAME}; "
    f"UID={DB_USER}; "
    f"PWD={DB_PASSWORD}; "
    f"TrustServerCertificate=yes; MARS_Connection=yes;"
) if all([DB_SERVER, YOUTUBE_DB_NAME, DB_USER, DB_PASSWORD]) else ""

# YouTube Posting Feature Flag
ENABLE_YOUTUBE_POSTING = os.getenv("ENABLE_YOUTUBE_POSTING", "false").lower() in ("true", "1", "yes")

# YouTube Candidate Selection
YOUTUBE_MAX_CANDIDATES = 250           # Videos to fetch from DB (needs headroom for filtering)
YOUTUBE_MAX_AGE_DAYS = 3               # Only consider videos from last N days
YOUTUBE_MIN_VIEWS = 1000               # Minimum view count threshold
YOUTUBE_MIN_DURATION_SECONDS = 60      # Skip very short videos (under 1 min)
YOUTUBE_MAX_DURATION_SECONDS = 360     # Skip long show segments (over 6 min)
YOUTUBE_CANDIDATE_SELECTION_LIMIT = 50 # Pool size for AI selection

# YouTube Posting Limits
YOUTUBE_MAX_POSTS_PER_RUN = 1          # Maximum videos to post per run
YOUTUBE_MAX_RETRIES = 15               # Max video candidates to try before giving up

# YouTube Channel Quality Tiers
# Lower tier = higher preference. Unknown channels default to YOUTUBE_DEFAULT_TIER.
#   Tier 1: Wire services & hard-news public broadcasters (AP, Reuters, BBC News, C-SPAN, PBS, NPR, AFP)
#   Tier 2: Major mainstream commercial news (NBC, ABC, CBS, CNN, Al Jazeera EN, Bloomberg, etc.)
#   Tier 3: Opinion-heavy cable/commentary (Fox News, MSNBC, Sky News Australia) — capped hard
#   Tier 4: Blocked (state propaganda, consistently unreliable per Wikipedia Perennial Sources)
YOUTUBE_CHANNEL_TIERS: dict = {
    # Tier 1 — Wire services & hard-news public broadcasters
    '@reuters': 1,
    '@associatedpress': 1,
    '@afp': 1,
    '@bbcnews': 1,
    '@pbsnewshour': 1,
    '@npr': 1,
    '@cspan': 1,

    # Tier 2 — Major mainstream, generally straight news
    '@nbcnews': 2,
    '@abcnews': 2,
    '@cbsnews': 2,
    '@cnn': 2,
    '@cbsmornings': 2,
    '@abc7': 2,
    '@bloombergtv': 2,
    '@wsj': 2,
    '@nytimes': 2,
    '@theeconomist': 2,
    '@aljazeeraenglish': 2,
    '@cbcnews': 2,
    '@cbcthenational': 2,
    '@globalnews': 2,
    '@skynews': 2,
    '@itvnews': 2,
    '@dwnews': 2,
    '@tagesschau': 2,
    '@france24': 2,
    '@euronews': 2,
    '@telemundonoticias': 2,
    '@aristeguinoticias': 2,

    # Tier 3 — Opinion-heavy cable/commentary (hard-capped to 1 per pool)
    '@foxnews': 3,
    '@foxbusiness': 3,
    '@msnbc': 3,
    '@skynewsaustralia': 3,

    # Tier 4 — Blocked (state-affiliated propaganda or deprecated-unreliable)
    '@trtworld': 4,
    '@rt': 4,
    '@sputnik': 4,
    '@cgtn': 4,
    '@presstv': 4,
    '@newsmax': 4,
    '@oann': 4,
}

YOUTUBE_DEFAULT_TIER: int = 2   # Default tier for channels not in YOUTUBE_CHANNEL_TIERS

# Per-tier caps on videos per channel in the AI's candidate pool.
# Replaces the former flat YOUTUBE_MAX_PER_CHANNEL. Tier 4 is filtered before this applies.
YOUTUBE_TIER_CAPS: dict = {
    1: 5,   # Wire/public can dominate the pool
    2: 3,   # Mainstream retains the previous flat cap
    3: 1,   # Opinion-heavy hard-limited to one per pool
    4: 0,   # Never reached — T4 filtered earlier
}

# YouTube Editorial Filters (principle-based, channel-agnostic)
# Title patterns that indicate opinion/commentary rather than straight news reporting
YOUTUBE_OPINION_TITLE_PATTERNS: list = [
    r'\b(opinion|editorial|commentary|my take|my thoughts)\b',
    r'\b(rant|reacts?|reaction|claps? back|destroys?|slams?|owned|obliterat)',
    r'\b(debate|panel discussion|roundtable)\b',
    r'^(WATCH|LISTEN|MUST SEE|YOU WON\'T BELIEVE)',
    r'\b(top \d+|ranking|rated|best of|worst of)\b',
    r'\b(full (show|episode|program|interview))\b',
    r'\b(highlights?|recap|compilation|montage)\b',
]

# =============================================================================
# Domain Lists and Content Filtering
# =============================================================================

# Import domain lists from domain_lists module and re-export for backward compatibility
from config.domain_lists import (
    PAYWALL_PHRASES,
    PAYWALL_DOMAINS,
    BLOCKED_DOMAINS,
    PR_TITLE_PATTERNS,
)

# =============================================================================
# Configuration Validation
# =============================================================================

# Import validation logic from validators module and re-export for backward compatibility
from config.validators import ConfigurationError, validate_settings, get_config_summary