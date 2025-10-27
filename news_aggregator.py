"""
College Football News Aggregator
Gathers publicly available news from RSS feeds focusing on injuries and depth chart changes.
"""

import feedparser
import smtplib
import logging
import time
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dateutil import parser as date_parser
import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregates news from RSS feeds and filters for relevant content."""
    
    def __init__(self):
        self.articles = []
        
    def fetch_feed(self, feed_info):
        """
        Fetch and parse an RSS feed.
        
        Args:
            feed_info (dict): Dictionary containing feed name, url, and keywords
            
        Returns:
            list: List of relevant articles from the feed
        """
        try:
            logger.info(f"Fetching feed: {feed_info['name']}")
            # Note: feedparser doesn't support timeout parameter directly
            # It uses urllib internally which has system-level timeout defaults
            feed = feedparser.parse(feed_info['url'])
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_info['name']}: {feed.bozo_exception}")
            
            relevant_articles = []
            cutoff_time = datetime.now() - timedelta(hours=config.MAX_NEWS_AGE_HOURS)
            
            for entry in feed.entries[:config.MAX_ARTICLES_PER_FEED]:
                try:
                    # Check if article is relevant based on keywords
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', entry.get('description', '')).lower()
                    content = f"{title} {summary}"
                    
                    # Check if any keyword matches
                    if any(keyword.lower() in content for keyword in feed_info['keywords']):
                        # Parse publication date
                        pub_date = None
                        if 'published' in entry:
                            try:
                                pub_date = date_parser.parse(entry.published)
                            except Exception as e:
                                logger.debug(f"Could not parse date: {e}")
                        
                        # Filter by age if date is available
                        if pub_date and pub_date < cutoff_time:
                            continue
                        
                        article = {
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', 'Date unknown'),
                            'summary': entry.get('summary', entry.get('description', 'No summary')),
                            'source': feed_info['name']
                        }
                        relevant_articles.append(article)
                        logger.debug(f"Found relevant article: {article['title']}")
                        
                except Exception as e:
                    logger.error(f"Error processing entry from {feed_info['name']}: {e}")
                    continue
            
            logger.info(f"Found {len(relevant_articles)} relevant articles from {feed_info['name']}")
            return relevant_articles
            
        except Exception as e:
            logger.error(f"Error fetching feed {feed_info['name']}: {e}")
            return []
    
    def aggregate_news(self):
        """
        Aggregate news from all configured RSS feeds.
        
        Returns:
            list: List of all relevant articles
        """
        logger.info("Starting news aggregation")
        all_articles = []
        
        for feed_info in config.RSS_FEEDS:
            try:
                articles = self.fetch_feed(feed_info)
                all_articles.extend(articles)
                
                # Rate limiting
                time.sleep(config.REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Error processing feed {feed_info.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"Total articles aggregated: {len(all_articles)}")
        self.articles = all_articles
        return all_articles
    
    def format_email_report(self):
        """
        Format the aggregated articles into an HTML email report.
        
        Returns:
            str: HTML formatted email body
        """
        if not self.articles:
            return "<html><body><h2>No relevant news found</h2><p>No injury or depth chart news was found in the configured feeds.</p></body></html>"
        
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                h1 { color: #2c3e50; }
                h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
                .article { margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-left: 4px solid #3498db; }
                .article-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
                .article-meta { font-size: 12px; color: #7f8c8d; margin-bottom: 10px; }
                .article-summary { margin-bottom: 10px; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>College Football News Report</h1>
            <p><strong>Focus:</strong> Injuries & Depth Chart Changes</p>
            <p><strong>Generated:</strong> {timestamp}</p>
            <p><strong>Articles Found:</strong> {count}</p>
            <hr>
        """.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            count=len(self.articles)
        )
        
        # Group articles by source
        articles_by_source = {}
        for article in self.articles:
            source = article['source']
            if source not in articles_by_source:
                articles_by_source[source] = []
            articles_by_source[source].append(article)
        
        # Format articles by source
        for source, articles in articles_by_source.items():
            html += f"<h2>{source} ({len(articles)} articles)</h2>"
            for article in articles:
                html += f"""
                <div class="article">
                    <div class="article-title">{article['title']}</div>
                    <div class="article-meta">
                        <strong>Published:</strong> {article['published']} | 
                        <strong>Source:</strong> {article['source']}
                    </div>
                    <div class="article-summary">{article['summary'][:500]}...</div>
                    <div><a href="{article['link']}" target="_blank">Read full article</a></div>
                </div>
                """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def send_email_report(self, html_content):
        """
        Send the formatted report via email.
        
        Args:
            html_content (str): HTML formatted email body
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Validate configuration
            if not config.EMAIL_SENDER or not config.EMAIL_PASSWORD:
                logger.error("Email credentials not configured")
                return False
            
            if not config.EMAIL_RECIPIENT:
                logger.error("Email recipient not configured")
                return False
            
            logger.info(f"Sending email report to {config.EMAIL_RECIPIENT}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = config.REPORT_SUBJECT
            msg['From'] = config.EMAIL_SENDER
            msg['To'] = config.EMAIL_RECIPIENT
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT) as server:
                server.set_debuglevel(0)
                server.starttls()
                server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info("Email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False


def main():
    """Main execution function."""
    try:
        logger.info("=== College Football News Aggregator Started ===")
        
        # Create aggregator instance
        aggregator = NewsAggregator()
        
        # Aggregate news
        articles = aggregator.aggregate_news()
        
        # Format report
        html_report = aggregator.format_email_report()
        
        # Send email
        success = aggregator.send_email_report(html_report)
        
        if success:
            logger.info("=== News Aggregation Completed Successfully ===")
            sys.exit(0)
        else:
            logger.error("=== News Aggregation Completed with Errors ===")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
