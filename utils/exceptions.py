"""
Custom Exception Classes for News Poster Application

This module defines custom exceptions for better error handling and
categorization of failures across the application.
"""


class NewsPosterError(Exception):
    """Base exception for all News Poster application errors."""
    pass


# =============================================================================
# Configuration Errors
# =============================================================================

class ConfigurationError(NewsPosterError):
    """Raised when configuration validation fails or required settings are missing."""
    pass


# =============================================================================
# Article Processing Errors
# =============================================================================

class ArticleError(NewsPosterError):
    """Base exception for article-related errors."""
    pass


class PaywallError(ArticleError):
    """Raised when an article is behind a paywall."""
    pass


class ArticleFetchError(ArticleError):
    """Raised when an article cannot be fetched or downloaded."""
    pass


class ArticleParseError(ArticleError):
    """Raised when article content cannot be parsed properly."""
    pass


class InsufficientContentError(ArticleError):
    """Raised when article content is too short or empty."""
    pass


# =============================================================================
# Social Media Errors
# =============================================================================

class SocialMediaError(NewsPosterError):
    """Base exception for social media platform errors."""
    pass


class AuthenticationError(SocialMediaError):
    """Raised when authentication with a social media platform fails."""
    pass


class PostingError(SocialMediaError):
    """Raised when posting to a social media platform fails."""
    pass


class RateLimitError(SocialMediaError):
    """Raised when a rate limit is hit on a social media platform."""
    pass


class MediaUploadError(SocialMediaError):
    """Raised when media upload fails."""
    pass


# =============================================================================
# AI Service Errors
# =============================================================================

class AIServiceError(NewsPosterError):
    """Base exception for AI service errors."""
    pass


class DuplicateContentError(AIServiceError):
    """Raised when content is too similar to recently posted content."""
    pass


class ArticleSelectionError(AIServiceError):
    """Raised when AI cannot select an appropriate article."""
    pass


class TweetGenerationError(AIServiceError):
    """Raised when AI cannot generate a tweet/post."""
    pass


# =============================================================================
# Database Errors
# =============================================================================

class DatabaseError(NewsPosterError):
    """Base exception for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass
