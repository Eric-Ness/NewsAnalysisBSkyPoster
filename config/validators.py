"""
Configuration Validation for News Poster Application

This module contains configuration validation logic and related exceptions.
Extracted from settings.py for better separation of concerns.
"""


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


def validate_settings():
    """
    Validate that all required settings are properly configured.

    Raises:
        ConfigurationError: If required settings are missing or invalid.
    """
    # Import settings here to avoid circular imports
    from config import settings

    errors = []

    # Required environment variables
    required_vars = [
        ("GOOGLE_AI_API_KEY", settings.GOOGLE_AI_API_KEY),
        ("DB_SERVER", settings.DB_SERVER),
        ("DB_NAME", settings.DB_NAME),
        ("DB_USER", settings.DB_USER),
        ("DB_PASSWORD", settings.DB_PASSWORD)
    ]

    for var_name, var_value in required_vars:
        if not var_value:
            errors.append(f"Missing required environment variable: {var_name}")

    # Verify database connection string was built successfully
    if not settings.DB_CONNECTION_STRING:
        errors.append("Database connection string could not be built. Check DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD.")

    # Check platform enable/disable configuration
    import logging
    logger = logging.getLogger(__name__)

    if not settings.ENABLE_BLUESKY and not settings.ENABLE_TWITTER:
        logger.warning("Both ENABLE_BLUESKY and ENABLE_TWITTER are disabled. "
                      "Defaulting to BlueSky only. Check your .env configuration.")

    # Check for at least one social media platform authentication
    bluesky_configured = bool(settings.AT_PROTOCOL_USERNAME and settings.AT_PROTOCOL_PASSWORD)

    twitter_oauth1 = all([
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_KEY_SECRET,
        settings.TWITTER_ACCESS_TOKEN,
        settings.TWITTER_ACCESS_TOKEN_SECRET
    ])

    twitter_app_only = all([
        settings.TWITTER_API_KEY,
        settings.TWITTER_API_KEY_SECRET,
        settings.TWITTER_BEARER_TOKEN
    ])

    twitter_configured = twitter_oauth1 or twitter_app_only

    # Validate enabled platforms have credentials
    if settings.ENABLE_BLUESKY and not bluesky_configured:
        errors.append("ENABLE_BLUESKY is true but BlueSky credentials are not configured. "
                     "Please configure AT_PROTOCOL_USERNAME and AT_PROTOCOL_PASSWORD.")

    if settings.ENABLE_TWITTER and not twitter_configured:
        errors.append("ENABLE_TWITTER is true but Twitter credentials are not configured. "
                     "Please configure Twitter API credentials.")

    if not bluesky_configured and not twitter_configured:
        errors.append("No social media platform authentication configured. "
                     "Please configure either BlueSky or Twitter authentication.")

    # Validate numeric settings are within reasonable bounds
    numeric_validations = [
        ("MIN_ARTICLE_WORD_COUNT", settings.MIN_ARTICLE_WORD_COUNT, 1, 500),
        ("SIMILARITY_CHECK_POSTS_LIMIT", settings.SIMILARITY_CHECK_POSTS_LIMIT, 1, 500),
        ("CANDIDATE_SELECTION_LIMIT", settings.CANDIDATE_SELECTION_LIMIT, 1, 200),
        ("TWEET_CHARACTER_LIMIT", settings.TWEET_CHARACTER_LIMIT, 50, 500),
        ("TWITTER_CHARACTER_LIMIT", settings.TWITTER_CHARACTER_LIMIT, 50, 500),
        ("DB_TOTAL_NEWS_FEED_RESULTS", settings.DB_TOTAL_NEWS_FEED_RESULTS, 1, 1000),
        ("TITLE_SIMILARITY_THRESHOLD", settings.TITLE_SIMILARITY_THRESHOLD, 0.0, 1.0),
        ("DB_CAT1_ALLOCATION", settings.DB_CAT1_ALLOCATION, 0.0, 1.0),
        ("DB_CAT2_ALLOCATION", settings.DB_CAT2_ALLOCATION, 0.0, 1.0),
    ]

    for name, value, min_val, max_val in numeric_validations:
        if value < min_val or value > max_val:
            errors.append(f"{name} must be between {min_val} and {max_val}, got {value}")

    # Validate allocation percentages sum correctly
    total_allocation = settings.DB_CAT1_ALLOCATION + settings.DB_CAT2_ALLOCATION
    if total_allocation > 1.0:
        errors.append(f"Category allocations sum to {total_allocation}, must be <= 1.0")

    # Validate timeout values are positive
    timeout_settings = [
        ("SELENIUM_REDIRECT_TIMEOUT", settings.SELENIUM_REDIRECT_TIMEOUT),
        ("SELENIUM_PAGE_LOAD_TIMEOUT", settings.SELENIUM_PAGE_LOAD_TIMEOUT),
        ("BLUESKY_IMAGE_TIMEOUT", settings.BLUESKY_IMAGE_TIMEOUT),
        ("TWITTER_IMAGE_TIMEOUT", settings.TWITTER_IMAGE_TIMEOUT),
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
    # Import settings here to avoid circular imports
    from config import settings

    return {
        "platforms": {
            "bluesky": {
                "enabled": settings.ENABLE_BLUESKY,
                "configured": bool(settings.AT_PROTOCOL_USERNAME and settings.AT_PROTOCOL_PASSWORD),
            },
            "twitter": {
                "enabled": settings.ENABLE_TWITTER,
                "configured": bool(settings.TWITTER_API_KEY and settings.TWITTER_ACCESS_TOKEN),
            },
            "default_platforms": settings.DEFAULT_PLATFORMS,
        },
        "database": {
            "server": settings.DB_SERVER[:20] + "..." if settings.DB_SERVER and len(settings.DB_SERVER) > 20 else settings.DB_SERVER,
            "database": settings.DB_NAME,
        },
        "content_settings": {
            "min_article_words": settings.MIN_ARTICLE_WORD_COUNT,
            "tweet_char_limit": settings.TWEET_CHARACTER_LIMIT,
            "similarity_threshold": settings.TITLE_SIMILARITY_THRESHOLD,
        },
        "feed_settings": {
            "total_results": settings.DB_TOTAL_NEWS_FEED_RESULTS,
            "cat1_allocation": f"{int(settings.DB_CAT1_ALLOCATION * 100)}%",
            "cat2_allocation": f"{int(settings.DB_CAT2_ALLOCATION * 100)}%",
            "cat3_allocation": f"{int((1 - settings.DB_CAT1_ALLOCATION - settings.DB_CAT2_ALLOCATION) * 100)}%",
        }
    }
