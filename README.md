# News Aggregation System

A robust news aggregation system with RSS feed support, designed to fetch, parse, and manage multiple RSS feeds with proper error handling and caching.

## Features

- **RSS Feed Support**: Parse RSS 2.0 and Atom feed formats
- **Error Handling**: Comprehensive error handling with retry logic
- **Caching**: Intelligent caching system to reduce unnecessary requests
- **Priority-based Refresh**: Configure different refresh intervals based on feed priority
- **Multiple Feed Support**: Manage multiple RSS feeds simultaneously
- **Logging**: Detailed logging for debugging and monitoring
- **Flexible Configuration**: Easy-to-modify configuration system

## Installation

No external dependencies are required beyond Python's standard library. Simply clone the repository:

```bash
git clone https://github.com/trashduty/injury.git
cd injury
```

## Quick Start

### Running the News Aggregator

```python
from news_aggregator import RSSFeedHandler

# Initialize the handler
handler = RSSFeedHandler()

# Get all items from all enabled feeds
items = handler.get_all_feeds()

# Display items
for item in items:
    print(f"Title: {item.get('title')}")
    print(f"Link: {item.get('link')}")
    print(f"Source: {item.get('feed_name')}")
    print()
```

Or run the included main function:

```bash
python news_aggregator.py
```

### Configuration

The system is configured through `config.py`. The default configuration includes:

```python
RSS_FEEDS = [
    {
        'url': 'https://rss.app/feeds/3j65xfmG9wfdJGvl.xml',
        'name': 'Custom RSS Feed',
        'enabled': True,
        'priority': 1
    }
]
```

## Managing RSS Feeds

### Adding a New Feed

Use the `add_rss_feed()` function to add feeds programmatically:

```python
import config

config.add_rss_feed(
    url='https://example.com/feed.xml',
    name='Example Feed',
    enabled=True,
    priority=2  # 1=high, 2=normal, 3=low
)
```

Or edit `config.py` directly and add to the `RSS_FEEDS` list:

```python
RSS_FEEDS = [
    {
        'url': 'https://example.com/feed.xml',
        'name': 'My News Feed',
        'enabled': True,
        'priority': 2
    }
]
```

### Removing a Feed

```python
import config

config.remove_rss_feed('https://example.com/feed.xml')
```

Or edit `config.py` and remove the feed entry from the `RSS_FEEDS` list.

### Disabling a Feed

To temporarily disable a feed without removing it, set `enabled` to `False`:

```python
RSS_FEEDS = [
    {
        'url': 'https://example.com/feed.xml',
        'name': 'My News Feed',
        'enabled': False,  # This feed will be skipped
        'priority': 2
    }
]
```

### Feed Priority Levels

Feeds can be assigned priority levels that determine their refresh interval:

- **Priority 1 (High)**: Refreshes every 30 minutes (1800 seconds)
- **Priority 2 (Normal)**: Refreshes every 1 hour (3600 seconds)
- **Priority 3 (Low)**: Refreshes every 2 hours (7200 seconds)

Configure refresh intervals in `config.py`:

```python
FEED_REFRESH_INTERVALS = {
    'default': 3600,        # 1 hour
    'high_priority': 1800,  # 30 minutes
    'low_priority': 7200    # 2 hours
}
```

## Configuration Options

### Feed Settings

```python
# Maximum items to retrieve per feed
MAX_ITEMS_PER_FEED = 50

# Feed request timeout in seconds
FEED_TIMEOUT = 30

# Number of retry attempts for failed requests
MAX_RETRIES = 3

# Delay between retries in seconds
RETRY_DELAY = 5

# Cache duration in seconds
CACHE_DURATION = 86400  # 24 hours
```

### Logging Configuration

```python
# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = logging.INFO

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

## API Reference

### RSSFeedHandler Class

#### Methods

**`__init__()`**
Initialize the RSS feed handler.

**`fetch_feed(feed_url: str, timeout: int = None) -> Optional[str]`**
Fetch raw RSS feed content from a URL.
- Parameters:
  - `feed_url`: The URL of the RSS feed
  - `timeout`: Request timeout in seconds (optional)
- Returns: Raw XML content as string, or None if fetch failed

**`parse_rss_feed(xml_content: str) -> List[Dict[str, Any]]`**
Parse RSS feed XML content into a list of items.
- Parameters:
  - `xml_content`: Raw XML content of the RSS feed
- Returns: List of parsed feed items

**`get_feed_items(feed_config: Dict[str, Any]) -> List[Dict[str, Any]]`**
Get items from a feed with caching support.
- Parameters:
  - `feed_config`: Feed configuration dictionary
- Returns: List of feed items

**`get_all_feeds() -> List[Dict[str, Any]]`**
Get items from all enabled feeds.
- Returns: List of all feed items from enabled feeds

**`get_feed_status() -> Dict[str, Any]`**
Get status information for all feeds.
- Returns: Dictionary with feed status information

### Configuration Functions

**`add_rss_feed(url: str, name: str, enabled: bool = True, priority: int = 1)`**
Add a new RSS feed to the configuration.

**`remove_rss_feed(url: str) -> bool`**
Remove an RSS feed from the configuration.
- Returns: True if feed was removed, False if not found

**`get_refresh_interval(priority: int) -> int`**
Get the refresh interval based on feed priority.

**`get_enabled_feeds() -> List[Dict[str, Any]]`**
Get all enabled RSS feeds.

## Supported Feed Formats

The system supports:
- **RSS 2.0**: Standard RSS format with channel and item elements
- **Atom**: Atom 1.0 syndication format

Both formats are automatically detected and parsed appropriately.

## Testing

Run the test suite:

```bash
python -m unittest test_news_aggregator.py
```

Run tests with verbose output:

```bash
python -m unittest test_news_aggregator.py -v
```

Run specific test classes:

```bash
python -m unittest test_news_aggregator.TestRSSFeedHandler
python -m unittest test_news_aggregator.TestConfig
```

## Troubleshooting

### Common Issues

#### Feed Not Loading

**Symptom**: Feed returns no items or fails to load.

**Solutions**:
1. Check the feed URL is correct and accessible:
   ```python
   from news_aggregator import RSSFeedHandler
   handler = RSSFeedHandler()
   content = handler.fetch_feed('https://your-feed-url.xml')
   print(content)  # Should show XML content
   ```

2. Verify the feed format is valid RSS or Atom:
   - Test the feed URL in a browser
   - Use an online RSS validator

3. Check for network connectivity issues:
   - Verify firewall settings
   - Check if the URL requires authentication

4. Review logs for error messages:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

#### Timeout Errors

**Symptom**: "Timeout fetching feed" in logs.

**Solutions**:
1. Increase the timeout value in `config.py`:
   ```python
   FEED_TIMEOUT = 60  # Increase to 60 seconds
   ```

2. Check network latency to the feed server

3. Verify the feed server is responding:
   ```bash
   curl -I https://your-feed-url.xml
   ```

#### Parse Errors

**Symptom**: "XML parsing error" in logs.

**Solutions**:
1. Validate the feed XML structure:
   - Check for malformed XML
   - Ensure proper encoding (UTF-8)

2. Test parsing manually:
   ```python
   from news_aggregator import RSSFeedHandler
   handler = RSSFeedHandler()
   items = handler.parse_rss_feed(xml_content)
   ```

3. Some feeds may have custom namespaces or structures not yet supported

#### No Items Returned

**Symptom**: Feed fetches successfully but returns 0 items.

**Solutions**:
1. Check if items have required fields (title or link):
   - The parser requires at least a title or link element
   
2. Verify the feed actually contains items:
   - Inspect the raw XML content

3. Check `MAX_ITEMS_PER_FEED` setting:
   ```python
   MAX_ITEMS_PER_FEED = 50  # Increase if needed
   ```

#### Stale Data

**Symptom**: Feed shows old/cached data.

**Solutions**:
1. Check refresh interval settings:
   ```python
   # Force immediate refresh by clearing cache
   handler = RSSFeedHandler()
   handler.feeds_cache.clear()
   handler.last_fetch_times.clear()
   ```

2. Adjust priority for more frequent updates:
   ```python
   RSS_FEEDS = [
       {
           'url': 'https://example.com/feed.xml',
           'priority': 1  # High priority = more frequent
       }
   ]
   ```

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
import config

config.LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
```

### Getting Feed Status

Check the status of all feeds:

```python
from news_aggregator import RSSFeedHandler

handler = RSSFeedHandler()
status = handler.get_feed_status()

print(f"Total feeds: {status['total_feeds']}")
print(f"Enabled feeds: {status['enabled_feeds']}")
print(f"Cached feeds: {status['cached_feeds']}")

for feed in status['feeds']:
    print(f"\nFeed: {feed['name']}")
    print(f"  URL: {feed['url']}")
    print(f"  Enabled: {feed['enabled']}")
    print(f"  Items cached: {feed['items_count']}")
    print(f"  Last fetch: {feed['last_fetch']}")
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.