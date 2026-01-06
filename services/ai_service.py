"""
AI Service Module

This module handles AI operations using Google's Gemini API.
It provides functionality for content generation, article selection,
and assessing article similarity.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import re

import google.generativeai as genai
from atproto import models

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class FeedPost:
    """Data class to store AT Protocol feed post content."""
    text: str
    url: Optional[str]
    title: Optional[str]
    timestamp: datetime

class AIService:
    """Service for AI operations with Google's Gemini API."""
    
    def __init__(self):
        """
        Initialize the AI service with the Gemini API.
        
        Configures the API key and selects an appropriate model based on availability.
        """
        # Initialize Gemini AI
        api_key = settings.GOOGLE_AI_API_KEY
        if not api_key:
            raise ValueError("Missing required GOOGLE_AI_API_KEY")
            
        genai.configure(api_key=api_key)
        
        # Get available models
        try:
            models_list = genai.list_models()
            available_models = [m.name for m in models_list]
            
            # Select a model based on preference order
            model_name = None
            for preferred in settings.DEFAULT_AI_MODELS:
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
            
            logger.info(f"Selected AI model: {model_name}")
            
            # Initialize model with the complete model path
            self.model = genai.GenerativeModel(model_name=model_name)
            
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {e}")
            raise
    
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
            # Optimize: Reduce number of posts to compare against
            posts_to_check = recent_posts[:settings.SIMILARITY_CHECK_POSTS_LIMIT]
            
            # Add basic keyword matching as a pre-filter
            # Extract important keywords from title (simple approach)
            title_words = set(re.sub(r'[^\w\s]', '', article_title.lower()).split())
            title_words = {w for w in title_words if len(w) > settings.MIN_KEYWORD_LENGTH}  # Only keep meaningful words
            
            # Check for basic title similarity first (cheaper than AI check)
            for post in posts_to_check:
                if not post.title:
                    continue
                    
                post_title_words = set(re.sub(r'[^\w\s]', '', post.title.lower()).split())
                post_title_words = {w for w in post_title_words if len(w) > settings.MIN_KEYWORD_LENGTH}
                
                # If more than 50% of important words match, likely similar content
                if title_words and post_title_words:
                    word_overlap = len(title_words.intersection(post_title_words))
                    similarity_ratio = word_overlap / min(len(title_words), len(post_title_words))
                    
                    if similarity_ratio > settings.TITLE_SIMILARITY_THRESHOLD:
                        logger.info(f"Title keyword similarity detected ({similarity_ratio:.2f}): '{article_title[:50]}...'")
                        return True
            
            # Only use AI for borderline cases
            # Prepare content for AI comparison, using less text
            recent_content = "\n".join([
                f"Title: {post.title}"  # Just use titles for comparison
                for post in posts_to_check
                if post.title
            ])
            
            # Simplified prompt with fewer tokens
            prompt = f"""Compare this new article with recent posts. Are they about the same news event?

New Article:
Title: {article_title}
Text: {article_text[:settings.AI_COMPARISON_TEXT_LENGTH]}...  

Recent Post Titles:
{recent_content}

Return ONLY 'SIMILAR' if they cover the same specific news event, otherwise 'DIFFERENT'.
"""

            # Add timeout and error handling
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
    
    def select_news_articles(self, candidates: List[Dict[str, Any]], recent_posts: List[FeedPost], max_count: int = 3) -> List[Dict[str, Any]]:
        """
        Selects multiple newsworthy articles from a list of candidates in order of priority.

        Args:
            candidates: A list of candidate articles with URL, Title, and News_Feed_ID.
            recent_posts: A list of recent feed posts.
            max_count: Maximum number of articles to select.

        Returns:
            List[Dict]: The selected articles in priority order, empty list if no articles selected.
        """
        try:
            # Take up to CANDIDATE_SELECTION_LIMIT items from the randomized list
            import random
            random_candidates = candidates.copy()
            random.shuffle(random_candidates)
            candidate_list = random_candidates[:settings.CANDIDATE_SELECTION_LIMIT]

            # Generate a string of recent post titles
            recent_titles = "\n".join([
                f"- {post.title}" for post in recent_posts if post.title
            ])

            # Generate a string of candidate titles and URLs
            candidate_titles = "\n".join([
                f"- {item['Title']} ({item['URL']})" for item in candidate_list
            ])

            # Create a prompt for selecting multiple newsworthy articles
            prompt = f"""Select the {max_count} most newsworthy articles that:
1. Have significant public interest or impact
2. Represent meaningful developments rather than speculation
3. Avoid sensationalism and clickbait
4. Cover diverse topics (not all about the same subject)
5. Imagine you are Edward R. Murrow, a legendary journalist known for his integrity and commitment to factual reporting.
6. Prioritize articles that maybe breaking news or significant updates.
7. Avoid articles that are probably pseudo-news, pseudo-science or speculative in nature.
8. Nothing that is essentially a press release or promotional content.
9. Nothing to do with celebrity gossip, sports, or entertainment unless it has significant societal impact.
10. Avoid articles that are too similar to recent posts.
11. Avoid articles that talk about loans, mortgages, or financial products unless they are significant news events.
12. Avoid articles that feature sales for websites, products, or services unless they are significant news events. Like Amazon Prime Day or Black Friday.
13. Absolutely no articles from known fake news, unreliable sources or religious sites.
14. News from religious sites is not acceptable unless it is a major world event covered by mainstream media.
15. No Obituaries or memorials, unless they are of major public figures with significant societal impact.
16. No .gov or .mil sites. 
 .

Recent posts:
{recent_titles}

Candidates:
{candidate_titles}

Return ONLY the URLs and Titles in this format, ordered from most to least important:
1. URL: [first URL]
   TITLE: [first title]
2. URL: [second URL]
   TITLE: [second title]
...and so on"""

            try:
                # Generate content using the model
                response = self.model.generate_content(prompt)
                response_text = response.text
                
                # Parse and extract ranked articles
                selected_articles = []
                
                # Regular expression to extract numbered items with URL and TITLE
                pattern = r'(\d+)\.\s+URL:\s+(.*?)\s+TITLE:\s+(.*?)(?=\n\d+\.|\Z)'
                matches = re.findall(pattern, response_text, re.DOTALL)
                
                for _, url, title in matches:
                    url = url.strip()
                    title = title.strip()
                    
                    # Find the corresponding News_Feed_ID
                    selected_item = next(
                        (item for item in candidate_list if item['URL'] == url),
                        None
                    )
                    
                    if selected_item:
                        selected_articles.append({
                            'URL': url,
                            'Title': title,
                            'News_Feed_ID': selected_item['News_Feed_ID']
                        })
                
                if selected_articles:
                    return selected_articles[:max_count]
                
            except Exception as e:
                logger.error(f"Error parsing AI response for article selection: {e}")
            
            # Fallback: use top candidates if AI selection fails
            logger.warning("Falling back to direct candidate selection")
            return [
                {
                    'URL': item['URL'],
                    'Title': item['Title'],
                    'News_Feed_ID': item['News_Feed_ID']
                }
                for item in candidate_list[:max_count]
            ]

        except Exception as e:
            logger.error(f"Error selecting news articles: {e}")
            # Return a few random candidates as fallback
            if candidates and len(candidates) > 0:
                logger.warning("Using random candidates due to error")
                return [
                    {
                        'URL': item['URL'],
                        'Title': item['Title'],
                        'News_Feed_ID': item['News_Feed_ID']
                    }
                    for item in random_candidates[:max_count]
                ]
            return []
    
    def select_news_article(self, candidates: List[Dict[str, Any]], recent_posts: List[FeedPost]) -> Optional[Dict[str, Any]]:
        """
        Selects the most newsworthy article from a list of candidates.

        Args:
            candidates: A list of candidate articles with URL, Title, and News_Feed_ID.
            recent_posts: A list of recent feed posts.

        Returns:
            Optional[Dict]: The selected article, or None if no article is selected.
        """
        articles = self.select_news_articles(candidates, recent_posts, max_count=1)
        return articles[0] if articles else None
    
    def generate_tweet(self, article_text: str, article_title: str, article_url: str) -> Optional[Dict[str, Any]]:
        """
        Generate a tweet-like post for an article using AI, including hashtags and facets.
        
        Args:
            article_text: The full text of the article
            article_title: The title of the article
            article_url: The URL of the article
            
        Returns:
            Optional[Dict]: Dictionary with tweet text, summary, and facets for hashtag formatting
        """
        try:
            # Limit article text to reduce token usage
            truncated_text = article_text[:settings.ARTICLE_TEXT_TRUNCATE_LENGTH] if article_text else ""
            
            prompt = f"""Create a brief, informative social media post for the following news article.
            
Article Title: {article_title}
Article URL: {article_url}
Article Content: {truncated_text}

Requirements:
1. Be factual and objective - no editorializing or opinions
2. Include the most important information only (who, what, where, when)
3. Keep it under {settings.TWEET_CHARACTER_LIMIT} characters (excluding hashtags)
4. Use neutral, straightforward language
5. Add ONE relevant hashtag at the end that best represents the subject or category

Format your response as:
TWEET: [your tweet text]
HASHTAG: [one relevant hashtag without the # symbol]
SUMMARY: [one sentence summary of the article]"""

            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract the components from the response
            tweet_line = [line for line in response_text.split('\n') if line.startswith('TWEET:')]
            hashtag_line = [line for line in response_text.split('\n') if line.startswith('HASHTAG:')]
            summary_line = [line for line in response_text.split('\n') if line.startswith('SUMMARY:')]
            
            if not tweet_line:
                logger.warning("No tweet text found in AI response")
                return None
                
            tweet_text = tweet_line[0].replace('TWEET:', '').strip()
            
            # Extract the generated hashtag
            generated_hashtag = None
            if hashtag_line:
                generated_hashtag = hashtag_line[0].replace('HASHTAG:', '').strip()
                # Remove # if it was included
                if generated_hashtag.startswith('#'):
                    generated_hashtag = generated_hashtag[1:]
            
            # If no hashtag was found or it's invalid, use a fallback
            if not generated_hashtag or not re.match(r'^\w+$', generated_hashtag):
                keywords = ["Update", "Breaking", "Latest", "Report"]
                import random
                generated_hashtag = random.choice(keywords)
            
            # Add hashtags with proper spacing
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
            news_hashtag_start = len(tweet_text) + len(generated_hashtag) + 3  # Space + # + tag + space
            news_hashtag_end = news_hashtag_start + 5  # Length of "#News"
            
            facets.append(
                models.AppBskyRichtextFacet.Main(
                    features=[
                        models.AppBskyRichtextFacet.Tag(
                            tag="News"
                        )
                    ],
                    index=models.AppBskyRichtextFacet.ByteSlice(
                        byteStart=news_hashtag_start,
                        byteEnd=news_hashtag_end
                    )
                )
            )
            
            # Get summary if available
            summary_text = ""
            if summary_line:
                summary_text = summary_line[0].replace('SUMMARY:', '').strip()
            
            return {
                'tweet_text': final_tweet,
                'summary': summary_text,
                'facets': facets
            }
                
        except Exception as e:
            logger.error(f"Error generating tweet: {e}")
            return None 