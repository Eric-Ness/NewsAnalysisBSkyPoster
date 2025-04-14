"""
Article Service Module

This module handles article fetching, content extraction, and processing.
It provides functionality for retrieving real URLs from Google News, 
handling paywalls, and managing article content.
"""

import logging
import time
import os
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

import requests
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ArticleContent:
    """Data class to store article content and metadata.

    Attributes:
        url (str): The URL of the article.
        title (str): The title of the article.
        text (str): The full text of the article.
        summary (str): A summary of the article.
        top_image (str): The URL of the top image associated with the article.
        news_feed_id (int, optional): The database ID of the news feed item.
    """
    url: str
    title: str
    text: str
    summary: str
    top_image: str
    news_feed_id: Optional[int] = None

class PaywallError(Exception):
    """Custom exception for paywall detection."""
    pass

class ArticleService:
    """Service for fetching and processing articles."""
    
    def __init__(self):
        """Initialize the article service."""
        self.url_history_file = settings.URL_HISTORY_FILE
        self.max_history_lines = settings.MAX_HISTORY_LINES
        self.cleanup_threshold = settings.CLEANUP_THRESHOLD
        self.paywall_domains = settings.PAYWALL_DOMAINS
    
    def get_real_url(self, google_url: str) -> Optional[str]:
        """
        Get the real article URL from a Google News URL using Selenium.

        Args:
            google_url (str): The Google News URL.

        Returns:
            Optional[str]: The real article URL, or None if an error occurred.
        """
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

            service = Service(log_output=None)
            driver = webdriver.Chrome(options=chrome_options, service=service)
            
            driver.get(google_url)
            time.sleep(3)  # Allow redirect to complete
            return driver.current_url

        except Exception as e:
            logger.error(f"Error extracting real URL: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()
    
    def fetch_article(self, url: str, news_feed_id: Optional[int] = None) -> Optional[ArticleContent]:
        """
        Fetch and parse article content using newspaper3k with simple paywall detection.

        Args:
            url (str): The URL of the article to fetch and parse.
            news_feed_id (Optional[int]): The ID of the news feed item in the database.

        Returns:
            Optional[ArticleContent]: The parsed article content, or None if there was an error.
        """
        # First check if URL is from a paywall domain and skip it entirely
        if any(domain in url for domain in self.paywall_domains):
            logger.warning(f"Skipping paywall domain article: {url}")
            return None
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            article = Article(url)
            article.config.browser_user_agent = headers['User-Agent']
            article.config.headers = headers
            
            article.download()
            article.parse()
            article.nlp()

            # Basic content quality check
            if not article.text or len(article.text.split()) < 50:
                # Check for paywall indicators
                if any(phrase in article.html.lower() for phrase in settings.PAYWALL_PHRASES):
                    logger.warning(f"Paywall detected for {url}")
                    return None
                
                logger.warning(f"Article content too short: {len(article.text.split()) if article.text else 0} words")
                return None
                
            # Successfully parsed article
            return ArticleContent(
                url=article.url,
                title=article.title,
                text=article.text,
                summary=article.summary[:97] + "..." if len(article.summary) > 100 else article.summary,
                top_image=article.top_image,
                news_feed_id=news_feed_id
            )

        except Exception as e:
            logger.error(f"Error fetching article: {e} on URL {url}")
            return None
    
    def _fetch_with_selenium(self, url: str, news_feed_id: Optional[int] = None) -> Optional[ArticleContent]:
        """
        Simplified Selenium fallback for paywall bypass.
        
        Args:
            url (str): The URL of the article
            news_feed_id (Optional[int]): The ID of the news feed item
            
        Returns:
            Optional[ArticleContent]: Article content if successful, None otherwise
        """
        driver = None
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument(f'user-agent={settings.USER_AGENT}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            
            service = Service(log_output=None)
            driver = webdriver.Chrome(options=chrome_options, service=service)
            
            # Load the page
            driver.get(url)
            time.sleep(5)  # Wait for JavaScript to load
            
            # Extract content
            title = driver.title
            
            # Debug: Save HTML for inspection when troubleshooting
            html_content = driver.page_source
            
            # Try to extract paragraphs directly
            paragraphs = driver.find_elements(By.XPATH, "//p[string-length(text()) > 20]")
            text = " ".join([p.text for p in paragraphs if p.text.strip()])
            
            # Try to get main image (from meta tags first, then from regular img tags)
            img_url = ""
            meta_img = driver.find_elements(By.CSS_SELECTOR, "meta[property='og:image'], meta[name='twitter:image']")
            if meta_img:
                img_url = meta_img[0].get_attribute("content")
            
            if not img_url:
                images = driver.find_elements(By.CSS_SELECTOR, "article img, .featured-image img, figure img")
                if images:
                    img_url = images[0].get_attribute("src")
            
            # If we didn't get enough text content, try article element
            if len(text.split()) < 50:
                article_element = driver.find_elements(By.CSS_SELECTOR, "article, .article-content, #article-body")
                if article_element:
                    text = article_element[0].text
            
            # If still insufficient content, log HTML for debugging
            if len(text.split()) < 50:
                logger.warning(f"Selenium extraction yielded insufficient content: {len(text.split())} words")
                debug_dir = "debug_html"
                os.makedirs(debug_dir, exist_ok=True)
                
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{debug_dir}/{domain}_{timestamp}.html"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html_content)
                
                logger.info(f"Saved HTML debug to {filename}")
                return None
            
            # Create summary
            summary = " ".join(text.split()[:30]) + "..." if len(text.split()) > 30 else text
            
            return ArticleContent(
                url=url,
                title=title,
                text=text,
                summary=summary,
                top_image=img_url,
                news_feed_id=news_feed_id
            )
            
        except Exception as e:
            logger.error(f"Error in Selenium extraction: {e}")
            return None
            
        finally:
            if driver:
                driver.quit()
    
    def _get_posted_urls(self) -> List[str]:
        """Get list of previously posted URLs from the history file."""
        try:
            if not os.path.exists(self.url_history_file):
                logger.info(f"URL history file not found. Creating new file: {self.url_history_file}")
                with open(self.url_history_file, 'w') as f:
                    pass  # Create empty file
                return []
            
            with open(self.url_history_file, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
            
            logger.info(f"Loaded {len(urls)} URLs from history file")
            return urls
        except Exception as e:
            logger.error(f"Error reading URL history file: {e}")
            return []
    
    def _add_url_to_history(self, url: str):
        """Add a URL to the history file and clean up if needed."""
        try:
            urls = self._get_posted_urls()
            
            if url not in urls:
                urls.append(url)
            
            if len(urls) > self.max_history_lines:
                logger.info(f"URL history exceeds {self.max_history_lines} entries, removing oldest {self.cleanup_threshold}")
                urls = urls[self.cleanup_threshold:]
            
            with open(self.url_history_file, 'w') as f:
                for u in urls:
                    f.write(f"{u}\n")
            
            logger.info(f"Added URL to history file: {url}")
        except Exception as e:
            logger.error(f"Error adding URL to history file: {e}")
    
    def is_url_in_history(self, url: str) -> bool:
        """Check if URL is in the history file."""
        return url in self._get_posted_urls() 