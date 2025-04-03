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
python news_poster_V3.py
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

The table has this format:

| URL | Title |
|-----|-------|
| [Link](https://news.google.com/rss/articles/CBMiqgFBVV95cUxPa2R1Qk1OMFlIbVNrR2lySW5BeXZwNWwxSUJVS2haZ25rd1Jfd2pjU1hhNmkwTFlscHBnTnpvdzhEQnRwbng5T3BwZzJreUZuZUNxcklUQUpGSWNBVkp4c3poQ0FnZzM0UkhockprR0FuWlRjTWNEbFF1OHBPbWlwYjR2SGNqTEwtdldCOUowSHFpMjQ0RUlfYURPMzNqRTVzai0xZzBBMWJFUQ?oc=5) | Mayor Eric Adams' case dismissed with prejudice despite Trump admin's request to allow for later prosecution - ABC News |
| [Link](https://news.google.com/rss/articles/CBMipAFBVV95cUxPckVuNkFqclBocExaZkZYZE5IVE10c3VlcU5fYkpHcUFtQ2M0MzJxcWF6QUwtMjIySmw4ZFJXS3RsbGxpM1RJU0RPcUpGWWtUaEN1R1NfaWR0R2dBdWFQeVFna25OeUJYOHVycW5sNGEzREhnRy1mSkt6UVpYN0RPOVBXaVJVNnpFeGM5bkVaM1Zhbzl1NU4yQlhfUWlmbGVTYUxXLdIBqgFBVV95cUxPeVIweXVIUjVsWFFTMjNkSDI1X2RadVJEM01NZFNzc3ZjOGZxdHh0ZEtTYkVac3FfZy1PQ2ZjUVlhNTFpa0s2VjhvcEtSQklWRngxWUZfeXhRNW9HWXhoWVhMcHFwTk84WVhkLU9FN0NKVG5aMm1oUkkyaHc2SDVsZ1hubGZHSFZXYjBaN21SS3ZrMXhGc09lMEN5OFgtdXhpSnVHTHVhX0R3QQ?oc=5) | Remains of 4th missing US soldier found in Lithuania - ABC News |
| [Link](https://news.google.com/rss/articles/CBMikgFBVV95cUxOclBiMmhDRHZHSVRDTlpRRUtJNTJUNXJFaVVaUmh6eW96ZkpQVTR4V01yMWxVUnlYWnZzNGFJWFZNM2hhSmczNjU1bkRWV0MtN2lsTW1pT2o0WDRYbTQ4UzhfUTFxYVFPeWs3NUY1SE5IWmZmalZwWURkdEhlWGJwelZPTkFVT1k5Qjl5UWU2UFl4dw?oc=5) | Some Aid Workers Killed in Gaza Were Shot Multiple Times, Officials Say - The New York Times |
| [Link](https://news.google.com/rss/articles/CBMiqgFBVV95cUxPa2R1Qk1OMFlIbVNrR2lySW5BeXZwNWwxSUJVS2haZ25rd1Jfd2pjU1hhNmkwTFlscHBnTnpvdzhEQnRwbng5T3BwZzJreUZuZUNxcklUQUpGSWNBVkp4c3poQ0FnZzM0UkhockprR0FuWlRjTWNEbFF1OHBPbWlwYjR2SGNqTEwtdldCOUowSHFpMjQ0RUlfYURPMzNqRTVzai0xZzBBMWJFUdIBrwFBVV95cUxOeGM3RGdPV2FzTDFVcjRqWGE2aHRnd21lVlF1bEZFSUtlNnNKMnR1blhQa3hyOVZVeDlaWUpPVFVBaXZ2WXFSTDBWVzdFdXRFTGVGSW55R3FlOE1BT3RNQ1hXbFdPcE1Eck96M1ZTYnQ0RUZ2QTJHd0Q5RGljaFJORjBndS11bVBSSU05OWV2QkZqSVdKZ3laMF9ycXZzMlp0bm9tTlVvUmFPWVE2MW5v?oc=5) | Mayor Eric Adams' case dismissed with prejudice despite Trump admin's request to allow for later prosecution - ABC News |
| [Link](https://news.google.com/rss/articles/CBMiWkFVX3lxTE1HQVA3Mkdsb2dPcmd5M0FIU3RhR3JCckRzNjlzVDB5Yk5BamlqTHBNd1ZqVGlvVG44SUlOZFhSN3JBaFJXS1JFbVBFRG5pVUpHWGpfT0ZwR180QdIBX0FVX3lxTE9HRW9LV3ZDSDUzNnM2TklGa1dWZ2lLN01ZV19rOEQ5QXJ5cXo1dk9Gb0VIQTZIOG5lT1NoX3RMdlVhc2o4akZRcm5FN2Z4ejNFRWh5Y3IyY2JnUTIzX1pz?oc=5) | Muse and Robbie Williams face pressure to cancel Turkish gigs - BBC |
| [Link](https://news.google.com/rss/articles/CBMiWkFVX3lxTE4zUGFZMi1xNXBGMG5hVUhrUGI2YTh0U1dmV0NhaFRDRFZVRDBzcUlVVFBrVS1qY2ROcUxCN0FtdUp2M2VhMFdjc1MwOFl0V2RfQzRjYnpzMEZ4Zw?oc=5) | Waqf bill: India Lok Sabha passes controversial bill on Muslim properties - BBC |
| [Link](https://news.google.com/rss/articles/CBMipgFBVV95cUxNbmtkRDJmMExiNk1UQmxJNkRVWldpRjVFbjhISmYxRG9obWdPN3dBd2lZR1lGRV9RMnpNTVpsdHFzclpTVGMwVWhBbzlBM3VnRk5Qd1NLeEM3QnB2NXZycW1CTm5TMUdVX3NCY1E5N3hQT0JEQXdLcGxKRk9NdHRxOEpsRnU5X0hLMWtSTW53b1ctWWF0d1BDMER1LWhhVTdPdk92MER30gGrAUFVX3lxTE1iMFdsUDl3enp6Rms5OGNVZDVlNFVTNHdEQmZubE1MeXJVWlRHMl80NFdocVlzSy1paXVlbUF2YmwwSWNlZXVpME10YkZGMnltZmlFaVNTOXZmOExQeE9uVFVfTWk4ZE9pVVd6dUVqLWhhRmZiQmFVeHE1NnBBZUFGQVhBeDVWSGNVSnowRjlURkNMLXpBX0ZBT2owMXBVa3RCVlFaYWU0ZW5rMA?oc=5) | Musk still plans a major role in midterm elections despite loss in Wisconsin: Sources - ABC News |
| [Link](https://news.google.com/rss/articles/CBMieEFVX3lxTE5NZEtIb2NXNjlvbkJFdENRWnl5R283bHdxS01HQ2JfVlg1NHAxYXk5enJoQnVHSE9UMVVPOUhaalEzUzhLd2lNQXBZR2ItQVNadThGRHJpdURmMEFuZ1BzMTZHZDd0cE1DcnJwR2tPd0xMMjFTcHVtOA?oc=5) | Supreme Court Sides With Truck Driver Fired Over Drug Test - The New York Times |
| [Link](https://news.google.com/rss/articles/CBMimgFBVV95cUxPRGZoS2FWclJUd0lNQlN5ZDlqdnk4MjR1M2g0VFA3bW9TbEVRcjBKRjB3WWNtTUc5Y3ZFX2FoVDRabHBuLUxPVXRLam9rajdVcUE2TDdlb1JlQ0ItbDNKSER5ZXZ4N0t2dXh2cURkNGpMdDY2ZGloRHVtelZYOHBaRUh4LWtXZ0JZcENRQ05sRm1ndVNBZDZldy1B0gGfAUFVX3lxTFBDVGNKaV9wTmU3bGctektrYm52SjV5VDdTTWZIWkpVVjhaRW9zNnlXaEIzcGtTemZrb3Fkdi1FaFFadmFMOHFtVWxiRDAwdk9VcUQ4Z0xxbWxzOEVLdzI1cG92d3FoUUdsc29wS0dKbVF1eGUtTkdiN3ZldEJqcjNld1ppb1RKYTRnYlA5bFpOOUszM1NscDlNdmp6dzBJZw?oc=5) | Trump Administration Explores Costly Option For Greenland Takeover: Report - HuffPost |
| [Link](https://news.google.com/rss/articles/CBMimwFBVV95cUxNbXByY0xxbFZPZlBXWDRXWE55OWhQTmRvQXRvQ2pudTd4WG5PVXltYW1hSzBYeDVKSmRKZFBIQlFpQ1ktZ1BSTDRPZjgwa2dNaGR4aHVtZ0RXUDk3Ymk2Vzh3QkwzQVoyS2RmTUpQaXprTHY4ckRhWDhkVjZFa2RPT0Nhcm9BQ1ZzVDdiQWhLOWxQSXlpQTFEX1lMZw?oc=5) | Trump tariffs: List of global responses and countermeasures - Reuters |


## Author

Eric Ness
