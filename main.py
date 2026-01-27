"""
News Poster Application

This is the main entry point for the News Poster application.
It fetches news articles, selects the most newsworthy one,
and posts it to social media platforms (BlueSky and Twitter).

Author: Eric Ness
Version: 5.0
"""

import sys
import re
import argparse
import logging
import pandas as pd
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from config import settings
from utils.logger import get_logger, setup_file_logging
from utils.exceptions import (
    NewsPosterError, AIServiceError, ArticleError, SocialMediaError, DatabaseError
)
from utils.helpers import is_domain_match, extract_base_domain
from data.database import db
from services.article_service import ArticleService, ArticleContent
from services.ai_service import AIService, FeedPost
from services.social_service import SocialService
from services.twitter_service import TwitterService

# Set up logging
logger = get_logger(__name__)

class NewsPoster:
    """
    Main application class for the News Poster.
    
    This class orchestrates the process of fetching, selecting,
    and posting news articles to social media.
    """
    
    def __init__(self):
        """Initialize the News Poster application."""
        # Initialize services
        self.article_service = ArticleService()
        self.ai_service = AIService()
        self.social_service = SocialService()
        self.twitter_service = TwitterService()
        
        # Validate settings
        settings.validate_settings()
    
    def run(self, test_mode: bool = False, platforms: Optional[List[str]] = None) -> bool:
        """
        Run the main workflow of the News Poster application.
        
        Args:
            test_mode: If True, runs in test mode without actually posting to social media
            platforms: List of social media platforms to post to, defaults to settings.DEFAULT_PLATFORMS
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Set default platforms if none specified
        if platforms is None:
            platforms = settings.DEFAULT_PLATFORMS
            
        # Normalize platform names
        platforms = [p.lower() for p in platforms]
        
        try:
            # 1. Get news feed data from database
            news_feed_data = db.get_news_feed()
            if news_feed_data is None or len(news_feed_data) == 0:
                logger.warning("No news feed data available")
                return False
                
            # Transform DataFrame to list of dictionaries for processing
            news_candidates = []
            for _, row in news_feed_data.iterrows():
                news_candidates.append({
                    'URL': row['URL'],
                    'Title': row['Title'],
                    'News_Feed_ID': row['News_Feed_ID'],
                    'Source_Count': row.get('Source_Count', 1)
                })
            
            # Filter out articles from paywall domains
            filtered_candidates = []
            for candidate in news_candidates:
                url = candidate['URL']
                # Check against paywall domains using secure domain matching
                if not is_domain_match(url, settings.PAYWALL_DOMAINS):
                    filtered_candidates.append(candidate)
                else:
                    logger.info(f"Filtering out paywall domain article: {candidate['Title']} ({url})")
            
            # Log how many candidates were filtered out
            if len(news_candidates) != len(filtered_candidates):
                logger.info(f"Filtered out {len(news_candidates) - len(filtered_candidates)} paywall domain articles from {len(news_candidates)} total candidates")
            
            news_candidates = filtered_candidates
            
            # 2. Get recent posts to avoid duplicates
            recent_posts = []
            
            # Get recent BlueSky posts if posting to BlueSky
            if "bluesky" in platforms:
                bsky_posts = self.social_service.get_recent_posts()
                recent_posts.extend(bsky_posts)
                logger.info(f"Retrieved {len(bsky_posts)} recent BlueSky posts")
            
            # Get recent Twitter posts if posting to Twitter
            if "twitter" in platforms:
                twitter_posts = self.twitter_service.get_recent_tweets()
                recent_posts.extend(twitter_posts)
                logger.info(f"Retrieved {len(twitter_posts)} recent Twitter posts")
            
            # 3. Select multiple newsworthy articles and try them in order
            selected_articles = self.ai_service.select_news_articles(news_candidates, recent_posts, max_count=settings.MAX_ARTICLE_RETRIES)
            if not selected_articles:
                logger.warning("No articles selected")
                return False
            
            # Try each article until one succeeds
            for selected_article in selected_articles:
                logger.info(f"Trying article: {selected_article['Title']}")
                
                # 4. Check if article URL is in history
                if self.article_service.is_url_in_history(selected_article['URL']):
                    logger.warning(f"Article URL already in history: {selected_article['URL']}")
                    continue
                    
                # 5. Get the real URL (if it's a Google News URL)
                # Use proper domain check to prevent bypass attacks
                url_domain = extract_base_domain(selected_article['URL'])
                if url_domain == "google.com" and "news.google.com" in selected_article['URL']:
                    real_url = self.article_service.get_real_url(selected_article['URL'])
                    if real_url:
                        selected_article['URL'] = real_url

                        # Check if resolved URL is from a blocked domain
                        if is_domain_match(real_url, settings.BLOCKED_DOMAINS):
                            logger.warning(f"Resolved URL is from blocked domain: {real_url}")
                            continue

                        # Check .gov and .mil TLDs using proper domain extraction
                        resolved_domain = extract_base_domain(real_url)
                        if resolved_domain and (resolved_domain.endswith('.gov') or resolved_domain.endswith('.mil')):
                            logger.warning(f"Resolved URL is from .gov/.mil domain: {real_url}")
                            continue

                        # Check paywall domains
                        if is_domain_match(real_url, settings.PAYWALL_DOMAINS):
                            logger.warning(f"Resolved URL is from paywall domain: {real_url}")
                            continue
                
                # 6. Fetch the selected article content
                article_content = self.article_service.fetch_article(
                    selected_article['URL'], 
                    selected_article['News_Feed_ID']
                )
                
                if not article_content:
                    logger.warning(f"Failed to fetch article content for: {selected_article['Title']}")
                    continue
                    
                # 7. Check for content similarity with recent posts
                if self.ai_service.check_content_similarity(
                    article_content.title, 
                    article_content.text, 
                    recent_posts
                ):
                    logger.warning(f"Article content too similar to recent posts: {article_content.title}")
                    continue
                    
                # 8. Generate social media content
                tweet_data = self.ai_service.generate_tweet(
                    article_content.text,
                    article_content.title,
                    article_content.url
                )
                
                if not tweet_data:
                    logger.warning(f"Failed to generate social media content for: {article_content.title}")
                    continue
                
                # Track success across platforms
                success = False
                    
                # 9. Post to social media platforms (unless in test mode)
                if not test_mode:
                    # Post to BlueSky if enabled
                    if "bluesky" in platforms:
                        bsky_posted, bsky_social_post_id = self.social_service.post_to_social(
                            tweet_data['tweet_text'],
                            article_content.url,
                            article_content.title,
                            article_content.top_image,
                            tweet_data.get('facets'),
                            news_feed_id=article_content.news_feed_id
                        )

                        if bsky_posted:
                            logger.info(f"Successfully posted to BlueSky: {article_content.title}")
                            if bsky_social_post_id:
                                logger.info(f"BlueSky post stored with Social_Post_ID: {bsky_social_post_id}")

                            # Update database for BlueSky post
                            db.update_news_feed(
                                article_content.news_feed_id,
                                article_content.text,
                                tweet_data['tweet_text'],
                                article_content.url,
                                article_content.top_image or "",
                                platform="bluesky"
                            )

                            success = True
                        else:
                            logger.warning(f"Failed to post to BlueSky for: {article_content.title}")
                    
                    # Post to Twitter if enabled
                    if "twitter" in platforms:
                        twitter_posted, twitter_social_post_id = self.twitter_service.post_tweet(
                            tweet_data['tweet_text'],
                            article_content.url,
                            article_content.title,
                            article_content.top_image,
                            news_feed_id=article_content.news_feed_id
                        )

                        if twitter_posted:
                            logger.info(f"Successfully posted to Twitter: {article_content.title}")
                            if twitter_social_post_id:
                                logger.info(f"Twitter post stored with Social_Post_ID: {twitter_social_post_id}")

                            # Update database for Twitter post
                            db.update_news_feed(
                                article_content.news_feed_id,
                                article_content.text,
                                tweet_data['tweet_text'],
                                article_content.url,
                                article_content.top_image or "",
                                platform="twitter"
                            )
                            
                            success = True
                        else:
                            logger.warning(f"Failed to post to Twitter for: {article_content.title}")
                    
                    # If posted to at least one platform, add URL to history
                    if success:
                        self.article_service._add_url_to_history(article_content.url)
                else:
                    # Test mode
                    platforms_str = ", ".join(platforms)
                    logger.info(f"TEST MODE: Would post article to {platforms_str}: {article_content.title}")
                    logger.info(f"Social media text: {tweet_data['tweet_text']}")
                    success = True
                
                # If we got here with success, we're done
                if success:
                    return True
            
            # If we tried all articles and none worked
            logger.error("All selected articles failed processing")
            return False
            
        except AIServiceError as e:
            logger.error(f"AI service error in news processing: {e}", exc_info=True)
            return False
        except ArticleError as e:
            logger.error(f"Article processing error: {e}", exc_info=True)
            return False
        except SocialMediaError as e:
            logger.error(f"Social media error: {e}", exc_info=True)
            return False
        except DatabaseError as e:
            logger.error(f"Database error in news processing: {e}", exc_info=True)
            return False
        except NewsPosterError as e:
            logger.error(f"News poster error: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Unexpected error in NewsAnalyzer process_news_feed: {e}", exc_info=True)
            return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='News Poster Application')
    parser.add_argument('--test', action='store_true', help='Run in test mode without posting')
    parser.add_argument('--log-file', type=str, default='news_poster.log', help='Log file path')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Logging level')
    parser.add_argument('--platforms', type=str, default=None, 
                        help='Comma-separated list of platforms to post to (bluesky,twitter)')
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_file_logging(args.log_file, log_level)
    
    # Parse platforms
    platforms = None
    if args.platforms:
        platforms = [p.strip().lower() for p in args.platforms.split(',')]
    
    # Log application start
    logger.info("Starting News Poster application")
    if platforms:
        logger.info(f"Posting to platforms: {', '.join(platforms)}")
    
    try:
        # Initialize and run the News Poster
        poster = NewsPoster()
        success = poster.run(test_mode=args.test, platforms=platforms)
        
        # Report status
        if success:
            logger.info("News Poster completed successfully")
            exit_code = 0
        else:
            logger.warning("News Poster completed with warnings or errors")
            exit_code = 1
            
    except Exception as e:
        logger.error(f"Unhandled exception in News Poster: {e}", exc_info=True)
        exit_code = 2
    
    # Log application end
    logger.info(f"News Poster application finished with exit code {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())