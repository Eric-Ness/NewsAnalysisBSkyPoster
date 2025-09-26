# News Poster

A Python application for automatically selecting and posting newsworthy articles to BlueSky (AT Protocol).

## Overview

News Poster is designed to automate the process of selecting, processing, and posting news articles to the AT Protocol (BlueSky) social network. The application:

1. Retrieves news article candidates from a database
2. Uses Google's Gemini AI to select the most newsworthy article
3. Fetches the article content, handling paywalls and content extraction
4. Generates a concise, informative social media post
5. Posts the content to BlueSky
6. Updates the database with information about the posted article

## Features

- **AI-Powered Article Selection**: Uses Gemini AI to select articles based on newsworthiness
- **Content Similarity Detection**: Avoids posting articles too similar to recent posts
- **Paywall Detection**: Identifies and skips articles behind paywalls
- **URL History Tracking**: Maintains a record of previously posted URLs to avoid duplicates
- **Automated Social Media Posting**: Posts to BlueSky with article preview and link
- **Database Integration**: Works with a SQL Server database to track articles and update status

## Project Structure

```text
news-poster/
├── config/
│   ├── __init__.py
│   └── settings.py           # Centralized configuration settings
├── data/
│   ├── __init__.py
│   └── database.py           # Consolidated database operations
├── services/
│   ├── __init__.py
│   ├── article_service.py    # Article fetching and processing
│   ├── ai_service.py         # AI/ML operations with Gemini
│   └── social_service.py     # AT Protocol integration
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Centralized logging
│   └── helpers.py            # Helper functions
├── main.py                   # Application entry point
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:

   ```python
   git clone <repository-url>
   cd news-poster
   ```

2. Create a virtual environment and install dependencies:

   ```python
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration (see `.env.example` for template)

## Usage

Run the application with the following command:

```python
python main.py
```

### Command-line Arguments

- `--test`: Run in test mode without posting to social media
- `--log-file`: Specify a custom log file (default: news_poster.log)
- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR)

Example:

```python
python main.py --test --log-level DEBUG
```

## Dependencies

- Python 3.8+
- Google Generative AI (Gemini)
- ATProto (BlueSky) Client
- newspaper3k (Article extraction)
- pyodbc (Database connectivity)
- pandas (Data manipulation)
- selenium (Web scraping)

## Configuration

The application is configured through environment variables. Copy `.env.example` to `.env` and fill in the required values:

- `GOOGLE_AI_API_KEY`: Your Google AI API key for Gemini
- `AT_PROTOCOL_USERNAME`: Your BlueSky username
- `AT_PROTOCOL_PASSWORD`: Your BlueSky password
- Database configuration: `server`, `db`, `user`, `pwd`

## Change Log

**2025.09.25** – Updated Gemini Models List
**2025.08.05** – feat: Add PR Newswire to paywall domains list and increase total results in SQL query.  
**2025.07.06** – Blacklisted a couple of sites and trying to avoid sales articles like Amazon Prime Day.  
**2025.04.21** – Updated data retrieval – world news 50%, national 40%, business 10%.  
**2025.04.19** – Re-added hashtag creation.  
**2025.04.18** – Bug fix for paywalled sites. Added government sites to block.  
**2025.04.14** – Major restructure, no longer a monolith py file.  
**2025.04.13** – Keep track of bsky posts, extracted article text, and pertinent URLs.  
**2025.04.11** – Increased amount of news LLM could choose from 120 to 160 news items.  
**2025.04.10** – Added business news to the data feed.
