"""
Depth Chart Scraper for OurLads NCAA Football

This module scrapes starter information from OurLads NCAA football depth charts
and generates a CSV file with team, player, and position data.
"""

import logging
import time
import csv
import os
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DepthChartScraper:
    """
    Scraper for OurLads NCAA Football depth charts.
    
    Extracts starter information from depth charts and generates CSV output.
    """
    
    def __init__(
        self,
        base_url: str = "https://www.ourlads.com/ncaa-football-depth-charts/",
        rate_limit_delay: float = 2.0,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the depth chart scraper.
        
        Args:
            base_url: Base URL for OurLads depth charts
            rate_limit_delay: Minimum seconds between requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; DepthChartScraper/1.0; Educational Purpose)'
        })
        logger.info("DepthChartScraper initialized")
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL with error handling and rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        retries = 0
        
        while retries < self.max_retries:
            try:
                # Apply rate limiting
                self._rate_limit()
                
                logger.info(f"Fetching page: {url} (attempt {retries + 1}/{self.max_retries})")
                
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                logger.info(f"Successfully fetched page: {url}")
                return response.text
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
                if e.response.status_code in [404, 410, 403]:
                    # Don't retry on these errors
                    break
                    
            except requests.exceptions.Timeout:
                logger.error(f"Timeout fetching {url}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error fetching {url}: {str(e)}")
            
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
            
            retries += 1
            if retries < self.max_retries:
                time.sleep(self.rate_limit_delay)
        
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    def parse_team_links(self, html_content: str) -> List[Dict[str, str]]:
        """
        Parse team links from the main depth chart page.
        
        Args:
            html_content: HTML content of the main page
            
        Returns:
            List of dictionaries containing team name and URL
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        teams = []
        
        try:
            # Look for team links - OurLads typically has links to individual team depth charts
            # This is a generic approach that may need adjustment based on actual HTML structure
            
            # Try to find links that contain team names
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filter for depth chart related links
                if 'depth' in href.lower() and text and len(text) > 2:
                    # Build full URL if needed
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = f"https://www.ourlads.com{href}"
                    else:
                        full_url = f"{self.base_url}{href}"
                    
                    teams.append({
                        'team': text,
                        'url': full_url
                    })
            
            logger.info(f"Found {len(teams)} team links")
            
        except Exception as e:
            logger.error(f"Error parsing team links: {str(e)}")
        
        return teams
    
    def parse_depth_chart(self, html_content: str, team_name: str) -> List[Dict[str, str]]:
        """
        Parse depth chart information from a team's page.
        
        Args:
            html_content: HTML content of the team's depth chart page
            team_name: Name of the team
            
        Returns:
            List of dictionaries containing team, player, and position
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        starters = []
        
        try:
            # Look for depth chart tables or structured data
            # OurLads typically organizes depth charts by position
            
            # Try multiple approaches to find depth chart data
            
            # Approach 1: Look for tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Try to extract position and player names
                        position_text = cells[0].get_text(strip=True)
                        
                        # Look for position codes (QB, RB, WR, etc.)
                        if len(position_text) <= 4 and position_text.isupper():
                            # Get player name(s) from remaining cells
                            for cell in cells[1:]:
                                player_name = cell.get_text(strip=True)
                                if player_name and len(player_name) > 2:
                                    # Only get the first player (starter)
                                    starters.append({
                                        'team': team_name,
                                        'player': player_name,
                                        'position': position_text
                                    })
                                    break  # Only take the first player (starter)
            
            # Approach 2: Look for divs with position classes
            position_divs = soup.find_all('div', class_=lambda x: x and ('position' in x.lower() or 'player' in x.lower()))
            
            current_position = None
            for div in position_divs:
                text = div.get_text(strip=True)
                
                # Check if this is a position heading
                if len(text) <= 4 and text.isupper():
                    current_position = text
                elif current_position and len(text) > 2:
                    # This might be a player name
                    starters.append({
                        'team': team_name,
                        'player': text,
                        'position': current_position
                    })
                    current_position = None  # Reset after getting starter
            
            logger.info(f"Extracted {len(starters)} starters from {team_name}")
            
        except Exception as e:
            logger.error(f"Error parsing depth chart for {team_name}: {str(e)}")
        
        return starters
    
    def scrape_all_depth_charts(self) -> List[Dict[str, str]]:
        """
        Scrape depth chart information for all teams.
        
        Returns:
            List of dictionaries containing team, player, and position for all starters
        """
        all_starters = []
        
        # Fetch main page
        logger.info("Fetching main depth chart page")
        main_page_html = self.fetch_page(self.base_url)
        
        if not main_page_html:
            logger.error("Failed to fetch main depth chart page")
            return all_starters
        
        # Parse team links
        teams = self.parse_team_links(main_page_html)
        
        if not teams:
            logger.warning("No team links found, attempting direct parsing of main page")
            # Try to parse starters directly from main page
            starters = self.parse_depth_chart(main_page_html, "Various Teams")
            all_starters.extend(starters)
        else:
            # Fetch each team's depth chart
            for i, team_info in enumerate(teams):
                logger.info(f"Processing team {i+1}/{len(teams)}: {team_info['team']}")
                
                team_html = self.fetch_page(team_info['url'])
                if team_html:
                    starters = self.parse_depth_chart(team_html, team_info['team'])
                    all_starters.extend(starters)
                else:
                    logger.warning(f"Failed to fetch depth chart for {team_info['team']}")
        
        logger.info(f"Total starters scraped: {len(all_starters)}")
        return all_starters
    
    def save_to_csv(self, starters: List[Dict[str, str]], output_path: str = "data/starters.csv"):
        """
        Save starters data to a CSV file.
        
        Args:
            starters: List of starter dictionaries
            output_path: Path to output CSV file
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Use pandas for better CSV handling
            df = pd.DataFrame(starters)
            
            # Ensure columns are in the specified order
            df = df[['team', 'player', 'position']]
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            
            logger.info(f"Successfully saved {len(starters)} starters to {output_path}")
            print(f"\n✓ Saved {len(starters)} starters to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")
            raise
    
    def run(self, output_path: str = "data/starters.csv"):
        """
        Run the complete scraping process and save results.
        
        Args:
            output_path: Path to output CSV file
        """
        logger.info("Starting depth chart scraping process")
        print("Starting OurLads NCAA Football Depth Chart Scraper...")
        print(f"Target URL: {self.base_url}")
        print(f"Rate limit: {self.rate_limit_delay} seconds between requests")
        print()
        
        # Scrape all depth charts
        starters = self.scrape_all_depth_charts()
        
        if not starters:
            logger.warning("No starter data was scraped")
            print("\n⚠ Warning: No starter data was scraped. The website structure may have changed.")
            print("Please check the logs for details.")
            return
        
        # Save to CSV
        self.save_to_csv(starters, output_path)
        
        # Print summary
        print(f"\nSummary:")
        print(f"  - Total starters: {len(starters)}")
        if starters:
            df = pd.DataFrame(starters)
            print(f"  - Unique teams: {df['team'].nunique()}")
            print(f"  - Unique positions: {df['position'].nunique()}")
        
        logger.info("Scraping process completed")


def main():
    """Main entry point for the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape NCAA football depth charts from OurLads.com'
    )
    parser.add_argument(
        '--output',
        '-o',
        default='data/starters.csv',
        help='Output CSV file path (default: data/starters.csv)'
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=2.0,
        help='Rate limit delay in seconds between requests (default: 2.0)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create scraper and run
    scraper = DepthChartScraper(rate_limit_delay=args.delay)
    scraper.run(output_path=args.output)


if __name__ == '__main__':
    main()
