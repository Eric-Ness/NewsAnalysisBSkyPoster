# Automated News Poster for AT Protocol

This application automatically selects newsworthy articles from various sources and posts summaries to the AT Protocol (Bluesky) social network. It uses Google's Gemini AI to determine the most newsworthy content and generate balanced summaries, avoiding duplicates and paywalled content.

The primary reason I am releasing this is to be transparent in the prompts that are used to run the feed.

## Bluesky 

https://bsky.app/profile/newsanalysis.com

## Features

- Automated selection of newsworthy articles from various sources
- AI-powered article evaluation and summary generation
- Paywall detection and avoidance
- Duplicate content detection to prevent posting similar stories
- History tracking to avoid reposting the same URLs
- Proper hashtag formatting for AT Protocol posts
- Error handling and retry logic

## Requirements

- Python 3.8+
- Required Python packages:
  - atproto
  - newspaper3k
  - pandas
  - nltk
  - selenium
  - google.generativeai
  - python-dotenv
  - requests

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/news-poster.git
   cd news-poster
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your credentials (see `.env.example` for reference)

4. Ensure you have a compatible Chrome driver installed for Selenium

## Configuration

Create a `.env` file in the project root with the following variables:

```
# Database Configuration
DB_SERVER=your_server_address
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# AT Protocol (Bluesky) Credentials
AT_PROTOCOL_USERNAME=your_bluesky_handle
AT_PROTOCOL_PASSWORD=your_bluesky_password

# API Keys
GOOGLE_AI_API_KEY=your_google_ai_api_key
```

See `.env.example` for a complete template.

## Usage

Run the script with:

```
python main.py
```

The script will:
1. Fetch candidate news articles
2. Use AI to select the most newsworthy article
3. Extract the content and generate a summary
4. Post the summary to your AT Protocol (Bluesky) feed with appropriate hashtags
5. Track posted URLs to avoid duplicates

## Scheduling

This script is designed to be run as a scheduled task. You can use cron (Linux/Mac) or Task Scheduler (Windows) to run it at regular intervals.

### Example cron job (Linux/Mac)

To run the script every hour:

```
0 * * * * cd /path/to/news-poster && python main.py >> /path/to/logfile.log 2>&1
```

## Customization

- Modify the `known_paywall_domains` list in the `process_news_feed_v2` method to add or remove domains
- Adjust the `max_history_lines` and `cleanup_threshold` values to control the URL history file size
- Change the similarity checking parameters in the `check_content_similarity` method to be more or less strict

## News Feed Datasource

The news source primary feed comes from the https://news.google.com rss feed.

## Author

Eric Ness
