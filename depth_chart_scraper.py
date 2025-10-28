"""
Depth Chart Scraper Module

This module provides functionality to scrape NCAA football depth charts
from Ourlads.com and export the data to CSV format.

The scraper is restricted to only access the NCAA football depth charts URL
and includes connection verification and comprehensive error handling.
"""

import logging
import csv
import time
import socket
from typing import List, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# URL whitelist - only NCAA football depth charts are allowed
ALLOWED_URL = 'https://www.ourlads.com/ncaa-football-depth-charts/'

# Scraper configuration
SCRAPER_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'rate_limit_delay': 2,
    'user_agent': 'DepthChartScraper/1.0 (Educational Purpose)',
}


class DepthChartParser(HTMLParser):
    """HTML parser for NCAA football depth charts from Ourlads.com."""
    
    def __init__(self):
        super().__init__()
        self.depth_chart = []
        self.current_team = None
        self.current_position = None
        self.in_starter_section = False
        
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        attrs_dict = dict(attrs)
        
        # Detect team sections
        if tag in ['h2', 'h3', 'div'] and any('team' in str(v).lower() for k, v in attrs if k == 'class'):
            self.current_team = None
    
    def handle_data(self, data):
        """Handle text data within HTML tags."""
        data = data.strip()
        if not data:
            return
        
        # Basic heuristic for parsing depth charts
        # Position codes are typically 2-4 uppercase letters
        if data.isupper() and 2 <= len(data) <= 4 and data.isalpha():
            self.current_position = data
        elif self.current_team and self.current_position:
            # This is likely a player name
            # Add to depth chart (as starter - first player listed)
            self.depth_chart.append({
                'team': self.current_team,
                'player': data,
                'position': self.current_position
            })


class DepthChartScraper:
    """Scraper for NCAA football depth charts with connection verification."""
    
    def __init__(self):
        """Initialize the depth chart scraper."""
        self.last_request_time = 0
        logger.info("Depth Chart Scraper initialized")
    
    def _verify_url(self, url: str) -> bool:
        """
        Verify that the URL is in the allowed whitelist.
        
        Args:
            url: The URL to verify
            
        Returns:
            True if URL is allowed, False otherwise
        """
        if url != ALLOWED_URL:
            logger.error(f"URL not allowed: {url}")
            logger.error(f"Only the following URL is permitted: {ALLOWED_URL}")
            return False
        return True
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < SCRAPER_CONFIG['rate_limit_delay']:
            sleep_time = SCRAPER_CONFIG['rate_limit_delay'] - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def verify_connection(self, url: str) -> bool:
        """
        Verify that a connection can be established to the URL.
        
        Args:
            url: The URL to verify connection to
            
        Returns:
            True if connection is successful, False otherwise
        """
        logger.info(f"Verifying connection to {url}")
        
        try:
            # Parse URL to get host and port
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.netloc
            port = 443 if parsed.scheme == 'https' else 80
            
            # Attempt to establish a socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SCRAPER_CONFIG['timeout'])
            
            logger.info(f"Attempting to connect to {host}:{port}")
            sock.connect((host, port))
            sock.close()
            
            logger.info(f"Connection verification successful for {url}")
            return True
            
        except socket.gaierror as e:
            logger.error(f"Connection verification failed: DNS resolution error for {url}")
            logger.error(f"Error details: {str(e)}")
            logger.error("Please check your internet connection and verify the URL is correct")
            return False
            
        except socket.timeout:
            logger.error(f"Connection verification failed: Connection timeout for {url}")
            logger.error(f"The server did not respond within {SCRAPER_CONFIG['timeout']} seconds")
            logger.error("Please check your internet connection or try again later")
            return False
            
        except ConnectionRefusedError:
            logger.error(f"Connection verification failed: Connection refused for {url}")
            logger.error("The server refused the connection")
            logger.error("The website may be down or blocking connections")
            return False
            
        except Exception as e:
            logger.error(f"Connection verification failed: Unexpected error for {url}")
            logger.error(f"Error details: {str(e)}")
            logger.error("Please check your internet connection and firewall settings")
            return False
    
    def fetch_html(self, url: str, timeout: int = None) -> Optional[str]:
        """
        Fetch HTML content from a URL with error handling.
        
        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        # Verify URL is allowed
        if not self._verify_url(url):
            return None
        
        # Verify connection before attempting to fetch
        if not self.verify_connection(url):
            logger.error(f"Skipping fetch due to connection verification failure for {url}")
            return None
        
        if timeout is None:
            timeout = SCRAPER_CONFIG['timeout']
        
        retries = 0
        max_retries = SCRAPER_CONFIG['max_retries']
        
        while retries < max_retries:
            try:
                # Apply rate limiting
                self._rate_limit()
                
                logger.info(f"Fetching HTML from {url} (attempt {retries + 1}/{max_retries})")
                
                # Create request with user agent
                request = Request(
                    url,
                    headers={'User-Agent': SCRAPER_CONFIG['user_agent']}
                )
                
                with urlopen(request, timeout=timeout) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    logger.info(f"Successfully fetched HTML from {url}")
                    logger.info(f"Received {len(content)} bytes of content")
                    return content
                    
            except HTTPError as e:
                logger.error(f"HTTP error fetching {url}: {e.code} - {e.reason}")
                if e.code == 404:
                    logger.error("Error 404: The requested page was not found")
                    logger.error("The depth chart URL may have changed or is temporarily unavailable")
                elif e.code == 403:
                    logger.error("Error 403: Access forbidden")
                    logger.error("The website may be blocking automated access")
                elif e.code == 500:
                    logger.error("Error 500: Internal server error")
                    logger.error("The website is experiencing technical difficulties")
                
                if e.code in [404, 410, 403]:  # Don't retry on these errors
                    break
                    
            except URLError as e:
                logger.error(f"URL error fetching {url}: {e.reason}")
                logger.error("This may indicate a network connectivity issue or invalid URL")
                
            except socket.timeout:
                logger.error(f"Timeout fetching {url}")
                logger.error(f"The server did not respond within {timeout} seconds")
                logger.error("The website may be slow or experiencing high traffic")
                
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
                logger.error("An unexpected error occurred during the fetch operation")
            
            retries += 1
            if retries < max_retries:
                logger.info(f"Retrying in {SCRAPER_CONFIG['rate_limit_delay']} seconds...")
                time.sleep(SCRAPER_CONFIG['rate_limit_delay'])
        
        logger.error(f"Failed to fetch HTML from {url} after {max_retries} attempts")
        logger.error("Please check your internet connection and try again later")
        return None
    
    def scrape_depth_chart(self, url: str = None) -> List[Dict[str, Any]]:
        """
        Scrape depth chart data from the NCAA football depth charts URL.
        
        Args:
            url: Optional URL to scrape (must be in whitelist, defaults to ALLOWED_URL)
            
        Returns:
            List of dictionaries containing team, player, and position data
        """
        if url is None:
            url = ALLOWED_URL
        
        logger.info(f"Starting depth chart scrape from {url}")
        
        html_content = self.fetch_html(url)
        if not html_content:
            logger.error("Failed to fetch HTML content, cannot proceed with scraping")
            return []
        
        try:
            parser = DepthChartParser()
            parser.feed(html_content)
            
            logger.info(f"Successfully parsed {len(parser.depth_chart)} depth chart entries")
            
            # Filter to only include starters (first player at each position per team)
            starters = []
            seen_positions = set()
            
            for entry in parser.depth_chart:
                key = (entry['team'], entry['position'])
                if key not in seen_positions:
                    starters.append(entry)
                    seen_positions.add(key)
            
            logger.info(f"Extracted {len(starters)} starter positions")
            return starters
            
        except Exception as e:
            logger.error(f"Error parsing depth chart data: {str(e)}")
            logger.error("The HTML structure may have changed or be malformed")
            return []
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = 'depth_chart.csv') -> bool:
        """
        Export depth chart data to CSV file.
        
        Args:
            data: List of depth chart entries
            filename: Output CSV filename
            
        Returns:
            True if export was successful, False otherwise
        """
        if not data:
            logger.warning("No data to export to CSV")
            return False
        
        try:
            logger.info(f"Exporting {len(data)} entries to {filename}")
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['team', 'player', 'position']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Successfully exported depth chart data to {filename}")
            return True
            
        except IOError as e:
            logger.error(f"Failed to write CSV file: {str(e)}")
            logger.error("Check file permissions and disk space")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error exporting to CSV: {str(e)}")
            return False


def main():
    """Main function to run the depth chart scraper."""
    logger.info("Starting NCAA Football Depth Chart Scraper")
    logger.info(f"Target URL: {ALLOWED_URL}")
    
    # Create scraper instance
    scraper = DepthChartScraper()
    
    # Scrape depth chart data
    depth_chart_data = scraper.scrape_depth_chart()
    
    if depth_chart_data:
        # Export to CSV
        success = scraper.export_to_csv(depth_chart_data)
        
        if success:
            logger.info("Depth chart scraping completed successfully")
            print(f"\nSuccessfully scraped {len(depth_chart_data)} depth chart entries")
            print(f"Data exported to: depth_chart.csv")
        else:
            logger.error("Failed to export data to CSV")
            print("\nFailed to export data to CSV")
    else:
        logger.error("No depth chart data was scraped")
        print("\nFailed to scrape depth chart data")
        print("Please check the logs for detailed error messages")


if __name__ == '__main__':
    main()
