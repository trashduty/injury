"""
Unit tests for the news aggregation system.

Tests cover configuration management, RSS feed parsing,
error handling, and feed management functionality.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import time
from urllib.error import URLError, HTTPError
import socket

import config
import news_aggregator


class TestConfig(unittest.TestCase):
    """Test cases for configuration module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Save original config
        self.original_feeds = config.RSS_FEEDS.copy()
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original config
        config.RSS_FEEDS = self.original_feeds
    
    def test_default_rss_feed_configured(self):
        """Test that the default RSS feed is configured."""
        self.assertGreaterEqual(len(config.RSS_FEEDS), 1)
        
        # Check that the required feed is present
        feed_urls = [feed['url'] for feed in config.RSS_FEEDS]
        self.assertIn('https://rss.app/feeds/3j65xfmG9wfdJGvl.xml', feed_urls)
    
    def test_add_rss_feed(self):
        """Test adding a new RSS feed."""
        initial_count = len(config.RSS_FEEDS)
        
        config.add_rss_feed(
            url='https://example.com/feed.xml',
            name='Test Feed',
            enabled=True,
            priority=2
        )
        
        self.assertEqual(len(config.RSS_FEEDS), initial_count + 1)
        
        # Verify the feed was added correctly
        new_feed = config.RSS_FEEDS[-1]
        self.assertEqual(new_feed['url'], 'https://example.com/feed.xml')
        self.assertEqual(new_feed['name'], 'Test Feed')
        self.assertTrue(new_feed['enabled'])
        self.assertEqual(new_feed['priority'], 2)
    
    def test_remove_rss_feed(self):
        """Test removing an RSS feed."""
        # Add a test feed
        test_url = 'https://test.example.com/feed.xml'
        config.add_rss_feed(test_url, 'Test Feed')
        
        initial_count = len(config.RSS_FEEDS)
        
        # Remove the feed
        result = config.remove_rss_feed(test_url)
        
        self.assertTrue(result)
        self.assertEqual(len(config.RSS_FEEDS), initial_count - 1)
        
        # Verify feed is removed
        feed_urls = [feed['url'] for feed in config.RSS_FEEDS]
        self.assertNotIn(test_url, feed_urls)
    
    def test_remove_nonexistent_feed(self):
        """Test removing a feed that doesn't exist."""
        result = config.remove_rss_feed('https://nonexistent.example.com/feed.xml')
        self.assertFalse(result)
    
    def test_get_refresh_interval(self):
        """Test getting refresh intervals based on priority."""
        # High priority
        self.assertEqual(
            config.get_refresh_interval(1),
            config.FEED_REFRESH_INTERVALS['high_priority']
        )
        
        # Normal priority
        self.assertEqual(
            config.get_refresh_interval(2),
            config.FEED_REFRESH_INTERVALS['default']
        )
        
        # Low priority
        self.assertEqual(
            config.get_refresh_interval(3),
            config.FEED_REFRESH_INTERVALS['low_priority']
        )
        
        # Unknown priority defaults to normal
        self.assertEqual(
            config.get_refresh_interval(99),
            config.FEED_REFRESH_INTERVALS['default']
        )
    
    def test_get_enabled_feeds(self):
        """Test getting only enabled feeds."""
        # Add some test feeds
        config.add_rss_feed('https://enabled1.com/feed.xml', 'Enabled 1', enabled=True)
        config.add_rss_feed('https://disabled.com/feed.xml', 'Disabled', enabled=False)
        config.add_rss_feed('https://enabled2.com/feed.xml', 'Enabled 2', enabled=True)
        
        enabled_feeds = config.get_enabled_feeds()
        
        # Check that only enabled feeds are returned
        for feed in enabled_feeds:
            self.assertTrue(feed.get('enabled', True))
        
        # Verify disabled feed is not included
        enabled_urls = [feed['url'] for feed in enabled_feeds]
        self.assertNotIn('https://disabled.com/feed.xml', enabled_urls)


class TestRSSFeedHandler(unittest.TestCase):
    """Test cases for RSS feed handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = news_aggregator.RSSFeedHandler()
        self.sample_rss = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Test Feed</title>
        <link>https://example.com</link>
        <description>Test Description</description>
        <item>
            <title>Test Item 1</title>
            <link>https://example.com/item1</link>
            <description>Description 1</description>
            <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
            <guid>item1-guid</guid>
        </item>
        <item>
            <title>Test Item 2</title>
            <link>https://example.com/item2</link>
            <description>Description 2</description>
            <pubDate>Mon, 01 Jan 2024 13:00:00 GMT</pubDate>
        </item>
    </channel>
</rss>'''
        
        self.sample_atom = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Test Atom Feed</title>
    <entry>
        <title>Atom Item 1</title>
        <link rel="alternate" href="https://example.com/atom1"/>
        <summary>Atom Description 1</summary>
        <updated>2024-01-01T12:00:00Z</updated>
        <id>atom1-id</id>
    </entry>
</feed>'''
    
    def test_parse_rss_2_0_feed(self):
        """Test parsing RSS 2.0 format feed."""
        items = self.handler.parse_rss_feed(self.sample_rss)
        
        self.assertEqual(len(items), 2)
        
        # Check first item
        self.assertEqual(items[0]['title'], 'Test Item 1')
        self.assertEqual(items[0]['link'], 'https://example.com/item1')
        self.assertEqual(items[0]['description'], 'Description 1')
        self.assertEqual(items[0]['pubDate'], 'Mon, 01 Jan 2024 12:00:00 GMT')
        self.assertEqual(items[0]['guid'], 'item1-guid')
        
        # Check second item
        self.assertEqual(items[1]['title'], 'Test Item 2')
        self.assertEqual(items[1]['link'], 'https://example.com/item2')
    
    def test_parse_atom_feed(self):
        """Test parsing Atom format feed."""
        items = self.handler.parse_rss_feed(self.sample_atom)
        
        self.assertEqual(len(items), 1)
        
        # Check item
        self.assertEqual(items[0]['title'], 'Atom Item 1')
        self.assertEqual(items[0]['link'], 'https://example.com/atom1')
        self.assertEqual(items[0]['description'], 'Atom Description 1')
        self.assertEqual(items[0]['pubDate'], '2024-01-01T12:00:00Z')
        self.assertEqual(items[0]['guid'], 'atom1-id')
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML returns empty list."""
        invalid_xml = "This is not valid XML"
        items = self.handler.parse_rss_feed(invalid_xml)
        self.assertEqual(len(items), 0)
    
    def test_parse_empty_feed(self):
        """Test parsing feed with no items."""
        empty_rss = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Empty Feed</title>
    </channel>
</rss>'''
        items = self.handler.parse_rss_feed(empty_rss)
        self.assertEqual(len(items), 0)
    
    def test_max_items_limit(self):
        """Test that parsing respects MAX_ITEMS_PER_FEED limit."""
        # Create RSS with many items
        items_xml = ''.join([
            f'<item><title>Item {i}</title><link>https://example.com/item{i}</link></item>'
            for i in range(config.MAX_ITEMS_PER_FEED + 10)
        ])
        
        large_rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Large Feed</title>
        {items_xml}
    </channel>
</rss>'''
        
        items = self.handler.parse_rss_feed(large_rss)
        self.assertLessEqual(len(items), config.MAX_ITEMS_PER_FEED)
    
    @patch('news_aggregator.urlopen')
    def test_fetch_feed_success(self, mock_urlopen):
        """Test successful feed fetching."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'<rss>test</rss>'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response
        
        content = self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertEqual(content, '<rss>test</rss>')
        mock_urlopen.assert_called_once()
    
    @patch('news_aggregator.urlopen')
    def test_fetch_feed_http_error(self, mock_urlopen):
        """Test handling of HTTP errors."""
        mock_urlopen.side_effect = HTTPError(
            'https://example.com/feed.xml',
            404,
            'Not Found',
            {},
            None
        )
        
        content = self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertIsNone(content)
    
    @patch('news_aggregator.urlopen')
    def test_fetch_feed_url_error(self, mock_urlopen):
        """Test handling of URL errors."""
        mock_urlopen.side_effect = URLError('Connection refused')
        
        content = self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertIsNone(content)
    
    @patch('news_aggregator.urlopen')
    def test_fetch_feed_timeout(self, mock_urlopen):
        """Test handling of timeout errors."""
        mock_urlopen.side_effect = socket.timeout()
        
        content = self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertIsNone(content)
    
    @patch('news_aggregator.urlopen')
    def test_fetch_feed_retry_logic(self, mock_urlopen):
        """Test retry logic for failed fetches."""
        mock_urlopen.side_effect = URLError('Connection refused')
        
        # Fetch should retry MAX_RETRIES times
        self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertEqual(mock_urlopen.call_count, config.MAX_RETRIES)
    
    @patch('news_aggregator.urlopen')
    @patch('news_aggregator.time.sleep')
    def test_fetch_feed_eventual_success(self, mock_sleep, mock_urlopen):
        """Test that retries eventually succeed."""
        # Fail twice, then succeed
        mock_response = MagicMock()
        mock_response.read.return_value = b'<rss>success</rss>'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        
        mock_urlopen.side_effect = [
            URLError('Connection refused'),
            URLError('Connection refused'),
            mock_response
        ]
        
        content = self.handler.fetch_feed('https://example.com/feed.xml')
        
        self.assertEqual(content, '<rss>success</rss>')
        self.assertEqual(mock_urlopen.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('news_aggregator.RSSFeedHandler.fetch_feed')
    @patch('news_aggregator.RSSFeedHandler.parse_rss_feed')
    def test_get_feed_items(self, mock_parse, mock_fetch):
        """Test getting feed items with caching."""
        mock_fetch.return_value = self.sample_rss
        mock_parse.return_value = [
            {'title': 'Item 1', 'link': 'https://example.com/1'},
            {'title': 'Item 2', 'link': 'https://example.com/2'}
        ]
        
        feed_config = {
            'url': 'https://example.com/feed.xml',
            'name': 'Test Feed',
            'priority': 2
        }
        
        items = self.handler.get_feed_items(feed_config)
        
        self.assertEqual(len(items), 2)
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once()
    
    @patch('news_aggregator.RSSFeedHandler.fetch_feed')
    @patch('news_aggregator.RSSFeedHandler.parse_rss_feed')
    def test_get_feed_items_caching(self, mock_parse, mock_fetch):
        """Test that feed items are cached."""
        mock_fetch.return_value = self.sample_rss
        mock_parse.return_value = [{'title': 'Item 1'}]
        
        feed_config = {
            'url': 'https://example.com/feed.xml',
            'name': 'Test Feed',
            'priority': 1  # High priority for shorter cache time
        }
        
        # First fetch
        items1 = self.handler.get_feed_items(feed_config)
        
        # Second fetch should use cache
        items2 = self.handler.get_feed_items(feed_config)
        
        self.assertEqual(items1, items2)
        # Fetch should only be called once due to caching
        mock_fetch.assert_called_once()
    
    @patch('news_aggregator.RSSFeedHandler.get_feed_items')
    def test_get_all_feeds(self, mock_get_items):
        """Test getting items from all enabled feeds."""
        mock_get_items.return_value = [
            {'title': 'Item 1', 'link': 'https://example.com/1'}
        ]
        
        all_items = self.handler.get_all_feeds()
        
        # Should call get_feed_items for each enabled feed
        enabled_count = len(config.get_enabled_feeds())
        self.assertEqual(mock_get_items.call_count, enabled_count)
        
        # Check that feed_name is added to items
        for item in all_items:
            self.assertIn('feed_name', item)
    
    def test_get_feed_status(self):
        """Test getting feed status information."""
        status = self.handler.get_feed_status()
        
        self.assertIn('total_feeds', status)
        self.assertIn('enabled_feeds', status)
        self.assertIn('cached_feeds', status)
        self.assertIn('feeds', status)
        
        self.assertIsInstance(status['feeds'], list)
        self.assertEqual(status['total_feeds'], len(config.RSS_FEEDS))
    
    @patch('news_aggregator.RSSFeedHandler.fetch_feed')
    def test_stale_cache_fallback(self, mock_fetch):
        """Test that stale cache is used when fetch fails."""
        # First successful fetch
        mock_fetch.return_value = self.sample_rss
        
        feed_config = {
            'url': 'https://example.com/feed.xml',
            'name': 'Test Feed',
            'priority': 1
        }
        
        # Populate cache
        items1 = self.handler.get_feed_items(feed_config)
        self.assertGreater(len(items1), 0)
        
        # Wait for cache to expire
        time.sleep(0.1)
        # Force cache expiration
        self.handler.last_fetch_times[feed_config['url']] = 0
        
        # Simulate fetch failure
        mock_fetch.return_value = None
        
        # Should return stale cache
        items2 = self.handler.get_feed_items(feed_config)
        self.assertEqual(len(items2), len(items1))


if __name__ == '__main__':
    unittest.main()
