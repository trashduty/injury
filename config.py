"""
Configuration module for the news aggregation system.

This module contains configuration settings for RSS feeds,
refresh intervals, and other system parameters.
"""

import logging
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


def add_rss_feed(url: str, name: str, enabled: bool = True, priority: int = 1) -> None:
    """
    Add a new RSS feed to the configuration.
    
    Args:
        url: The URL of the RSS feed
        name: A friendly name for the feed
        enabled: Whether the feed is enabled (default: True)
        priority: Priority level (1=high, 2=normal, 3=low)
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
