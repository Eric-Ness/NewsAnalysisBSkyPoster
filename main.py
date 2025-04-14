"""
News Poster Application

This is the main entry point for the News Poster application.
It fetches news articles, selects the most newsworthy one,
and posts it to the AT Protocol (BlueSky) feed.

Author: Eric Ness
Version: 4.0
"""

import sys
import argparse
import logging
import pandas as pd
from typing import Optional, List, Dict, Any

from config import settings
from utils.logger import get_logger, setup_file_logging
from data.database import db
from services.article_service import ArticleService, ArticleContent
from services.ai_service import AIService, FeedPost
from services.social_service import SocialService

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
        
        # Validate settings
        settings.validate_settings()
    
    def run(self, test_mode: bool = False) -> bool:
        """
        Run the main workflow of the News Poster application.
        
        Args:
            test_mode: If True, runs in test mode without actually posting to social media
            
        Returns:
            bool: True if successful, False otherwise
        """
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
                    'News_Feed_ID': row['News_Feed_ID']
                })
            
            # Filter out articles from paywall domains
            filtered_candidates = []
            for candidate in news_candidates:
                if not any(domain in candidate['URL'] for domain in settings.PAYWALL_DOMAINS):
                    filtered_candidates.append(candidate)
                else:
                    logger.info(f"Filtering out paywall domain article: {candidate['Title']} ({candidate['URL']})")
            
            # Log how many candidates were filtered out
            if len(news_candidates) != len(filtered_candidates):
                logger.info(f"Filtered out {len(news_candidates) - len(filtered_candidates)} paywall domain articles from {len(news_candidates)} total candidates")
            
            news_candidates = filtered_candidates
            
            # 2. Get recent posts to avoid duplicates
            recent_posts = self.social_service.get_recent_posts()
            
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
                if "news.google.com" in selected_article['URL']:
                    real_url = self.article_service.get_real_url(selected_article['URL'])
                    if real_url:
                        selected_article['URL'] = real_url
                        
                        # Check if resolved URL is from a paywall domain
                        if any(domain in selected_article['URL'] for domain in settings.PAYWALL_DOMAINS):
                            logger.warning(f"Resolved URL is from paywall domain: {selected_article['URL']}")
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
                    
                # 8. Generate tweet text
                tweet_data = self.ai_service.generate_tweet(
                    article_content.text,
                    article_content.title,
                    article_content.url
                )
                
                if not tweet_data:
                    logger.warning(f"Failed to generate tweet content for: {article_content.title}")
                    continue
                    
                # 9. Post to social media (unless in test mode)
                if not test_mode:
                    posted = self.social_service.post_to_social(
                        tweet_data['tweet_text'],
                        article_content.url,
                        article_content.title,
                        article_content.top_image
                    )
                    
                    if not posted:
                        logger.warning(f"Failed to post to social media for: {article_content.title}")
                        continue
                        
                    # 10. Update database
                    db.update_news_feed(
                        article_content.news_feed_id,
                        article_content.text,
                        tweet_data['tweet_text'],
                        article_content.url,
                        article_content.top_image or ""
                    )
                    
                    # 11. Add URL to history
                    self.article_service._add_url_to_history(article_content.url)
                    
                    logger.info(f"Successfully posted article: {article_content.title}")
                else:
                    logger.info(f"TEST MODE: Would post article: {article_content.title}")
                    logger.info(f"Tweet text: {tweet_data['tweet_text']}")
                
                # If we got here, we succeeded with this article
                return True
            
            # If we tried all articles and none worked
            logger.error("All selected articles failed processing")
            return False
            
        except Exception as e:
            logger.error(f"Error in NewsAnalyzer process_news_feed: {e}", exc_info=True)
            return False

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='News Poster Application')
    parser.add_argument('--test', action='store_true', help='Run in test mode without posting')
    parser.add_argument('--log-file', type=str, default='news_poster.log', help='Log file path')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Logging level')
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_file_logging(args.log_file, log_level)
    
    # Log application start
    logger.info("Starting News Poster application")
    
    try:
        # Initialize and run the News Poster
        poster = NewsPoster()
        success = poster.run(test_mode=args.test)
        
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