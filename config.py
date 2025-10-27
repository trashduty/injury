"""
Configuration settings and constants for the football news aggregator.
"""

import os

# Email Configuration
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')

# RSS Feed Sources
RSS_FEEDS = [
    {
        'name': 'ESPN College Football',
        'url': 'https://www.espn.com/espn/rss/ncf/news',
        'keywords': ['injury', 'injuries', 'depth chart', 'out for season', 'questionable', 'doubtful', 'ruled out']
    },
    {
        'name': 'CBS Sports College Football',
        'url': 'https://www.cbssports.com/rss/headlines/college-football/',
        'keywords': ['injury', 'injuries', 'depth chart', 'out for season', 'questionable', 'doubtful', 'ruled out']
    },
    {
        'name': 'Sports Illustrated College Football',
        'url': 'https://www.si.com/rss/si_ncaaf.rss',
        'keywords': ['injury', 'injuries', 'depth chart', 'out for season', 'questionable', 'doubtful', 'ruled out']
    }
]

# Rate Limiting
REQUEST_TIMEOUT = 10  # seconds
REQUEST_DELAY = 2  # seconds between requests

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# News Filtering
MAX_NEWS_AGE_HOURS = 72  # Only include news from the last 72 hours
MAX_ARTICLES_PER_FEED = 20  # Maximum articles to process per feed

# Report Configuration
REPORT_SUBJECT = 'College Football News Report - Injuries & Depth Charts'
