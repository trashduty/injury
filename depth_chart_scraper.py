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
    """HTML parser for NCAA football depth charts from Ourlads.com.
    
    This parser extracts team information from the main landing page which 
    contains links to individual team depth charts.
    """
    
    def __init__(self, debug=False):
        super().__init__()
        self.teams = []
        self.current_link = None
        self.pending_team_name = None  # Buffer for team name waiting for its link
        self.in_team_name = False
        self.debug = debug
        self.tag_count = 0
        self.text_count = 0
        
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        self.tag_count += 1
        attrs_dict = dict(attrs)
        
        # Debug: Log tag information periodically
        if self.debug and self.tag_count % 1000 == 0:
            logger.debug(f"Processed {self.tag_count} tags so far...")
        
        # Look for links to depth chart pages
        # Pattern: <a href='depth-chart.aspx?s=team-name&id=12345'>
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if 'depth-chart.aspx' in href and 's=' in href:
                # Extract team slug from URL
                import re
                match = re.search(r's=([^&]+)', href)
                if match:
                    self.current_link = match.group(1)
                    # If we have a pending team name, pair it with this link
                    if self.pending_team_name:
                        self.teams.append({
                            'team': self.pending_team_name,
                            'slug': self.current_link
                        })
                        if self.debug:
                            logger.debug(f"Added team: {self.pending_team_name} (slug: {self.current_link})")
                        self.pending_team_name = None
                    if self.debug:
                        logger.debug(f"Found depth chart link for team: {self.current_link}")
        
        # Look for team names in div elements
        if tag == 'div' and 'class' in attrs_dict:
            if 'team-name' in attrs_dict['class'] or 'mm-team-name' in attrs_dict['class']:
                self.in_team_name = True
                if self.debug:
                    logger.debug(f"Found team name div with class: {attrs_dict['class']}")
    
    def handle_data(self, data):
        """Handle text data within HTML tags."""
        data = data.strip()
        if not data:
            return
        
        self.text_count += 1
        
        # If we're in a team name div, buffer the name for the next link
        if self.in_team_name and data:
            # Warn if we're overwriting a pending team name
            if self.pending_team_name:
                logger.warning(f"Overwriting pending team name '{self.pending_team_name}' with '{data}' - previous name was not paired with a link")
            self.pending_team_name = data
            if self.debug:
                logger.debug(f"Buffered team name: {data}")
            self.in_team_name = False
    
    def handle_endtag(self, tag):
        """Handle closing HTML tags."""
        if tag == 'div':
            self.in_team_name = False


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
    
    def scrape_depth_chart(self, url: str = None, debug: bool = False) -> List[Dict[str, Any]]:
        """
        Scrape depth chart data from the NCAA football depth charts URL.
        
        This scraper extracts team information from the main landing page,
        which contains links to individual team depth charts. The actual
        depth chart details (players and positions) are on separate pages
        that use JavaScript to load data dynamically.
        
        Args:
            url: Optional URL to scrape (must be in whitelist, defaults to ALLOWED_URL)
            debug: Enable debug logging to show HTML parsing details
            
        Returns:
            List of dictionaries containing team information
        """
        if url is None:
            url = ALLOWED_URL
        
        logger.info(f"Starting depth chart scrape from {url}")
        
        html_content = self.fetch_html(url)
        if not html_content:
            logger.error("Failed to fetch HTML content, cannot proceed with scraping")
            logger.error("Parsing step failed at: HTML fetch")
            return []
        
        # Log HTML structure information for debugging
        if debug:
            logger.debug("=== HTML Structure Analysis ===")
            logger.debug(f"Total HTML size: {len(html_content)} bytes")
            logger.debug(f"First 500 characters: {html_content[:500]}")
            
            # Count key HTML elements
            import re
            div_count = len(re.findall(r'<div', html_content, re.IGNORECASE))
            a_count = len(re.findall(r'<a\s', html_content, re.IGNORECASE))
            table_count = len(re.findall(r'<table', html_content, re.IGNORECASE))
            
            logger.debug(f"HTML contains: {div_count} divs, {a_count} links, {table_count} tables")
            
            # Check for depth chart related content
            depth_chart_links = len(re.findall(r'depth-chart\.aspx', html_content, re.IGNORECASE))
            logger.debug(f"Found {depth_chart_links} references to 'depth-chart.aspx'")
        
        try:
            logger.info("Starting HTML parsing with DepthChartParser...")
            parser = DepthChartParser(debug=debug)
            parser.feed(html_content)
            
            # Check for unpaired team name
            if parser.pending_team_name:
                logger.warning(f"Unpaired team name at end of parsing: '{parser.pending_team_name}' - no corresponding link found")
            
            logger.info(f"HTML parsing completed: processed {parser.tag_count} tags, {parser.text_count} text nodes")
            logger.info(f"Successfully parsed {len(parser.teams)} team entries")
            
            # Validate parsed content
            if len(parser.teams) == 0:
                logger.error("Parsing step failed at: No teams extracted from HTML")
                logger.error("The HTML structure may have changed or uses JavaScript to load data")
                logger.error("Expected to find <a> tags with 'depth-chart.aspx' URLs")
                
                # Additional diagnostics
                import re
                depth_chart_links = re.findall(r'depth-chart\.aspx\?s=([^&"\']+)', html_content)
                if depth_chart_links:
                    logger.error(f"DIAGNOSTIC: Found {len(depth_chart_links)} depth chart links in HTML")
                    logger.error(f"DIAGNOSTIC: Sample links: {depth_chart_links[:5]}")
                    logger.error("DIAGNOSTIC: Parser failed to extract these links properly")
                else:
                    logger.error("DIAGNOSTIC: No depth chart links found in HTML at all")
                    logger.error("DIAGNOSTIC: The website structure may have changed completely")
                
                return []
            
            # Remove duplicates based on team slug
            seen_slugs = set()
            unique_teams = []
            for team in parser.teams:
                if team['slug'] not in seen_slugs:
                    unique_teams.append(team)
                    seen_slugs.add(team['slug'])
            
            logger.info(f"Extracted {len(unique_teams)} unique teams (removed {len(parser.teams) - len(unique_teams)} duplicates)")
            
            # Log sample of extracted data
            if unique_teams:
                logger.info(f"Sample teams extracted: {[t['team'] for t in unique_teams[:5]]}")
            
            # Validate team data structure
            invalid_teams = [t for t in unique_teams if not t.get('team') or not t.get('slug')]
            if invalid_teams:
                logger.warning(f"Found {len(invalid_teams)} teams with missing data")
                unique_teams = [t for t in unique_teams if t.get('team') and t.get('slug')]
            
            return unique_teams
            
        except Exception as e:
            logger.error(f"Error parsing depth chart data: {str(e)}")
            logger.error(f"Parsing step failed at: Exception during HTML parsing - {type(e).__name__}")
            logger.error("The HTML structure may have changed or be malformed")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = 'depth_chart.csv') -> bool:
        """
        Export depth chart data to CSV file with validation.
        
        Args:
            data: List of depth chart entries
            filename: Output CSV filename
            
        Returns:
            True if export was successful, False otherwise
        """
        # Validate data before export
        if not data:
            logger.warning("No data to export to CSV")
            logger.warning("CSV generation skipped: empty data list")
            return False
        
        if not isinstance(data, list):
            logger.error(f"Invalid data type for CSV export: expected list, got {type(data).__name__}")
            logger.error("CSV generation failed: data validation error")
            return False
        
        # Validate data structure
        logger.info("Validating data structure before CSV export...")
        valid_entries = []
        invalid_count = 0
        
        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                logger.warning(f"Entry {i} is not a dictionary, skipping")
                invalid_count += 1
                continue
            
            # Check for required fields (team and slug for team listings)
            if 'team' not in entry:
                logger.warning(f"Entry {i} missing 'team' field, skipping")
                invalid_count += 1
                continue
            
            valid_entries.append(entry)
        
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} invalid entries, exporting {len(valid_entries)} valid entries")
        
        if not valid_entries:
            logger.error("No valid entries to export after validation")
            logger.error("CSV generation failed: all entries failed validation")
            return False
        
        try:
            logger.info(f"Exporting {len(valid_entries)} entries to {filename}")
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Determine fieldnames based on actual data structure
                # Team listings have 'team' and 'slug' fields
                sample_entry = valid_entries[0]
                if 'slug' in sample_entry:
                    fieldnames = ['team', 'slug']
                elif 'player' in sample_entry and 'position' in sample_entry:
                    fieldnames = ['team', 'player', 'position']
                else:
                    # Fallback: use all keys from first entry
                    fieldnames = list(sample_entry.keys())
                
                logger.info(f"CSV fields: {fieldnames}")
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                writer.writeheader()
                writer.writerows(valid_entries)
            
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
    import sys
    
    # Check for debug flag
    debug = '--debug' in sys.argv
    
    if debug:
        # Enable debug logging
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    
    logger.info("Starting NCAA Football Depth Chart Scraper")
    logger.info(f"Target URL: {ALLOWED_URL}")
    if debug:
        logger.info("Debug mode enabled")
    
    # Create scraper instance
    scraper = DepthChartScraper()
    
    # Scrape depth chart data with debug option
    depth_chart_data = scraper.scrape_depth_chart(debug=debug)
    
    if depth_chart_data:
        # Show what was scraped
        logger.info(f"Scraped data contains {len(depth_chart_data)} entries")
        
        # Export to CSV
        success = scraper.export_to_csv(depth_chart_data)
        
        if success:
            logger.info("Depth chart scraping completed successfully")
            print(f"\nSuccessfully scraped {len(depth_chart_data)} team entries")
            print(f"Data exported to: depth_chart.csv")
            print(f"\nNote: This list contains team information and links to individual depth charts.")
            print(f"Individual team depth charts use JavaScript to load player data dynamically.")
            if depth_chart_data:
                print(f"\nSample teams: {', '.join([d['team'] for d in depth_chart_data[:5]])}")
        else:
            logger.error("Failed to export data to CSV")
            print("\nFailed to export data to CSV")
            print("Data was scraped but could not be written to file")
    else:
        logger.error("No depth chart data was scraped")
        print("\nFailed to scrape depth chart data")
        print("Please check the logs for detailed error messages")
        print("\nTroubleshooting tips:")
        print("1. Run with --debug flag for more detailed logging: python depth_chart_scraper.py --debug")
        print("2. Check your internet connection")
        print("3. Verify the website structure hasn't changed")


if __name__ == '__main__':
    main()
