'''
Version: 3.2
Date: 2025-04-02
Author: Eric Ness (Updated Code)

Description: This script is designed to be run as a scheduled task to automatically 
post news articles to the AT Protocol feed. It uses Google's Gemini AI model to select 
the most newsworthy article from a list of candidates and then fetches the article 
content, checks for paywalls, and posts a tweet summary to the AT Protocol feed.
Updates in this version:
- Added functionality to track previously posted URLs to avoid duplicates
- Implemented URL storage in a text file for future reference
- Added cleanup functionality for the URL history file
'''

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime, timedelta

import nltk
import pandas as pd
import requests
from atproto import Client, models
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# Import Google's Generative AI library
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")

@dataclass
class ArticleContent:
    """Data class to store article content and metadata.

    Attributes:
        url (str): The URL of the article.
        title (str): The title of the article.
        text (str): The full text of the article.
        summary (str): A summary of the article.
        top_image (str): The URL of the top image associated with the article.
    """
    url: str
    title: str
    text: str
    summary: str
    top_image: str

@dataclass
class FeedPost:
    """Data class to store AT Protocol feed post content."""
    text: str
    url: Optional[str]
    title: Optional[str]
    timestamp: datetime

class PaywallError(Exception):
    """Custom exception for paywall detection."""
    pass

class DuplicateContentError(Exception):
    """Custom exception for duplicate or similar content detection."""
    pass

class NewsAnalyzer:
    def __init__(self):
        """
        Initialize the NewsAnalyzer with required API clients and more cost-effective model selection.
        
        This method performs the following tasks:
        1. Loads environment variables.
        2. Sets the path for the URL history file.
        3. Initializes the Gemini AI by configuring the API key.
        4. Lists available models and selects a preferred model based on cost-effectiveness.
        5. Initializes the selected model.
        6. Initializes the AT Protocol client.
        7. Sets up the AT Protocol.
        """
        # Load environment variables
        load_dotenv()
        
        # Set the path for the URL history file
        self.url_history_file = "posted_urls.txt"
        self.max_history_lines = 100
        self.cleanup_threshold = 10
        
        # Initialize Gemini AI
        api_key = self._get_env_var("GOOGLE_AI_API_KEY")
        genai.configure(api_key=api_key)
        
        # List available models to debug
        try:
            models_list = genai.list_models()
            available_models = [m.name for m in models_list]
            
            # OPTIMIZED: Prioritize cost-effective models first
            # For text summarization and similarity checking, we don't need the most powerful models
            preferred_models = [
                # Prioritize more cost-effective models first
                'gemini-1.5-flash',  # Good balance of capability and cost
                'gemini-flash',      # If available, even more cost-effective
                'gemini-1.0-pro',    # Fallback to older model
                'gemini-pro',        # Another fallback
                # Only use the most expensive models as last resort
                'gemini-1.5-pro',
                'gemini-1.5-pro-latest',
                'gemini-2.0-pro-exp'
            ]
            
            model_name = None
            for preferred in preferred_models:
                for available in available_models:
                    if preferred in available:
                        model_name = available
                        break
                if model_name:
                    break
                    
            if not model_name and len(available_models) > 0:
                # If none of our preferred models are available, just use the first one
                model_name = available_models[0]
                
            if not model_name:
                raise ValueError("No Gemini models available")
            
            logger.info(f"Selected model: {model_name}")
            
            # Initialize model with the complete model path
            self.model = genai.GenerativeModel(model_name=model_name)
            
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {e}")
            raise
        
        # Initialize AT Protocol client
        self.at_client = Client()
        self._setup_at_protocol()

    def _get_env_var(self, var_name: str) -> str:
        """Safely get environment variable or raise error if not found."""
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Missing required environment variable: {var_name}")
        return value

    def _setup_at_protocol(self):
        """Set up AT Protocol authentication."""
        try:
            username = self._get_env_var("AT_PROTOCOL_USERNAME")
            password = self._get_env_var("AT_PROTOCOL_PASSWORD")
            self.at_client.login(username, password)
        except Exception as e:
            logger.error(f"Failed to authenticate with AT Protocol: {e}")
            raise
    
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
            # Get existing URLs
            urls = self._get_posted_urls()
            
            # Add new URL if it's not already in the list
            if url not in urls:
                urls.append(url)
            
            # Check if we need to clean up
            if len(urls) > self.max_history_lines:
                logger.info(f"URL history exceeds {self.max_history_lines} entries, removing oldest {self.cleanup_threshold}")
                urls = urls[self.cleanup_threshold:]
            
            # Write back to file
            with open(self.url_history_file, 'w') as f:
                for u in urls:
                    f.write(f"{u}\n")
            
            logger.info(f"Added URL to history file: {url}")
        except Exception as e:
            logger.error(f"Error adding URL to history file: {e}")
    
    def _is_url_in_history(self, url: str) -> bool:
        """Check if URL is in the history file."""
        return url in self._get_posted_urls()

    def check_content_similarity(self, article_title: str, article_text: str, recent_posts: List[FeedPost]) -> bool:
        """
        Checks if an article is too similar to recently posted content.
        Uses a tiered approach: first basic title comparison, then AI similarity check if needed.
        
        Args:
            article_title: Title of the candidate article
            article_text: Text content of the candidate article
            recent_posts: List of recent posts to compare against
            
        Returns:
            bool: True if content is similar to recent posts, False otherwise
        """
        try:
            # 1. OPTIMIZATION: Reduce number of posts to compare against
            posts_to_check = recent_posts[:15]  # Reduced from 20 to 10
            
            # 2. OPTIMIZATION: Add basic keyword matching as a pre-filter
            # Extract important keywords from title (simple approach)
            import re
            title_words = set(re.sub(r'[^\w\s]', '', article_title.lower()).split())
            title_words = {w for w in title_words if len(w) > 3}  # Only keep meaningful words
            
            # Check for basic title similarity first (cheaper than AI check)
            for post in posts_to_check:
                if not post.title:
                    continue
                    
                post_title_words = set(re.sub(r'[^\w\s]', '', post.title.lower()).split())
                post_title_words = {w for w in post_title_words if len(w) > 3}
                
                # If more than 50% of important words match, likely similar content
                if title_words and post_title_words:
                    word_overlap = len(title_words.intersection(post_title_words))
                    similarity_ratio = word_overlap / min(len(title_words), len(post_title_words))
                    
                    if similarity_ratio > 0.5:
                        logger.info(f"Title keyword similarity detected ({similarity_ratio:.2f}): '{article_title[:50]}...'")
                        return True
            
            # 3. OPTIMIZATION: Only use AI for borderline cases or when needed
            # Prepare content for AI comparison, using less text
            recent_content = "\n".join([
                f"Title: {post.title}"  # Removed post numbering and text, just use titles
                for post in posts_to_check
                if post.title
            ])
            
            # 4. OPTIMIZATION: Simplified prompt with fewer tokens
            prompt = f"""Compare this new article with recent posts. Are they about the same news event?

    New Article:
    Title: {article_title}
    Text: {article_text[:500]}...  

    Recent Post Titles:
    {recent_content}

    Return ONLY 'SIMILAR' if they cover the same specific news event, otherwise 'DIFFERENT'.
    """

            # 5. OPTIMIZATION: Add timeout and error handling
            try:
                response = self.model.generate_content(prompt)
                result = response.text.strip().upper() == "SIMILAR"
                logger.info(f"AI similarity check for '{article_title[:30]}...': {'SIMILAR' if result else 'DIFFERENT'}")
                return result
            except Exception as e:
                logger.error(f"Error in AI similarity check, defaulting to not similar: {e}")
                return False

        except Exception as e:
            logger.error(f"Error checking content similarity: {e}")
            return False
    
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

                service = Service(log_output=os.devnull)
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

    def fetch_article(self, url: str) -> Optional[ArticleContent]:
        """
        Fetch and parse article content using newspaper3k with paywall handling.

        Args:
            url (str): The URL of the article to fetch and parse.

        Returns:
            Optional[ArticleContent]: An instance of the ArticleContent class containing the parsed article content, or None if there was an error.

        Raises:
            PaywallError: If the article appears to be behind a paywall.

        """
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

            if not article.text or len(article.text.split()) < 50:
                known_paywall_phrases = [
                    "subscribe", "subscription", "sign in",
                    "premium content", "premium article",
                    "paid subscribers only"
                ]
                if any(phrase in article.html.lower() for phrase in known_paywall_phrases):
                    raise PaywallError(f"Content appears to be behind a paywall: {url}")

            return ArticleContent(
                url=article.url,
                title=article.title,
                text=article.text,
                summary=article.summary[:97] + "..." if len(article.summary) > 100 else article.summary,
                top_image=article.top_image
            )

        except PaywallError as e:
            logger.error(f"Paywall detected: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching article: {e}")
            return None

    def generate_tweet(self, article_text: str) -> Optional[Dict]:
        """Generate a tweet summary using Google's Gemini model.
        Returns a dictionary containing the tweet text and facets for hashtag formatting.

        Args:
            article_text (str): The text of the news article.

        Returns:
            Optional[Dict]: A dictionary containing the generated tweet text and facets for hashtag formatting.
        """
        try:
            prompt = f"""Write a very balanced tweet in approximately 200 characters about this news. No personal comments. Just the facts. Also add one hashtag at the end of the tweet that isn't '#News'. No greater than 200 characters.  
    News article text: {article_text}"""
            try:
                response = self.model.generate_content(prompt)
                tweet_text = response.text.strip()
                
                # Parse the response to find the generated hashtag
                # Look for a hashtag pattern at the end
                import re
                generated_hashtag_match = re.search(r'#(\w+)$', tweet_text)
                generated_hashtag = None
                
                # If we found a hashtag at the end, extract it and remove it from the tweet text
                if generated_hashtag_match:
                    generated_hashtag = generated_hashtag_match.group(1)  # Group 1 is the tag without the # symbol
                    tweet_text = tweet_text[:generated_hashtag_match.start()].strip()
                
                # Ensure we're within character limit (leaving room for both hashtags)
                if len(tweet_text) > 275:  # Allow room for both hashtags
                    tweet_text = tweet_text[:272] + "..."
                
                # If no hashtag was generated or found, we need to handle that case
                if not generated_hashtag:
                    # Either extract a relevant keyword from the text or use a generic tag
                    keywords = ["Update", "Breaking", "Latest", "Report"]
                    import random
                    generated_hashtag = random.choice(keywords)
                
                # Add both hashtags with proper spacing
                final_tweet = f"{tweet_text} #{generated_hashtag} #News"
                
                # Create facets for both hashtags
                facets = []
                
                # Facet for the generated hashtag
                generated_hashtag_start = len(tweet_text) + 1  # +1 for the space before hashtag
                generated_hashtag_end = generated_hashtag_start + len(generated_hashtag) + 1  # +1 for the # symbol
                
                facets.append(
                    models.AppBskyRichtextFacet.Main(
                        features=[
                            models.AppBskyRichtextFacet.Tag(
                                tag=generated_hashtag
                            )
                        ],
                        index=models.AppBskyRichtextFacet.ByteSlice(
                            byteStart=generated_hashtag_start,
                            byteEnd=generated_hashtag_end
                        )
                    )
                )
                
                # Facet for the "#News" hashtag
                news_hashtag_start = len(final_tweet) - 5  # Length of "#News"
                
                facets.append(
                    models.AppBskyRichtextFacet.Main(
                        features=[
                            models.AppBskyRichtextFacet.Tag(
                                tag="News"
                            )
                        ],
                        index=models.AppBskyRichtextFacet.ByteSlice(
                            byteStart=news_hashtag_start,
                            byteEnd=len(final_tweet)
                        )
                    )
                )
                
                return {
                    "text": final_tweet,
                    "facets": facets
                }
            except Exception as e:
                logger.error(f"Error generating tweet content: {e}")
                # Fallback to a simple tweet with both hashtags
                short_summary = article_text[:120] + "..." if len(article_text) > 120 else article_text
                
                # Add two hashtags for consistency
                final_tweet = f"New article: {short_summary} #Update #News"
                
                # Create facets for both hashtags
                facets = []
                
                # Calculate positions for the "#Update" hashtag
                update_tag_start = len(final_tweet) - 12  # Combined length of " #Update #News"
                update_tag_end = update_tag_start + 7  # Length of "#Update"
                
                facets.append(
                    models.AppBskyRichtextFacet.Main(
                        features=[
                            models.AppBskyRichtextFacet.Tag(
                                tag="Update"
                            )
                        ],
                        index=models.AppBskyRichtextFacet.ByteSlice(
                            byteStart=update_tag_start,
                            byteEnd=update_tag_end
                        )
                    )
                )
                
                # Calculate positions for the "#News" hashtag
                news_tag_start = len(final_tweet) - 5  # Length of "#News"
                
                facets.append(
                    models.AppBskyRichtextFacet.Main(
                        features=[
                            models.AppBskyRichtextFacet.Tag(
                                tag="News"
                            )
                        ],
                        index=models.AppBskyRichtextFacet.ByteSlice(
                            byteStart=news_tag_start,
                            byteEnd=len(final_tweet)
                        )
                    )
                )
                
                return {
                    "text": final_tweet,
                    "facets": facets
                }
        except Exception as e:
            logger.error(f"Error generating tweet: {e}")
            return None


    def post_to_social(self, tweet_data: Dict, article: ArticleContent) -> bool:
        """Post the article summary to AT Protocol with proper hashtag formatting.

        Args:
            tweet_data (Dict): A dictionary containing the tweet data, including the text and facets.
            article (ArticleContent): An object representing the article content, including the title, summary, URL, and image.

        Returns:
            bool: True if the article was successfully posted to social media, False otherwise.
        """
        try:
            response = requests.get(article.top_image)
            img_data = response.content
            upload = self.at_client.com.atproto.repo.upload_blob(img_data)

            embed_external = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    title=article.title,
                    description=article.summary,
                    uri=article.url,
                    thumb=upload.blob
                )
            )

            self.at_client.send_post(
                text=tweet_data["text"],
                facets=tweet_data["facets"],
                embed=embed_external
            )
            
            # Add the URL to our history file
            self._add_url_to_history(article.url)
            
            return True

        except Exception as e:
            logger.error(f"Error posting to social media: {e}")
            return False

    def get_recent_posts(self, limit: int = 30) -> List[FeedPost]:
        """
        Fetches recent posts from the AT Protocol feed.

        Args:
            limit (int): The maximum number of posts to fetch. Defaults to 30.

        Returns:
            List[FeedPost]: A list of FeedPost objects representing the recent posts.

        Raises:
            Exception: If there is an error fetching the recent posts.
        """
        try:
            profile = self.at_client.get_profile(self._get_env_var("AT_PROTOCOL_USERNAME"))
            feed = self.at_client.get_author_feed(profile.did, limit=limit)
            
            posts = []
            for post in feed.feed:
                url = None
                title = None
                
                # Extract embed data if available
                if hasattr(post.post, 'embed') and post.post.embed:
                    if hasattr(post.post.embed, 'external'):
                        url = post.post.embed.external.uri
                        title = post.post.embed.external.title

                # Extract timestamp from indexed_at field
                timestamp = None
                if hasattr(post.post, 'indexed_at'):
                    timestamp = datetime.fromisoformat(post.post.indexed_at.replace('Z', '+00:00'))
                else:
                    logger.warning(f"No timestamp found for post, using current time")
                    timestamp = datetime.now()

                # Extract text from record if available
                text = ""
                if hasattr(post.post, 'record') and hasattr(post.post.record, 'text'):
                    text = post.post.record.text
                elif hasattr(post.post, 'text'):
                    text = post.post.text

                posts.append(FeedPost(
                    text=text,
                    url=url,
                    title=title,
                    timestamp=timestamp
                ))
            
            return posts

        except Exception as e:
            logger.error(f"Error fetching recent posts: {e}")
            return []

    def select_news_article(self, candidates, recent_posts: List[FeedPost]) -> Optional[Dict]:
        """
        Selects the most newsworthy article from a list of candidates based on certain criteria.

        Args:
            candidates (list): A list of candidate articles.
            recent_posts (list): A list of recent feed posts.

        Returns:
            dict or None: A dictionary containing the URL and title of the selected article, or None if no article is selected.

        Raises:
            Exception: If there is an error processing the candidates or getting the article selection from the model.
        """
        try:
            # Generate a string of recent post titles
            recent_titles = "\n".join([
                f"- {post.title}" for post in recent_posts if post.title
            ])

            candidate_list = []
            try:
                # Process the candidates and create a list of dictionaries with URL and Title
                for row in candidates:
                    if hasattr(row, 'URL') and hasattr(row, 'Title'):
                        candidate_list.append({
                            'URL': getattr(row, 'URL'),
                            'Title': getattr(row, 'Title')
                        })
                    elif isinstance(row, (tuple, list)):
                        candidate_list.append({
                            'URL': row[0],
                            'Title': row[1]
                        })
            except Exception as e:
                logger.error(f"Error processing candidates: {e}")
                raise

            # Randomize the candidate list
            import random
            random.shuffle(candidate_list)

            # Take up to 30 items from the randomized list
            candidate_list = candidate_list[:30]

            # Generate a string of candidate titles and URLs
            candidate_titles = "\n".join([
                f"- {item['Title']} ({item['URL']})" for item in candidate_list
            ])

            # Create a prompt for selecting the most newsworthy article
            prompt = f"""Select the single most newsworthy article that:
    1. Has significant public interest or impact
    2. Represents meaningful developments rather than speculation
    3. Avoids sensationalism and clickbait

    Recent posts:
    {recent_titles}

    Candidates:
    {candidate_titles}

    Return ONLY the URL and Title in this format:
    URL: [selected URL]
    TITLE: [selected title]"""

            try:
                # Generate content using the model
                response = self.model.generate_content(prompt)
                response_text = response.text

                # Extract the URL and title from the model response
                url_line = [line for line in response_text.split('\n') if line.startswith('URL:')]
                title_line = [line for line in response_text.split('\n') if line.startswith('TITLE:')]

                if url_line and title_line:
                    return {
                        'URL': url_line[0].replace('URL:', '').strip(),
                        'Title': title_line[0].replace('TITLE:', '').strip()
                    }

                # If the response cannot be parsed correctly, select the first candidate
                if candidate_list:
                    logger.warning("Couldn't parse model response, selecting first candidate")
                    return candidate_list[0]

                return None

            except Exception as e:
                logger.error(f"Error getting article selection from model: {e}")
                # Fallback to first item if there's an error
                if candidate_list:
                    logger.warning("Model error, selecting first candidate")
                    return candidate_list[0]
                return None

        except Exception as e:
            logger.error(f"Error selecting news article: {e}")
            return None

    def process_news_feed_v2(self, news_feed_data: pd.DataFrame) -> bool:
        """Enhanced version of process_news_feed with consistent similarity checking and proper hashtag formatting.

        Args:
            news_feed_data (pd.DataFrame): The news feed data to process.

        Returns:
            bool: True if the news feed is successfully processed and posted, False otherwise.
        """
        try:
            # Get recent posts first
            recent_posts = self.get_recent_posts()
            if not recent_posts:
                logger.error("Failed to fetch recent posts")
                return False

            # Select candidate article
            selected = self.select_news_article(news_feed_data, recent_posts)
            if not selected:
                logger.error("Failed to select news article")
                return False

            logger.info(f"Selected article: {selected['Title']}")

            # Get real URL
            real_url = self.get_real_url(selected['URL'])
            if not real_url:
                return False
            
            # Check if URL is in our history file (to prevent duplicates)
            if self._is_url_in_history(real_url):
                logger.info(f"Skipping article as it's already in the URL history: {real_url}")
                return False

            # Check for known paywall domains
            known_paywall_domains = [
                'sfchronicle.com', 'wsj.com', 'nytimes.com',
                'ft.com', 'bloomberg.com', 'washingtonpost.com',
                'whitehouse.gov', 'treasury.gov', 'justice.gov',
                'fortune.com', '.gov'
            ]
            
            if any(domain in real_url.lower() for domain in known_paywall_domains):
                logger.warning(f"Skipping known paywall domain: {real_url}")
                return False

            # Fetch article content
            article = self.fetch_article(real_url)
            if not article:
                return False

            # Check for content similarity
            is_similar = self.check_content_similarity(article.title, article.text, recent_posts)
            if is_similar:
                logger.info(f"Skipping article due to similar content already posted: {article.title}")
                return False

            # Generate tweet with proper hashtag formatting
            tweet_data = self.generate_tweet(article.text)
            if not tweet_data:
                return False

            success = self.post_to_social(tweet_data, article)
            if success:
                logger.info(f"Successfully processed and posted article: {real_url}")
            return success

        except Exception as e:
            logger.error(f"Error in enhanced news feed processing: {e}")
            return False

def main():
    """Main function with retry logic.
    
    This function is the entry point of the program and contains the retry logic for processing the news feed data.
    It attempts to process the news feed multiple times with a delay between each attempt. If the processing is successful,
    the function exits. If all attempts fail, an error message is logged.
    """
    max_retries = 20  # Maximum number of retry attempts
    retry_delay = 5  # Delay between retries in seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting attempt {attempt + 1} of {max_retries}")
            
            import read_news_feed_data as rnfd
            analyzer = NewsAnalyzer()
            news_data = rnfd.get_news_feed_data()
            
            success = analyzer.process_news_feed_v2(news_data)
            if success:
                logger.info("Successfully processed news feed")
                return  # Exit successfully
            else:
                logger.error(f"Failed to process news feed on attempt {attempt + 1}")
                if attempt < max_retries - 1:  # If not the last attempt
                    logger.info(f"Waiting {retry_delay} seconds before next attempt...")
                    time.sleep(retry_delay)
                    continue

        except Exception as e:
            logger.error(f"Main execution failed on attempt {attempt + 1}: {e}", exc_info=True)
            if attempt < max_retries - 1:  # If not the last attempt
                logger.info(f"Waiting {retry_delay} seconds before next attempt...")
                time.sleep(retry_delay)
                continue
    
    logger.error(f"Failed to process news feed after {max_retries} attempts")

if __name__ == "__main__":
    main()