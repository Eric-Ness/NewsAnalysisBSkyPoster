"""
Helper Utility Module

This module provides various helper functions used throughout the News Poster application.
"""

import os
import time
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def retry(func, max_attempts: int = 3, delay: int = 2, 
          exceptions: Tuple = (Exception,), backoff: int = 2):
    """
    Retry a function multiple times if it fails.
    
    Args:
        func: The function to retry
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        exceptions: Tuple of exceptions to catch
        backoff: Multiplier for the delay between attempts
        
    Returns:
        The result of the function call
    
    Raises:
        The last exception raised by the function
    """
    attempt = 0
    while attempt < max_attempts:
        try:
            return func()
        except exceptions as e:
            attempt += 1
            if attempt == max_attempts:
                raise e
            
            wait_time = delay * (backoff ** (attempt - 1))
            time.sleep(wait_time)

def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: The text to clean
        
    Returns:
        str: Text with HTML tags removed
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: The text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add an ellipsis if text is truncated
        
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rstrip()
    if add_ellipsis:
        truncated += "..."
    
    return truncated

def get_date_range(days_back: int = 7) -> Tuple[datetime, datetime]:
    """
    Get a date range from now to X days back.
    
    Args:
        days_back: Number of days to go back
        
    Returns:
        Tuple: (start_date, end_date)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date

def safe_get(data: Dict[str, Any], *keys, default: Any = None) -> Any:
    """
    Safely get a value from a nested dictionary.
    
    Args:
        data: The dictionary to search
        *keys: The keys to follow
        default: Default value if key doesn't exist
        
    Returns:
        The value at the specified keys or the default value
    """
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data

def ensure_dir_exists(directory: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: The directory path to check/create
    """
    if not os.path.exists(directory):
        os.makedirs(directory) 