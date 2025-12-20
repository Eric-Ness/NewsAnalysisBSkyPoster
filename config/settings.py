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

# Paywall Detection
PAYWALL_PHRASES = [
    "subscribe", "subscription", "sign in",
    "premium content", "premium article",
    "paid subscribers only"
]

# Known Paywall Domains - these sites are known to implement paywalls
PAYWALL_DOMAINS = [
    "wsj.com",              # Wall Street Journal
    "nytimes.com",          # New York Times
    "ft.com",               # Financial Times
    "economist.com",        # The Economist
    "bloomberg.com",        # Bloomberg
    "washingtonpost.com",   # Washington Post
    "theatlantic.com",      # The Atlantic
    "newyorker.com",        # The New Yorker
    "medium.com",           # Medium
    "wired.com",            # Wired
    "barrons.com",          # Barron's
    "forbes.com",           # Forbes (sometimes)
    "businessinsider.com",  # Business Insider Prime
    "insider.com",          # Insider
    "buzzfeed.com",         # BuzzFeed (sometimes)
    "understandingwar.org", # Institute for the Study of War
    "federalreserve.gov",   # Federal Reserve
    "whitehouse.gov",       # White House
    "congress.gov",         # Congress
    "justice.gov",          # Department of Justice
    "state.gov",            # Department of State
    "defense.gov",          # Department of Defense
    "cia.gov",              # Central Intelligence Agency
    "nsa.gov",              # National Security Agency
    "fbi.gov",              # Federal Bureau of Investigation
    "dhs.gov",              # Department of Homeland Security
    "dod.gov",              # Department of Defense
    "nasa.gov",             # National Aeronautics and Space Administration
    "treasury.gov",         # Department of the Treasury
    'scmp.com',             # South China Morning Post
    'themoscowtimes.com',   # The Moscow Times
    'freebeacon.com',       # The Washington Free Beacon
    'engadget.com',         # Engadget
    'prnewswire.com',       # PR Newswire
    'globenewswire.com'     # GlobeNewswire (last item, no comma needed)
]

# =============================================================================
# Configuration Validation
# =============================================================================

class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_settings():
    """
    Validate that all required settings are properly configured.

    Raises:
        ConfigurationError: If required settings are missing or invalid.
    """
    errors = []
    warnings = []

    # Required environment variables
    required_vars = [
        ("GOOGLE_AI_API_KEY", GOOGLE_AI_API_KEY),
        ("DB_SERVER", DB_SERVER),
        ("DB_NAME", DB_NAME),
        ("DB_USER", DB_USER),
        ("DB_PASSWORD", DB_PASSWORD)
    ]

    for var_name, var_value in required_vars:
        if not var_value:
            errors.append(f"Missing required environment variable: {var_name}")

    # Verify database connection string was built successfully
    if not DB_CONNECTION_STRING:
        errors.append("Database connection string could not be built. Check DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD.")

    # Check for at least one social media platform authentication
    bluesky_configured = bool(AT_PROTOCOL_USERNAME and AT_PROTOCOL_PASSWORD)

    twitter_oauth1 = all([
        TWITTER_API_KEY,
        TWITTER_API_KEY_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    ])

    twitter_app_only = all([
        TWITTER_API_KEY,
        TWITTER_API_KEY_SECRET,
        TWITTER_BEARER_TOKEN
    ])

    twitter_configured = twitter_oauth1 or twitter_app_only

    if not bluesky_configured and not twitter_configured:
        errors.append("No social media platform authentication configured. "
                     "Please configure either BlueSky or Twitter authentication.")

    # Validate numeric settings are within reasonable bounds
    numeric_validations = [
        ("MIN_ARTICLE_WORD_COUNT", MIN_ARTICLE_WORD_COUNT, 1, 500),
        ("SIMILARITY_CHECK_POSTS_LIMIT", SIMILARITY_CHECK_POSTS_LIMIT, 1, 500),
        ("CANDIDATE_SELECTION_LIMIT", CANDIDATE_SELECTION_LIMIT, 1, 200),
        ("TWEET_CHARACTER_LIMIT", TWEET_CHARACTER_LIMIT, 50, 500),
        ("TWITTER_CHARACTER_LIMIT", TWITTER_CHARACTER_LIMIT, 50, 500),
        ("DB_TOTAL_NEWS_FEED_RESULTS", DB_TOTAL_NEWS_FEED_RESULTS, 1, 1000),
        ("TITLE_SIMILARITY_THRESHOLD", TITLE_SIMILARITY_THRESHOLD, 0.0, 1.0),
        ("DB_CAT1_ALLOCATION", DB_CAT1_ALLOCATION, 0.0, 1.0),
        ("DB_CAT2_ALLOCATION", DB_CAT2_ALLOCATION, 0.0, 1.0),
    ]

    for name, value, min_val, max_val in numeric_validations:
        if value < min_val or value > max_val:
            errors.append(f"{name} must be between {min_val} and {max_val}, got {value}")

    # Validate allocation percentages sum correctly
    total_allocation = DB_CAT1_ALLOCATION + DB_CAT2_ALLOCATION
    if total_allocation > 1.0:
        errors.append(f"Category allocations sum to {total_allocation}, must be <= 1.0")

    # Validate timeout values are positive
    timeout_settings = [
        ("SELENIUM_REDIRECT_TIMEOUT", SELENIUM_REDIRECT_TIMEOUT),
        ("SELENIUM_PAGE_LOAD_TIMEOUT", SELENIUM_PAGE_LOAD_TIMEOUT),
        ("BLUESKY_IMAGE_TIMEOUT", BLUESKY_IMAGE_TIMEOUT),
        ("TWITTER_IMAGE_TIMEOUT", TWITTER_IMAGE_TIMEOUT),
    ]

    for name, value in timeout_settings:
        if value <= 0:
            errors.append(f"{name} must be positive, got {value}")

    # Raise all errors at once
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ConfigurationError(error_msg)

    return True


def get_config_summary() -> dict:
    """
    Returns a summary of current configuration (without sensitive values).
    Useful for logging startup state.
    """
    return {
        "platforms": {
            "bluesky": bool(AT_PROTOCOL_USERNAME and AT_PROTOCOL_PASSWORD),
            "twitter": bool(TWITTER_API_KEY and TWITTER_ACCESS_TOKEN),
        },
        "database": {
            "server": DB_SERVER[:20] + "..." if DB_SERVER and len(DB_SERVER) > 20 else DB_SERVER,
            "database": DB_NAME,
        },
        "content_settings": {
            "min_article_words": MIN_ARTICLE_WORD_COUNT,
            "tweet_char_limit": TWEET_CHARACTER_LIMIT,
            "similarity_threshold": TITLE_SIMILARITY_THRESHOLD,
        },
        "feed_settings": {
            "total_results": DB_TOTAL_NEWS_FEED_RESULTS,
            "cat1_allocation": f"{int(DB_CAT1_ALLOCATION * 100)}%",
            "cat2_allocation": f"{int(DB_CAT2_ALLOCATION * 100)}%",
            "cat3_allocation": f"{int((1 - DB_CAT1_ALLOCATION - DB_CAT2_ALLOCATION) * 100)}%",
        }
    }