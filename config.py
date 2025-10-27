"""
Configuration module for the news aggregation system.

This module contains configuration settings for RSS feeds,
refresh intervals, email delivery, and other system parameters.
"""

import logging
import os
from typing import List, Dict, Any

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# RSS Feed Configuration
RSS_FEEDS: List[Dict[str, Any]] = [
    {
        'url': 'https://rss.app/feeds/3j65xfmG9wfdJGvl.xml',
        'name': 'Custom RSS Feed',
        'enabled': True,
        'priority': 1
    }
]

# Feed refresh intervals (in seconds)
FEED_REFRESH_INTERVALS = {
    'default': 3600,  # 1 hour
    'high_priority': 1800,  # 30 minutes
    'low_priority': 7200  # 2 hours
}

# Feed parsing configuration
FEED_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Feed content settings
MAX_ITEMS_PER_FEED = 50
CACHE_DURATION = 86400  # 24 hours in seconds

# Email Configuration (retrieved from environment variables/GitHub Secrets)
EMAIL_CONFIG = {
    'enabled': os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true',
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': int(os.environ.get('EMAIL_PORT', '587')),
    'username': os.environ.get('EMAIL_USERNAME', ''),
    'password': os.environ.get('EMAIL_PASSWORD', ''),
    'from_email': os.environ.get('EMAIL_FROM', os.environ.get('EMAIL_USERNAME', '')),
    'to_email': os.environ.get('EMAIL_TO', ''),
    'use_tls': os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true',
    'use_ssl': os.environ.get('EMAIL_USE_SSL', 'false').lower() == 'true',
}

# Output Format Configuration
OUTPUT_CONFIG = {
    'formats': ['markdown', 'csv'],  # Supported formats
    'output_directory': os.environ.get('OUTPUT_DIR', 'reports'),
    'filename_template': 'news_report_{timestamp}',  # {timestamp} will be replaced
    'include_timestamp': True,
    'date_format': '%Y-%m-%d_%H-%M-%S',
}

# Email Template Configuration
EMAIL_TEMPLATE_CONFIG = {
    'html_template': 'templates/email_template.html',
    'text_template': 'templates/email_template.txt',
    'subject_template': 'News Aggregator Report - {date}',
    'max_items_in_summary': 10,  # Maximum items to show in email body
}


def add_rss_feed(url: str, name: str, enabled: bool = True, priority: int = 2) -> None:
    """
    Add a new RSS feed to the configuration.
    
    Args:
        url: The URL of the RSS feed
        name: A friendly name for the feed
        enabled: Whether the feed is enabled (default: True)
        priority: Priority level (1=high, 2=normal, 3=low, default: 2)
    """
    feed_config = {
        'url': url,
        'name': name,
        'enabled': enabled,
        'priority': priority
    }
    RSS_FEEDS.append(feed_config)


def remove_rss_feed(url: str) -> bool:
    """
    Remove an RSS feed from the configuration.
    
    Args:
        url: The URL of the RSS feed to remove
        
    Returns:
        True if feed was removed, False if not found
    """
    global RSS_FEEDS
    initial_length = len(RSS_FEEDS)
    RSS_FEEDS = [feed for feed in RSS_FEEDS if feed['url'] != url]
    return len(RSS_FEEDS) < initial_length


def get_refresh_interval(priority: int) -> int:
    """
    Get the refresh interval based on feed priority.
    
    Args:
        priority: Priority level (1=high, 2=normal, 3=low)
        
    Returns:
        Refresh interval in seconds
    """
    priority_map = {
        1: FEED_REFRESH_INTERVALS['high_priority'],
        2: FEED_REFRESH_INTERVALS['default'],
        3: FEED_REFRESH_INTERVALS['low_priority']
    }
    return priority_map.get(priority, FEED_REFRESH_INTERVALS['default'])


def get_enabled_feeds() -> List[Dict[str, Any]]:
    """
    Get all enabled RSS feeds.
    
    Returns:
        List of enabled feed configurations
    """
    return [feed for feed in RSS_FEEDS if feed.get('enabled', True)]
