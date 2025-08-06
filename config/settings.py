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
DB_SERVER = os.getenv("server")
DB_NAME = os.getenv("db")
DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("pwd")
DB_CONNECTION_STRING = str('DRIVER={ODBC Driver 18 for SQL Server}; SERVER=' + DB_SERVER + 
                      '; DATABASE=' + DB_NAME + 
                      '; UID=' + DB_USER + 
                      '; PWD=' + DB_PASSWORD + 
                      '; TrustServerCertificate=yes; MARS_Connection=yes;')

# Application Settings
URL_HISTORY_FILE = os.path.join(APP_ROOT, "posted_urls.txt")
MAX_HISTORY_LINES = 100
CLEANUP_THRESHOLD = 10
MAX_ARTICLE_RETRIES = 30

# Social Media Platform Settings
DEFAULT_PLATFORMS = ["bluesky", "twitter"]  # Default platforms to post to

# AI Model Settings
DEFAULT_AI_MODELS = [
    'gemini-1.5-flash',  # Good balance of capability and cost
    'gemini-flash',      # If available, even more cost-effective
    'gemini-1.0-pro',    # Fallback to older model
    'gemini-pro',        # Another fallback
    'gemini-1.5-pro',
    'gemini-1.5-pro-latest',
    'gemini-2.0-pro-exp'
]

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
    'themoscowtimes.com'    # The Moscow Times
    'freebeacon.com',       # The Washington Free Beacon
    'engadget.com',         # Engadget
    'prnewswire.com',       # PR Newswire
    'globenewswire.com'     # GlobeNewswire
]

# Function to validate settings
def validate_settings():
    """Validate that all required settings are properly configured."""
    required_vars = [
        "GOOGLE_AI_API_KEY", 
        "DB_SERVER",
        "DB_NAME", 
        "DB_USER", 
        "DB_PASSWORD"
    ]
    
    # Check for at least one social media platform authentication
    social_platform_auth = False
    
    # Check BlueSky auth
    if AT_PROTOCOL_USERNAME and AT_PROTOCOL_PASSWORD:
        social_platform_auth = True
    
    # Check Twitter auth - OAuth 1.0a or Bearer Token
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
    
    if twitter_oauth1 or twitter_app_only:
        social_platform_auth = True
    
    if not social_platform_auth:
        raise ValueError("No social media platform authentication configured. "
                         "Please configure either BlueSky or Twitter authentication.")
    
    missing = [var for var in required_vars if not globals().get(var)]
    
    if missing:
        raise ValueError(f"Missing required configuration variables: {', '.join(missing)}")