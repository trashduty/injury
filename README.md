# College Football News Aggregator

An automated system for gathering publicly available college football news focused on injuries and depth chart changes for podcast preparation.

## Features

- 📰 Aggregates news from multiple legitimate RSS feeds (ESPN, CBS Sports, Sports Illustrated)
- 🔍 Filters articles based on injury and depth chart keywords
- 📧 Formats and sends HTML email reports
- ⏰ Runs automatically on scheduled intervals (Saturday nights and Sunday mornings)
- 🛡️ Secure handling of credentials via GitHub Secrets
- 📝 Comprehensive logging and error handling
- ⚡ Rate limiting to respect API terms of service

## Setup

### Prerequisites

- Python 3.11 or higher
- Git
- GitHub account (for automated workflows)
- Email account with SMTP access (e.g., Gmail)

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/trashduty/injury.git
cd injury
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:

Create a `.env` file or export the following variables:

```bash
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_SENDER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_RECIPIENT="recipient@example.com"
export LOG_LEVEL="INFO"
```

**Note for Gmail users:** You'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### GitHub Actions Setup

To enable automated news aggregation via GitHub Actions:

1. Go to your repository settings on GitHub
2. Navigate to "Secrets and variables" → "Actions"
3. Add the following repository secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `EMAIL_SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP server port | `587` |
| `EMAIL_SENDER` | Sender email address | `your-email@gmail.com` |
| `EMAIL_PASSWORD` | Email password or app password | `your-app-password` |
| `EMAIL_RECIPIENT` | Recipient email address | `recipient@example.com` |

4. The workflow will run automatically on:
   - Saturday at 11:00 PM UTC
   - Sunday at 9:00 AM UTC
   
5. You can also trigger it manually from the "Actions" tab

## Usage

### Running Locally

```bash
python news_aggregator.py
```

### Running Manually on GitHub

1. Go to the "Actions" tab in your repository
2. Select "College Football News Aggregator" workflow
3. Click "Run workflow"

### Customizing RSS Feeds

Edit `config.py` to add or modify RSS feeds:

```python
RSS_FEEDS = [
    {
        'name': 'Your Feed Name',
        'url': 'https://example.com/rss/feed',
        'keywords': ['injury', 'depth chart', 'questionable']
    }
]
```

### Adjusting Schedule

Edit `.github/workflows/football-news.yml` to change the schedule:

```yaml
on:
  schedule:
    # Cron format: minute hour day month weekday
    - cron: '0 23 * * 6'  # Saturday at 11:00 PM UTC
```

## Configuration

### Configuration Options (config.py)

| Option | Default | Description |
|--------|---------|-------------|
| `REQUEST_TIMEOUT` | 10 | Timeout for HTTP requests (seconds) |
| `REQUEST_DELAY` | 2 | Delay between feed requests (seconds) |
| `MAX_NEWS_AGE_HOURS` | 72 | Maximum age of articles to include |
| `MAX_ARTICLES_PER_FEED` | 20 | Maximum articles to process per feed |

### Supported RSS Feeds

The system currently supports:
- ESPN College Football News
- CBS Sports College Football
- Sports Illustrated College Football

### Keywords Monitored

Articles are filtered for the following keywords:
- injury / injuries
- depth chart
- out for season
- questionable
- doubtful
- ruled out

## Email Report Format

The email report includes:
- Report generation timestamp
- Total number of articles found
- Articles grouped by source
- Article title, publication date, summary, and link

## Error Handling

The system includes comprehensive error handling:
- Failed feed fetching logs warnings but continues processing other feeds
- Email sending errors are logged with detailed information
- Rate limiting prevents overwhelming RSS feeds
- Graceful degradation when individual components fail

## Logging

Logs include:
- Feed fetching status
- Number of articles found per feed
- Email sending status
- Any errors or warnings

Log level can be adjusted via the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages

## Security Considerations

- ✅ All sensitive credentials stored as GitHub Secrets
- ✅ Environment variables for configuration
- ✅ No hardcoded credentials in code
- ✅ HTTPS connections for all network requests
- ✅ Rate limiting to prevent abuse
- ✅ Input validation and error handling

## Troubleshooting

### Email Not Sending

1. Verify SMTP credentials are correct
2. For Gmail, ensure you're using an App Password
3. Check if less secure app access needs to be enabled
4. Verify SMTP server and port settings

### No Articles Found

1. Check if RSS feeds are accessible
2. Verify keyword configuration
3. Adjust `MAX_NEWS_AGE_HOURS` if needed
4. Check logs for feed parsing errors

### GitHub Actions Failing

1. Verify all secrets are correctly set
2. Check workflow logs in the Actions tab
3. Ensure repository has necessary permissions
4. Test the script locally first

## Development

### Running Tests

Currently, the system doesn't include unit tests. To test locally:

```bash
# Set test environment variables
export EMAIL_RECIPIENT="test@example.com"

# Run the aggregator
python news_aggregator.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Best Practices

- Respect RSS feed terms of service
- Don't reduce `REQUEST_DELAY` below 2 seconds
- Monitor email delivery to avoid spam filters
- Keep dependencies updated for security patches
- Review logs regularly to ensure system health

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, please open an issue on GitHub.

## Acknowledgments

- RSS feeds provided by ESPN, CBS Sports, and Sports Illustrated
- Built with Python and GitHub Actions