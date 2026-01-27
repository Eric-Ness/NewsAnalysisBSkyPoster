"""
Helper Utility Module

This module provides various helper functions used throughout the News Poster application.
"""

import os
import time
import re
import socket
import ipaddress
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid (basic check).

    Args:
        url: The URL to validate

    Returns:
        bool: True if the URL is valid, False otherwise

    Note:
        For security-critical validation, use validate_url() instead.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


# =============================================================================
# URL Security Functions
# =============================================================================

# Maximum allowed URL length (RFC 2616 suggests 2048 for compatibility)
MAX_URL_LENGTH = 2048

# Allowed URL schemes
ALLOWED_SCHEMES = {'http', 'https'}


def is_private_ip(hostname: str) -> bool:
    """
    Check if a hostname resolves to a private/internal IP address.

    This function helps prevent SSRF (Server-Side Request Forgery) attacks
    by blocking access to internal network resources.

    Args:
        hostname: The hostname to check (e.g., 'example.com' or '192.168.1.1')

    Returns:
        bool: True if the hostname is a private/internal IP, False otherwise
    """
    # Check for localhost variations
    localhost_patterns = {'localhost', 'localhost.localdomain', '127.0.0.1', '::1', '[::1]'}
    if hostname.lower() in localhost_patterns:
        return True

    # Try to parse as IP address directly
    try:
        # Remove brackets for IPv6
        clean_hostname = hostname.strip('[]')
        ip = ipaddress.ip_address(clean_hostname)

        # Check if it's a private, loopback, or link-local address
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return True

        # Specifically check for AWS metadata endpoint
        if str(ip) == '169.254.169.254':
            return True

        return False
    except ValueError:
        pass

    # Try DNS resolution for hostname
    try:
        # Get all IP addresses for the hostname
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)

        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return True
                # Check AWS metadata endpoint
                if str(ip) == '169.254.169.254':
                    return True
            except ValueError:
                continue

        return False
    except (socket.gaierror, socket.herror, OSError):
        # DNS resolution failed - could be invalid hostname
        # Return False to allow the request to fail naturally
        return False


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive URL validation with security checks.

    Validates that a URL is safe to process by checking:
    - URL is a non-empty string
    - URL length is within limits
    - Scheme is http or https only (blocks javascript://, file://, data://, etc.)
    - Has a valid network location (domain)
    - Does not point to private/internal IP addresses (SSRF protection)

    Args:
        url: The URL to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
            - (True, None) if URL is valid
            - (False, error_message) if URL is invalid
    """
    # Check for empty or non-string input
    if not url or not isinstance(url, str):
        return False, "URL is empty or not a string"

    # Check URL length
    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters"

    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Failed to parse URL: {e}"

    # Check scheme (must be http or https)
    if not parsed.scheme:
        return False, "URL has no scheme"

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False, f"URL scheme '{parsed.scheme}' is not allowed (only http/https)"

    # Check for valid netloc (domain)
    if not parsed.netloc:
        return False, "URL has no domain"

    # Extract hostname (without port)
    hostname = parsed.netloc.split(':')[0]

    if not hostname:
        return False, "URL has empty hostname"

    # Check for private/internal IPs (SSRF protection)
    if is_private_ip(hostname):
        return False, f"URL points to private/internal address: {hostname}"

    return True, None


def extract_base_domain(url: str) -> Optional[str]:
    """
    Extract the base (registrable) domain from a URL.

    Handles subdomains correctly:
    - 'https://www.example.com/path' -> 'example.com'
    - 'https://sub.domain.example.com' -> 'example.com'
    - 'https://example.co.uk' -> 'example.co.uk' (preserves compound TLDs)

    Args:
        url: The URL to extract the domain from

    Returns:
        Optional[str]: The base domain in lowercase, or None if extraction fails
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()

        if not hostname:
            return None

        # Remove port if present
        hostname = hostname.split(':')[0]

        # Handle IP addresses - return as-is
        try:
            ipaddress.ip_address(hostname.strip('[]'))
            return hostname
        except ValueError:
            pass

        # Split hostname into parts
        parts = hostname.split('.')

        if len(parts) < 2:
            return hostname

        # Common compound TLDs (two-part TLDs)
        compound_tlds = {
            'co.uk', 'com.au', 'co.nz', 'co.za', 'com.br', 'co.jp',
            'co.kr', 'co.in', 'org.uk', 'net.au', 'gov.uk', 'ac.uk',
            'edu.au', 'or.jp', 'ne.jp', 'go.jp'
        }

        # Check if we have a compound TLD
        if len(parts) >= 3:
            potential_compound = '.'.join(parts[-2:])
            if potential_compound in compound_tlds:
                # Return domain + compound TLD (e.g., 'example.co.uk')
                return '.'.join(parts[-3:])

        # Return the last two parts (e.g., 'example.com')
        return '.'.join(parts[-2:])

    except Exception:
        return None


def is_domain_match(url: str, domain_list: List[str]) -> bool:
    """
    Check if a URL's domain matches any domain in the provided list.

    Uses exact base domain matching to prevent bypasses like:
    - 'wsj.com.attacker.com' matching 'wsj.com' (substring attack)
    - 'notreally-wsj.com' matching 'wsj.com' (suffix attack)

    Args:
        url: The URL to check
        domain_list: List of domains to match against (e.g., ['wsj.com', 'nytimes.com'])

    Returns:
        bool: True if the URL's domain matches any domain in the list
    """
    base_domain = extract_base_domain(url)

    if not base_domain:
        return False

    # Normalize domain list for comparison
    normalized_list = [d.lower().strip() for d in domain_list]

    return base_domain in normalized_list

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