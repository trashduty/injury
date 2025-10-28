# News Aggregation System

A robust news aggregation system with RSS feed support, web scraping, depth chart parsing, email delivery, and dual-format reporting (Markdown and CSV). Designed to fetch, parse, and manage multiple news sources including RSS feeds and web-scraped injury reports with proper error handling, caching, and automated email notifications.

## Features

- **Multiple News Sources**: 
  - ESPN NCAAF RSS feed
  - CBS Sports NCAAF RSS feed
  - Custom RSS feeds
  - Covers.com injury reports (web scraping)
- **Depth Chart Integration**: Parse depth charts from Ourlads.com to enrich player data with positions
- **RSS Feed Support**: Parse RSS 2.0 and Atom feed formats
- **Web Scraping**: Scrape injury reports with rate limiting and error handling
- **Enhanced CSV Reports**: Organized output with Team, Player, Position, News/Injury Update, Source, and Date
- **Error Handling**: Comprehensive error handling with retry logic
- **Rate Limiting**: Automatic rate limiting for web scraping to be respectful of source websites
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

### Basic Installation (News Aggregator)

No external dependencies are required for the basic news aggregator beyond Python's standard library. Simply clone the repository:

```bash
git clone https://github.com/trashduty/injury.git
cd injury
```

### Full Installation (with Depth Chart Scraper)

To use the depth chart scraper, install the required dependencies:

```bash
git clone https://github.com/trashduty/injury.git
cd injury
pip install -r requirements.txt
```

Required packages:
- beautifulsoup4 - HTML parsing
- requests - HTTP requests
- pandas - CSV data handling

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

### Running the Depth Chart Scraper

The depth chart scraper extracts starter information from OurLads NCAA football depth charts and generates a CSV file with team, player, and position data.

**Basic usage:**

```bash
python depth_chart_scraper.py
```

This will:
- Scrape depth chart data from https://www.ourlads.com/ncaa-football-depth-charts/
- Extract starter information (first player at each position)
- Generate a CSV file at `data/starters.csv` with columns: team, player, position
- Apply rate limiting (2 seconds between requests by default)

**Advanced options:**

```bash
# Specify custom output location
python depth_chart_scraper.py --output my_starters.csv

# Adjust rate limiting delay (in seconds)
python depth_chart_scraper.py --delay 3.0

# Enable verbose logging
python depth_chart_scraper.py --verbose
```

**Using in Python code:**

```python
from depth_chart_scraper import DepthChartScraper

# Create scraper instance
scraper = DepthChartScraper(rate_limit_delay=2.0)

# Run the scraper
scraper.run(output_path='data/starters.csv')

# Or use individual methods
starters = scraper.scrape_all_depth_charts()
scraper.save_to_csv(starters, 'data/starters.csv')
```

**Output format:**

The generated CSV file contains:
- `team`: Team name
- `player`: Player name
- `position`: Position code (e.g., QB, RB, WR, etc.)

This data can be used to filter injury reports to show only injuries for starting players.

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
- Team name (when available)
- Player name (when available)
- Position (from depth chart when available)
- Formatted news items with titles, links, sources, and descriptions
- Proper markdown formatting for easy reading

### CSV Reports

CSV reports include organized columns ideal for injury tracking:
- **Team**: Team name
- **Player**: Player name
- **Position**: Player position (from depth chart)
- **Title**: News headline or injury update
- **Feed Name**: Source of the information
- **Date**: Publication date
- **Description**: Full description or injury details
- **Link**: URL to full article
- **GUID**: Unique identifier

The CSV format is compatible with Excel, Google Sheets, and data analysis tools, making it easy to:
- Track player injuries over time
- Filter by team or position
- Import into databases for analysis
- Share with coaching staff or analysts

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

The system is configured through `config.py`. The default configuration includes multiple news sources:

```python
RSS_FEEDS = [
    {
        'url': 'https://rss.app/feeds/3j65xfmG9wfdJGvl.xml',
        'name': 'Custom RSS Feed',
        'enabled': True,
        'priority': 1
    },
    {
        'url': 'https://www.espn.com/espn/rss/ncf/news',
        'name': 'ESPN NCAAF',
        'enabled': True,
        'priority': 1
    },
    {
        'url': 'https://www.cbssports.com/rss/collegefootball',
        'name': 'CBS Sports NCAAF',
        'enabled': True,
        'priority': 1
    }
]
```

## Web Scraping and Depth Charts

### Injury Reports from Covers.com

The system automatically scrapes injury reports from Covers.com when fetching news:

```python
from news_aggregator import RSSFeedHandler

handler = RSSFeedHandler()
# get_all_feeds() automatically includes scraped injury reports
items = handler.get_all_feeds()
```

Injury reports include:
- Team name
- Player name
- Position
- Injury status
- Publication date

### Depth Chart Integration

The system fetches and caches depth charts from Ourlads.com to enrich player data:

```python
from web_scraper import WebScraper

scraper = WebScraper()

# Fetch depth chart for all teams
depth_chart = scraper.fetch_depth_chart()

# Get a specific player's position
position = scraper.get_player_position('John Doe', team='Alabama')
print(f"Position: {position}")

# Enrich news items with position data
enriched_items = scraper.enrich_items_with_positions(items)
```

### Web Scraping Configuration

Web scraping is configured with rate limiting and error handling:

```python
WEB_SCRAPING_CONFIG = {
    'covers_injury_url': 'https://www.covers.com/sport/football/ncaaf/injuries',
    'ourlads_depth_chart_url': 'https://www.ourlads.com/ncaa-football-depth-charts/',
    'rate_limit_delay': 2,  # seconds between requests
    'user_agent': 'NewsAggregator/1.0 (Educational Purpose)',
    'timeout': 30,
    'max_retries': 3,
}
```

Rate limiting ensures respectful scraping:
- Minimum 2 seconds between requests
- Automatic retry with exponential backoff
- Proper User-Agent header
- Comprehensive error handling

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
Get items from all enabled feeds including web-scraped injury reports.
- Returns: List of all feed items from enabled feeds plus injury reports from Covers.com

**`get_feed_status() -> Dict[str, Any]`**
Get status information for all feeds.
- Returns: Dictionary with feed status information

### WebScraper Class

#### Methods

**`__init__()`**
Initialize the web scraper with rate limiting and caching support.

**`fetch_html(url: str, timeout: int = None) -> Optional[str]`**
Fetch HTML content from a URL with error handling and rate limiting.
- Parameters:
  - `url`: The URL to fetch
  - `timeout`: Request timeout in seconds (optional)
- Returns: HTML content as string, or None if fetch failed

**`scrape_covers_injuries() -> List[Dict[str, Any]]`**
Scrape injury reports from Covers.com.
- Returns: List of injury report items with team, player, position, and status

**`fetch_depth_chart(team: Optional[str] = None) -> Dict[str, Any]`**
Fetch depth chart data from Ourlads.com with caching.
- Parameters:
  - `team`: Optional team name to filter
- Returns: Dictionary mapping teams to positions to players

**`get_player_position(player_name: str, team: Optional[str] = None) -> Optional[str]`**
Get a player's position from the depth chart.
- Parameters:
  - `player_name`: Name of the player
  - `team`: Optional team name to narrow search
- Returns: Position string or None if not found

**`enrich_items_with_positions(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]`**
Enrich news items with position information from depth chart.
- Parameters:
  - `items`: List of news items
- Returns: List of items enriched with position data

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
- **Web Scraping**: HTML parsing for sites without RSS feeds

Both RSS formats are automatically detected and parsed appropriately. Web scraping includes:
- HTML parsing with Python's built-in html.parser
- Rate limiting to respect website resources
- Automatic retry logic with error handling
- Caching to reduce unnecessary requests

## Testing

Run the complete test suite:

```bash
# Run all tests
python -m unittest discover -v

# Or run specific test modules
python -m unittest test_news_aggregator.py -v
python -m unittest test_web_scraper.py -v
```

Run the test suite for the news aggregator:

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