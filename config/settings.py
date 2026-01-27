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
load_dotenv(dotenv_path=os.path.join(APP_ROOT, '.env'))

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

# Social Media Platform Settings
DEFAULT_PLATFORMS = ["bluesky", "twitter"]  # Default platforms to post to

# AI Model Settings
DEFAULT_AI_MODELS = [
    'gemini-2.0-flash',  # Good balance of capability and cost
    'gemini-2.0-flash-lite',      # If available, even more cost-effective
    'gemini-2.5-flash-lite',    # Fallback to older model
    'gemini-2.5-flash'
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
SIMILARITY_CHECK_POSTS_LIMIT = 72    # Number of recent posts to compare for similarity
MIN_KEYWORD_LENGTH = 3               # Minimum word length for keyword matching
TITLE_SIMILARITY_THRESHOLD = 0.5     # Ratio threshold for title word overlap (0-1)
AI_COMPARISON_TEXT_LENGTH = 500      # Article text length for AI similarity comparison

# Article Selection
CANDIDATE_SELECTION_LIMIT = 60       # Number of candidates to randomize from pool

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

DB_TOTAL_NEWS_FEED_RESULTS = 160     # Total articles to fetch from news feed
DB_CAT1_ALLOCATION = 0.5             # Category 1 (World) allocation percentage
DB_CAT2_ALLOCATION = 0.4             # Category 2 (National) allocation percentage
# Category 3 (Business) gets remainder: 1 - CAT1 - CAT2 = 0.1 (10%)

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