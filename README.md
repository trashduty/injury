# News Aggregation System

A robust news aggregation system with RSS feed support, email delivery, and dual-format reporting (Markdown and CSV). Designed to fetch, parse, and manage multiple RSS feeds with proper error handling, caching, and automated email notifications.

## Features

- **RSS Feed Support**: Parse RSS 2.0 and Atom feed formats
- **Error Handling**: Comprehensive error handling with retry logic
- **Caching**: Intelligent caching system to reduce unnecessary requests
- **Priority-based Refresh**: Configure different refresh intervals based on feed priority
- **Multiple Feed Support**: Manage multiple RSS feeds simultaneously
- **Logging**: Detailed logging for debugging and monitoring
- **Flexible Configuration**: Easy-to-modify configuration system
- **Dual-Format Reports**: Generate reports in both Markdown and CSV formats
- **Email Delivery**: Send automated email notifications with report attachments
- **HTML Email Templates**: Beautiful HTML email templates with plain text fallback
- **Secure Configuration**: Email credentials stored securely via environment variables

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

### Running with Report Generation and Email Delivery

The system can automatically generate reports and send them via email:

```bash
# Set environment variables for email configuration
export EMAIL_ENABLED=true
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USERNAME=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
export EMAIL_TO=recipient@email.com

# Run the aggregator
python news_aggregator.py
```

Or test with the demo script using mock data:

```bash
python demo.py
```

## Report Generation

The system can generate reports in multiple formats:

### Markdown Reports

Markdown reports include:
- Report metadata (date, total items, feeds processed)
- Formatted news items with titles, links, sources, and descriptions
- Proper markdown formatting for easy reading

### CSV Reports

CSV reports include:
- Structured data with columns: title, link, feed_name, pubDate, description, guid
- Compatible with Excel, Google Sheets, and data analysis tools
- Easy to import into databases

### Using Report Generation Programmatically

```python
from news_aggregator import RSSFeedHandler
from report_generator import ReportGenerator

# Fetch news items
handler = RSSFeedHandler()
items = handler.get_all_feeds()

# Generate reports
report_gen = ReportGenerator()
metadata = report_gen.get_report_metadata(items)
generated_files = report_gen.generate_all_formats(items, metadata)

print(f"Generated reports:")
for format_name, filepath in generated_files.items():
    print(f"  - {format_name}: {filepath}")
```

## Email Delivery

The system supports automated email delivery with attachments.

### Configuration

Email delivery is configured via environment variables (recommended for security):

```bash
# Required settings
export EMAIL_ENABLED=true
export EMAIL_HOST=smtp.gmail.com          # SMTP server
export EMAIL_PORT=587                      # SMTP port
export EMAIL_USERNAME=your-email@gmail.com # Your email address
export EMAIL_PASSWORD=your-app-password    # App-specific password
export EMAIL_TO=recipient@email.com        # Recipient email

# Optional settings
export EMAIL_FROM=your-email@gmail.com     # From address (defaults to EMAIL_USERNAME)
export EMAIL_USE_TLS=true                  # Use TLS (default: true)
export EMAIL_USE_SSL=false                 # Use SSL (default: false)
```

### GitHub Secrets Configuration

For GitHub Actions, store credentials as secrets:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `EMAIL_HOST`: smtp.gmail.com
   - `EMAIL_PORT`: 587
   - `EMAIL_USERNAME`: your-email@gmail.com
   - `EMAIL_PASSWORD`: your app-specific password
   - `EMAIL_TO`: recipient@email.com
   - `EMAIL_ENABLED`: true

### Gmail App Passwords

For Gmail accounts:

1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → 2-Step Verification → App passwords
3. Generate a new app password for "Mail"
4. Use this app password as `EMAIL_PASSWORD`

### Email Features

- **HTML Email Body**: Beautiful, responsive HTML email template
- **Plain Text Fallback**: Plain text version for email clients that don't support HTML
- **Attachments**: Both Markdown and CSV reports attached automatically
- **Summary**: Email body includes a summary of the latest headlines
- **Customizable Templates**: Edit templates in `templates/` directory

### Using Email Delivery Programmatically

```python
from email_delivery import EmailDelivery
from report_generator import ReportGenerator

# Generate reports
report_gen = ReportGenerator()
items = [...] # Your feed items
metadata = report_gen.get_report_metadata(items)
generated_files = report_gen.generate_all_formats(items, metadata)

# Send email
email_handler = EmailDelivery()
attachments = list(generated_files.values())
success = email_handler.send_email(items, metadata, attachments)

if success:
    print("Email sent successfully!")
else:
    print("Failed to send email")
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

### Email Configuration

```python
# Email settings (retrieved from environment variables)
EMAIL_CONFIG = {
    'enabled': os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true',
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': int(os.environ.get('EMAIL_PORT', '587')),
    'username': os.environ.get('EMAIL_USERNAME', ''),
    'password': os.environ.get('EMAIL_PASSWORD', ''),
    'to_email': os.environ.get('EMAIL_TO', ''),
    'use_tls': os.environ.get('EMAIL_USE_TLS', 'true').lower() == 'true',
    'use_ssl': os.environ.get('EMAIL_USE_SSL', 'false').lower() == 'true',
}
```

### Output Configuration

```python
# Output format settings
OUTPUT_CONFIG = {
    'formats': ['markdown', 'csv'],  # Supported formats
    'output_directory': os.environ.get('OUTPUT_DIR', 'reports'),
    'filename_template': 'news_report_{timestamp}',
    'include_timestamp': True,
    'date_format': '%Y-%m-%d_%H-%M-%S',
}

# Email template settings
EMAIL_TEMPLATE_CONFIG = {
    'html_template': 'templates/email_template.html',
    'text_template': 'templates/email_template.txt',
    'subject_template': 'News Aggregator Report - {date}',
    'max_items_in_summary': 10,  # Maximum items to show in email body
}
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