# Email Delivery and Reporting - Setup Guide

This guide provides step-by-step instructions for setting up email delivery and report generation for the news aggregator.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Email Configuration](#email-configuration)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

## Quick Start

### Local Testing

1. **Clone the repository**
   ```bash
   git clone https://github.com/trashduty/injury.git
   cd injury
   ```

2. **Set up environment variables** (create a `.env` file or export directly)
   ```bash
   export EMAIL_ENABLED=true
   export EMAIL_HOST=smtp.gmail.com
   export EMAIL_PORT=587
   export EMAIL_USERNAME=your-email@gmail.com
   export EMAIL_PASSWORD=your-app-password
   export EMAIL_TO=recipient@email.com
   ```

3. **Run the demo**
   ```bash
   python demo.py
   ```
   This will generate sample reports in the `reports/` directory.

4. **Run the full aggregator**
   ```bash
   python news_aggregator.py
   ```
   This will fetch real RSS feeds, generate reports, and send email (if configured).

## Email Configuration

### Gmail Setup (Recommended for Testing)

1. **Enable 2-Factor Authentication**
   - Go to your Google Account: https://myaccount.google.com
   - Navigate to Security → 2-Step Verification
   - Enable 2-Step Verification if not already enabled

2. **Generate App Password**
   - In Security settings, go to "App passwords"
   - Select app: Mail
   - Select device: Other (Custom name)
   - Enter a name: "News Aggregator"
   - Click "Generate"
   - Copy the 16-character password (without spaces)

3. **Use the App Password**
   - Use this app password as your `EMAIL_PASSWORD`
   - Never use your regular Gmail password

### Other SMTP Providers

#### Outlook/Office 365
```bash
export EMAIL_HOST=smtp.office365.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=true
```

#### Yahoo Mail
```bash
export EMAIL_HOST=smtp.mail.yahoo.com
export EMAIL_PORT=587
export EMAIL_USE_TLS=true
```

#### SendGrid
```bash
export EMAIL_HOST=smtp.sendgrid.net
export EMAIL_PORT=587
export EMAIL_USERNAME=apikey
export EMAIL_PASSWORD=your-sendgrid-api-key
export EMAIL_USE_TLS=true
```

#### Custom SMTP Server
```bash
export EMAIL_HOST=smtp.yourserver.com
export EMAIL_PORT=465
export EMAIL_USE_SSL=true  # Use SSL instead of TLS for port 465
```

## GitHub Actions Setup

### Step 1: Add Secrets to Repository

1. Go to your GitHub repository
2. Click on "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add the following secrets:

   | Secret Name | Example Value | Description |
   |------------|---------------|-------------|
   | `EMAIL_HOST` | smtp.gmail.com | SMTP server address |
   | `EMAIL_PORT` | 587 | SMTP server port |
   | `EMAIL_USERNAME` | your-email@gmail.com | Your email address |
   | `EMAIL_PASSWORD` | xxxx xxxx xxxx xxxx | App-specific password |
   | `EMAIL_TO` | recipient@email.com | Recipient email address |

### Step 2: Create Workflow File

1. Create `.github/workflows/` directory in your repository if it doesn't exist
   ```bash
   mkdir -p .github/workflows
   ```

2. Copy the example workflow file
   ```bash
   cp WORKFLOW_EXAMPLE.yml .github/workflows/news-aggregator.yml
   ```

3. Commit and push the workflow
   ```bash
   git add .github/workflows/news-aggregator.yml
   git commit -m "Add news aggregator workflow"
   git push
   ```

### Step 3: Test the Workflow

1. Go to your repository on GitHub
2. Click on "Actions" tab
3. Select "News Aggregator with Email Delivery" workflow
4. Click "Run workflow" → "Run workflow"
5. Monitor the workflow execution
6. Check your email for the report

### Step 4: Customize Schedule

Edit `.github/workflows/news-aggregator.yml` to change the schedule:

```yaml
on:
  schedule:
    # Daily at 9 AM UTC
    - cron: '0 9 * * *'
    
    # Every 6 hours
    # - cron: '0 */6 * * *'
    
    # Monday-Friday at 8 AM UTC
    # - cron: '0 8 * * 1-5'
    
    # Twice daily at 9 AM and 5 PM UTC
    # - cron: '0 9,17 * * *'
```

## Testing

### Test Report Generation Only

```python
from news_aggregator import RSSFeedHandler
from report_generator import ReportGenerator

# Fetch items
handler = RSSFeedHandler()
items = handler.get_all_feeds()

# Generate reports
report_gen = ReportGenerator()
metadata = report_gen.get_report_metadata(items)
files = report_gen.generate_all_formats(items, metadata)

print(f"Generated: {files}")
```

### Test Email Without Sending

Set `EMAIL_ENABLED=false` to test the application without actually sending emails:

```bash
export EMAIL_ENABLED=false
python news_aggregator.py
```

This will generate reports but skip email delivery.

### Test with Mock Data

Use the demo script which uses mock data instead of fetching from RSS feeds:

```bash
python demo.py
```

This is useful for testing report generation and email templates without network access.

## Troubleshooting

### Email Not Sending

1. **Check Environment Variables**
   ```bash
   echo $EMAIL_ENABLED
   echo $EMAIL_HOST
   echo $EMAIL_USERNAME
   # Don't echo PASSWORD for security
   ```

2. **Verify SMTP Settings**
   - Ensure you're using the correct SMTP server and port
   - Gmail: smtp.gmail.com:587
   - Check if your provider requires SSL or TLS

3. **Check Firewall/Network**
   - Some networks block SMTP ports (587, 465)
   - Try a different network or use a VPN

4. **Authentication Issues**
   - For Gmail: Make sure you're using an App Password, not your regular password
   - Verify 2FA is enabled on your Google account

5. **Check Logs**
   - Look for error messages in the console output
   - Common errors:
     - "Authentication failed": Wrong username/password
     - "Connection refused": Wrong host/port or firewall blocking
     - "SSL/TLS error": Wrong SSL/TLS settings

### Reports Not Generated

1. **Check Output Directory**
   ```bash
   ls -la reports/
   ```

2. **Verify Permissions**
   ```bash
   mkdir -p reports
   chmod 755 reports
   ```

3. **Check Disk Space**
   ```bash
   df -h .
   ```

### No Items Fetched

1. **Check Internet Connection**
   ```bash
   ping google.com
   ```

2. **Verify RSS Feed URLs**
   - Open the feed URL in a browser
   - Check if the feed is still active

3. **Check Feed Configuration**
   - Ensure feeds are enabled in `config.py`
   - Verify feed URLs are correct

### GitHub Actions Issues

1. **Secrets Not Working**
   - Verify secret names match exactly (case-sensitive)
   - Re-create secrets if needed
   - Check workflow file references: `${{ secrets.EMAIL_HOST }}`

2. **Workflow Not Running**
   - Check workflow syntax: Use YAML validator
   - Verify schedule cron syntax
   - Ensure workflow is in `.github/workflows/` directory

3. **Permission Issues**
   - Go to Settings → Actions → General
   - Ensure "Read and write permissions" is enabled if needed

## Security Best Practices

1. **Never commit credentials**
   - Use environment variables or secrets
   - Add `.env` to `.gitignore`

2. **Use App Passwords**
   - Never use your main email password
   - Generate app-specific passwords

3. **Rotate Credentials Regularly**
   - Change app passwords periodically
   - Update secrets in GitHub

4. **Limit Access**
   - Use recipient-specific email addresses
   - Don't share credentials

5. **Monitor Usage**
   - Check email sending logs
   - Monitor for unauthorized access

## Advanced Configuration

### Custom Email Templates

Edit the templates in `templates/` directory:

- `templates/email_template.html` - HTML email template
- `templates/email_template.txt` - Plain text email template

Templates support these variables:
- `{report_date}` - Report generation date
- `{total_items}` - Total number of items
- `{feeds_count}` - Number of feeds processed
- `{items_html}` - HTML formatted items (HTML template only)
- `{items_text}` - Plain text formatted items (text template only)
- `{more_items_message}` - Message when items exceed max_items_in_summary
- `{generation_time}` - Full timestamp
- `{separator}` - Separator line (text template only)

### Custom Report Formats

To add support for additional formats, extend the `ReportGenerator` class:

```python
from report_generator import ReportGenerator

class CustomReportGenerator(ReportGenerator):
    def generate_json(self, items, metadata=None):
        """Generate JSON format report."""
        import json
        filepath = self._generate_filename('json')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
        
        return filepath
```

### Output Directory Configuration

Change the output directory via environment variable:

```bash
export OUTPUT_DIR=/path/to/custom/reports
python news_aggregator.py
```

Or modify `config.py`:

```python
OUTPUT_CONFIG = {
    'output_directory': '/path/to/custom/reports',
    # ...
}
```

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/trashduty/injury/issues
- Pull Requests: https://github.com/trashduty/injury/pulls
