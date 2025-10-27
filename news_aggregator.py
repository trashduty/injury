"""
News Aggregator Module

This module handles fetching and parsing RSS feeds with proper error
handling, logging, and support for multiple feed formats.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import socket

import config
from report_generator import ReportGenerator
from email_delivery import EmailDelivery


# Set up module logger (application should configure logging)
logger = logging.getLogger(__name__)


def configure_logging():
    """
    Configure logging for the news aggregator.
    
    Call this function if you want to use the default logging configuration.
    Otherwise, configure logging in your application before using this module.
    """
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT
    )


class RSSFeedHandler:
    """Handler for RSS feed parsing and management."""
    
    def __init__(self):
        """Initialize the RSS feed handler."""
        self.feeds_cache: Dict[str, Dict[str, Any]] = {}
        self.last_fetch_times: Dict[str, float] = {}
        logger.info("RSS Feed Handler initialized")
    
    def fetch_feed(self, feed_url: str, timeout: int = None) -> Optional[str]:
        """
        Fetch raw RSS feed content from a URL.
        
        Args:
            feed_url: The URL of the RSS feed
            timeout: Request timeout in seconds (default: from config)
            
        Returns:
            Raw XML content as string, or None if fetch failed
        """
        if timeout is None:
            timeout = config.FEED_TIMEOUT
            
        retries = 0
        last_error = None
        
        while retries < config.MAX_RETRIES:
            try:
                logger.info(f"Fetching feed from {feed_url} (attempt {retries + 1}/{config.MAX_RETRIES})")
                
                # Create request with user agent to avoid blocking
                request = Request(
                    feed_url,
                    headers={'User-Agent': 'NewsAggregator/1.0'}
                )
                
                with urlopen(request, timeout=timeout) as response:
                    content = response.read().decode('utf-8')
                    logger.info(f"Successfully fetched feed from {feed_url}")
                    return content
                    
            except HTTPError as e:
                last_error = e
                logger.error(f"HTTP error fetching {feed_url}: {e.code} - {e.reason}")
                if e.code in [404, 410]:  # Not found or gone - don't retry
                    break
                    
            except URLError as e:
                last_error = e
                logger.error(f"URL error fetching {feed_url}: {e.reason}")
                
            except socket.timeout:
                last_error = TimeoutError(f"Timeout after {timeout} seconds")
                logger.error(f"Timeout fetching {feed_url}")
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error fetching {feed_url}: {str(e)}")
            
            retries += 1
            if retries < config.MAX_RETRIES:
                logger.info(f"Retrying in {config.RETRY_DELAY} seconds...")
                time.sleep(config.RETRY_DELAY)
        
        logger.error(f"Failed to fetch feed from {feed_url} after {config.MAX_RETRIES} attempts")
        return None
    
    def parse_rss_feed(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse RSS feed XML content into a list of items.
        
        Args:
            xml_content: Raw XML content of the RSS feed
            
        Returns:
            List of parsed feed items
        """
        items = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Try RSS 2.0 format first
            channel = root.find('channel')
            if channel is not None:
                items = self._parse_rss_2_0(channel)
            else:
                # Try Atom format
                items = self._parse_atom_feed(root)
            
            logger.info(f"Successfully parsed {len(items)} items from feed")
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing feed: {str(e)}")
        
        return items[:config.MAX_ITEMS_PER_FEED]
    
    def _parse_rss_2_0(self, channel: ET.Element) -> List[Dict[str, Any]]:
        """Parse RSS 2.0 format feed."""
        items = []
        
        for item_elem in channel.findall('item'):
            item = {}
            
            # Extract common RSS 2.0 elements
            title = item_elem.find('title')
            if title is not None and title.text:
                item['title'] = title.text.strip()
            
            link = item_elem.find('link')
            if link is not None and link.text:
                item['link'] = link.text.strip()
            
            description = item_elem.find('description')
            if description is not None and description.text:
                item['description'] = description.text.strip()
            
            pub_date = item_elem.find('pubDate')
            if pub_date is not None and pub_date.text:
                item['pubDate'] = pub_date.text.strip()
            
            # Extract GUID if available
            guid = item_elem.find('guid')
            if guid is not None and guid.text:
                item['guid'] = guid.text.strip()
            
            # Only add item if it has at least a title or link
            if item.get('title') or item.get('link'):
                items.append(item)
        
        return items
    
    def _parse_atom_feed(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Parse Atom format feed."""
        items = []
        
        # Handle Atom namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Try to find entries with namespace first, then without
        entries = root.findall('atom:entry', ns)
        if not entries:
            entries = root.findall('entry')
        
        for entry in entries:
            item = {}
            
            # Extract Atom elements
            title = entry.find('atom:title', ns)
            if title is None:
                title = entry.find('title')
            if title is not None and title.text:
                item['title'] = title.text.strip()
            
            # Atom uses link elements with href attribute
            link = entry.find('atom:link[@rel="alternate"]', ns)
            if link is None:
                link = entry.find('atom:link', ns)
            if link is None:
                link = entry.find('link')
            if link is not None:
                href = link.get('href')
                if href:
                    item['link'] = href.strip()
            
            summary = entry.find('atom:summary', ns)
            if summary is None:
                summary = entry.find('summary')
            if summary is not None and summary.text:
                item['description'] = summary.text.strip()
            
            updated = entry.find('atom:updated', ns)
            if updated is None:
                updated = entry.find('updated')
            if updated is not None and updated.text:
                item['pubDate'] = updated.text.strip()
            
            entry_id = entry.find('atom:id', ns)
            if entry_id is None:
                entry_id = entry.find('id')
            if entry_id is not None and entry_id.text:
                item['guid'] = entry_id.text.strip()
            
            # Only add item if it has at least a title or link
            if item.get('title') or item.get('link'):
                items.append(item)
        
        return items
    
    def get_feed_items(self, feed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get items from a feed with caching support.
        
        Args:
            feed_config: Feed configuration dictionary
            
        Returns:
            List of feed items
        """
        feed_url = feed_config['url']
        feed_name = feed_config.get('name', feed_url)
        
        logger.info(f"Getting items for feed: {feed_name}")
        
        # Check if we need to refresh the cache
        current_time = time.time()
        last_fetch = self.last_fetch_times.get(feed_url, 0)
        priority = feed_config.get('priority', 2)
        refresh_interval = config.get_refresh_interval(priority)
        
        if current_time - last_fetch < refresh_interval:
            # Use cached data if available
            if feed_url in self.feeds_cache:
                logger.info(f"Using cached data for {feed_name}")
                return self.feeds_cache[feed_url].get('items', [])
        
        # Fetch and parse the feed
        xml_content = self.fetch_feed(feed_url)
        if xml_content:
            items = self.parse_rss_feed(xml_content)
            
            # Update cache
            self.feeds_cache[feed_url] = {
                'items': items,
                'fetched_at': current_time,
                'name': feed_name
            }
            self.last_fetch_times[feed_url] = current_time
            
            return items
        else:
            logger.warning(f"Failed to fetch feed: {feed_name}")
            # Return cached data if available, even if stale
            if feed_url in self.feeds_cache:
                logger.info(f"Returning stale cached data for {feed_name}")
                return self.feeds_cache[feed_url].get('items', [])
            return []
    
    def get_all_feeds(self) -> List[Dict[str, Any]]:
        """
        Get items from all enabled feeds.
        
        Returns:
            List of all feed items from enabled feeds
        """
        all_items = []
        enabled_feeds = config.get_enabled_feeds()
        
        logger.info(f"Fetching {len(enabled_feeds)} enabled feeds")
        
        for feed_config in enabled_feeds:
            items = self.get_feed_items(feed_config)
            # Add feed name to each item
            for item in items:
                item['feed_name'] = feed_config.get('name', feed_config['url'])
            all_items.extend(items)
        
        logger.info(f"Retrieved {len(all_items)} total items from all feeds")
        return all_items
    
    def get_feed_status(self) -> Dict[str, Any]:
        """
        Get status information for all feeds.
        
        Returns:
            Dictionary with feed status information
        """
        status = {
            'total_feeds': len(config.RSS_FEEDS),
            'enabled_feeds': len(config.get_enabled_feeds()),
            'cached_feeds': len(self.feeds_cache),
            'feeds': []
        }
        
        for feed_config in config.RSS_FEEDS:
            feed_url = feed_config['url']
            feed_info = {
                'name': feed_config.get('name', feed_url),
                'url': feed_url,
                'enabled': feed_config.get('enabled', True),
                'priority': feed_config.get('priority', 2),
                'cached': feed_url in self.feeds_cache,
                'last_fetch': None,
                'items_count': 0
            }
            
            if feed_url in self.last_fetch_times:
                feed_info['last_fetch'] = datetime.fromtimestamp(
                    self.last_fetch_times[feed_url]
                ).isoformat()
            
            if feed_url in self.feeds_cache:
                feed_info['items_count'] = len(
                    self.feeds_cache[feed_url].get('items', [])
                )
            
            status['feeds'].append(feed_info)
        
        return status


def main():
    """Main function for testing the news aggregator."""
    # Configure logging for the main function
    configure_logging()
    
    logger.info("Starting News Aggregator")
    
    handler = RSSFeedHandler()
    
    # Get all feed items
    items = handler.get_all_feeds()
    
    print(f"\nFetched {len(items)} items from all feeds:")
    for i, item in enumerate(items[:5], 1):  # Show first 5 items
        print(f"\n{i}. {item.get('title', 'No title')}")
        print(f"   Source: {item.get('feed_name', 'Unknown')}")
        print(f"   Link: {item.get('link', 'No link')}")
        if item.get('pubDate'):
            print(f"   Published: {item['pubDate']}")
    
    # Show feed status
    status = handler.get_feed_status()
    print(f"\n\nFeed Status:")
    print(f"Total feeds: {status['total_feeds']}")
    print(f"Enabled feeds: {status['enabled_feeds']}")
    print(f"Cached feeds: {status['cached_feeds']}")
    
    # Generate reports if items were fetched
    if items:
        print("\n\nGenerating reports...")
        report_gen = ReportGenerator()
        metadata = report_gen.get_report_metadata(items)
        generated_files = report_gen.generate_all_formats(items, metadata)
        
        print(f"Generated reports:")
        for format_name, filepath in generated_files.items():
            print(f"  - {format_name}: {filepath}")
        
        # Send email if configured
        if config.EMAIL_CONFIG.get('enabled'):
            print("\n\nSending email...")
            email_handler = EmailDelivery()
            attachments = list(generated_files.values())
            success = email_handler.send_email(items, metadata, attachments)
            
            if success:
                print("Email sent successfully!")
            else:
                print("Failed to send email. Check logs for details.")
        else:
            print("\n\nEmail delivery is disabled. Set EMAIL_ENABLED=true to enable.")
    else:
        print("\n\nNo items fetched, skipping report generation and email delivery.")


if __name__ == '__main__':
    main()
