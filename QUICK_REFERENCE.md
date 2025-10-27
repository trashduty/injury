# Quick Reference Card

## Quick Start

### Run with Mock Data (No Network Required)
```bash
python demo.py
```

### Run with Real RSS Feeds
```bash
python news_aggregator.py
```

### Enable Email Delivery
```bash
export EMAIL_ENABLED=true
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=587
export EMAIL_USERNAME=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
export EMAIL_TO=recipient@email.com

python news_aggregator.py
```

## Environment Variables

### Required for Email
```bash
EMAIL_ENABLED=true              # Enable email delivery
EMAIL_HOST=smtp.gmail.com       # SMTP server
EMAIL_PORT=587                  # SMTP port
EMAIL_USERNAME=user@email.com   # Email username
EMAIL_PASSWORD=app-password     # App password (not regular password!)
EMAIL_TO=recipient@email.com    # Recipient email
```

### Optional
```bash
EMAIL_FROM=sender@email.com     # From address (defaults to EMAIL_USERNAME)
EMAIL_USE_TLS=true             # Use TLS (default: true)
EMAIL_USE_SSL=false            # Use SSL (default: false)
OUTPUT_DIR=reports             # Report output directory (default: reports)
```

## Gmail App Password Setup

1. Enable 2FA: https://myaccount.google.com/security
2. Generate App Password: Security → App passwords → Mail
3. Use the generated 16-character password (no spaces)
4. Set as EMAIL_PASSWORD

## Testing

### Run All Tests
```bash
python -m unittest discover -v
```

### Run Specific Test Suite
```bash
python -m unittest test_email_reports -v
python -m unittest test_news_aggregator -v
python -m unittest test_web_scraper -v
```

### Test Report Generation
```python
from report_generator import ReportGenerator
gen = ReportGenerator()
# Will create files in reports/ directory
```

## Common SMTP Configurations

### Gmail
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
```

### Outlook
```bash
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
```

### Yahoo
```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
```

### SendGrid
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USERNAME=apikey
EMAIL_PASSWORD=<your-api-key>
EMAIL_USE_TLS=true
```

## Output Files

Generated reports are saved to `reports/` directory:
- `news_report_YYYY-MM-DD_HH-MM-SS.md` - Markdown format
- `news_report_YYYY-MM-DD_HH-MM-SS.csv` - CSV format

## GitHub Actions Setup

1. **Add Secrets**: Settings → Secrets → Actions → New secret
   - EMAIL_HOST
   - EMAIL_PORT
   - EMAIL_USERNAME
   - EMAIL_PASSWORD
   - EMAIL_TO

2. **Add Workflow**: Copy `WORKFLOW_EXAMPLE.yml` to `.github/workflows/`

3. **Test**: Actions tab → Select workflow → Run workflow

## Troubleshooting

### Email Not Sending
- Check EMAIL_ENABLED=true
- Verify SMTP settings
- Use app password, not regular password
- Check firewall/network blocks port 587

### No Reports Generated
- Check if feeds fetched successfully
- Verify output directory permissions
- Check logs for errors

### Authentication Failed
- For Gmail: Use app password
- Enable 2FA on Google account
- Verify username/password correct

## File Structure

```
injury/
├── config.py                    # Configuration
├── news_aggregator.py          # Main aggregator
├── report_generator.py         # Report generation
├── email_delivery.py           # Email sending
├── web_scraper.py              # Web scraping and depth charts
├── demo.py                     # Demo with mock data
├── test_news_aggregator.py     # RSS feed tests
├── test_email_reports.py       # Email tests
├── test_web_scraper.py         # Web scraping tests
├── templates/
│   ├── email_template.html     # HTML email template
│   └── email_template.txt      # Plain text template
├── reports/                    # Generated reports (gitignored)
│   ├── *.md                   # Markdown reports
│   └── *.csv                  # CSV reports
├── README.md                   # Main documentation
├── SETUP_GUIDE.md             # Setup instructions
├── WORKFLOW_EXAMPLE.yml       # GitHub Actions example
└── IMPLEMENTATION_SUMMARY.md  # Implementation details
```

## Key Features

- ✅ RSS feed aggregation (ESPN, CBS Sports, Custom feeds)
- ✅ Web scraping (Covers.com injury reports)
- ✅ Depth chart integration (Ourlads.com)
- ✅ Enhanced CSV with Team/Player/Position data
- ✅ Markdown report generation
- ✅ CSV report generation
- ✅ Email delivery with attachments
- ✅ HTML and plain text emails
- ✅ Rate limiting for web scraping
- ✅ Secure credential handling
- ✅ GitHub Actions ready
- ✅ Comprehensive error handling
- ✅ Full test coverage (63/63 tests passing)

## Documentation

- **README.md** - Main documentation with API reference
- **SETUP_GUIDE.md** - Detailed setup and configuration guide
- **WORKFLOW_EXAMPLE.yml** - GitHub Actions workflow template
- **IMPLEMENTATION_SUMMARY.md** - Implementation details and testing results
- **QUICK_REFERENCE.md** - This file

## Support

- Issues: https://github.com/trashduty/injury/issues
- Pull Requests: https://github.com/trashduty/injury/pulls

## Security Notes

- ⚠️ Never commit credentials to git
- ✅ Use environment variables for secrets
- ✅ Use app passwords, not regular passwords
- ✅ Enable 2FA on email accounts
- ✅ Keep credentials secure
- ✅ Rotate passwords regularly

## Version

- **Implementation Date**: 2025-10-27
- **Tests**: 63/63 passing
- **Python**: 3.11+
- **Dependencies**: Standard library only

## News Sources

### RSS Feeds
- ESPN NCAAF: https://www.espn.com/espn/rss/ncf/news
- CBS Sports NCAAF: https://www.cbssports.com/rss/collegefootball
- Custom RSS Feed: https://rss.app/feeds/3j65xfmG9wfdJGvl.xml

### Web Scraping
- Covers.com: Injury reports
- Ourlads.com: Depth charts

### CSV Output Format
The CSV report includes the following fields in order:
- `team` - Team name
- `player` - Player name
- `position` - Player position (from depth chart)
- `title` - News headline or injury update
- `feed_name` - Source of the information
- `pubDate` - Publication date
- `description` - Full description or injury details
- `link` - URL to full article
- `guid` - Unique identifier
