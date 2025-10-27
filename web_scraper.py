"""
Web Scraper Module

This module handles web scraping for injury reports and depth charts
from sources that don't provide RSS feeds.
"""

import logging
import time
import re
from typing import List, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import socket

import config


logger = logging.getLogger(__name__)


class InjuryReportParser(HTMLParser):
    """HTML parser for Covers.com injury reports."""
    
    def __init__(self):
        super().__init__()
        self.injuries = []
        self.current_item = {}
        self.in_injury_section = False
        self.in_player_name = False
        self.in_position = False
        self.in_status = False
        self.in_team = False
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        # Detect injury table or list sections
        if tag in ['tr', 'div'] and any('injury' in str(v).lower() or 'player' in str(v).lower() 
                                        for k, v in attrs if k == 'class'):
            self.in_injury_section = True
            self.current_item = {}
    
    def handle_endtag(self, tag):
        """Handle closing HTML tags."""
        if tag in ['tr', 'div'] and self.in_injury_section:
            # Save completed injury item
            if self.current_item and 'player' in self.current_item:
                self.injuries.append(self.current_item.copy())
            self.in_injury_section = False
            self.current_item = {}
        self.current_tag = None
    
    def handle_data(self, data):
        """Handle text data within HTML tags."""
        if not self.in_injury_section or not data.strip():
            return
        
        data = data.strip()
        
        # Simple heuristic to identify data based on context
        # This is a basic implementation and would need refinement for actual scraping
        if self.current_tag in ['td', 'span', 'div', 'p']:
            if not self.current_item.get('player'):
                self.current_item['player'] = data
            elif not self.current_item.get('position'):
                self.current_item['position'] = data
            elif not self.current_item.get('status'):
                self.current_item['status'] = data
            elif not self.current_item.get('team'):
                self.current_item['team'] = data


class DepthChartParser(HTMLParser):
    """HTML parser for Ourlads.com depth charts."""
    
    def __init__(self):
        super().__init__()
        self.depth_chart = {}
        self.current_team = None
        self.current_position = None
        self.in_player_name = False
        
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        attrs_dict = dict(attrs)
        
        # Detect team sections
        if tag in ['h2', 'h3'] and any('team' in str(v).lower() for k, v in attrs if k == 'class'):
            self.current_team = None
    
    def handle_data(self, data):
        """Handle text data within HTML tags."""
        data = data.strip()
        if not data:
            return
        
        # Basic heuristic for parsing depth charts
        # In a real implementation, this would need to be more sophisticated
        if self.current_team and data:
            if data.isupper() and len(data) <= 4:  # Position code like "QB", "RB", "WR"
                self.current_position = data
            elif self.current_position:
                if self.current_team not in self.depth_chart:
                    self.depth_chart[self.current_team] = {}
                if self.current_position not in self.depth_chart[self.current_team]:
                    self.depth_chart[self.current_team][self.current_position] = []
                self.depth_chart[self.current_team][self.current_position].append(data)


class WebScraper:
    """Handler for web scraping with rate limiting and error handling."""
    
    def __init__(self):
        """Initialize the web scraper."""
        self.last_request_time = 0
        self.depth_chart_cache = {}
        self.depth_chart_cache_time = 0
        logger.info("Web Scraper initialized")
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < config.WEB_SCRAPING_CONFIG['rate_limit_delay']:
            sleep_time = config.WEB_SCRAPING_CONFIG['rate_limit_delay'] - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_html(self, url: str, timeout: int = None) -> Optional[str]:
        """
        Fetch HTML content from a URL with error handling.
        
        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content as string, or None if fetch failed
        """
        if timeout is None:
            timeout = config.WEB_SCRAPING_CONFIG['timeout']
        
        retries = 0
        max_retries = config.WEB_SCRAPING_CONFIG['max_retries']
        
        while retries < max_retries:
            try:
                # Apply rate limiting
                self._rate_limit()
                
                logger.info(f"Fetching HTML from {url} (attempt {retries + 1}/{max_retries})")
                
                # Create request with user agent
                request = Request(
                    url,
                    headers={'User-Agent': config.WEB_SCRAPING_CONFIG['user_agent']}
                )
                
                with urlopen(request, timeout=timeout) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    logger.info(f"Successfully fetched HTML from {url}")
                    return content
                    
            except HTTPError as e:
                logger.error(f"HTTP error fetching {url}: {e.code} - {e.reason}")
                if e.code in [404, 410, 403]:  # Don't retry on these errors
                    break
                    
            except URLError as e:
                logger.error(f"URL error fetching {url}: {e.reason}")
                
            except socket.timeout:
                logger.error(f"Timeout fetching {url}")
                
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {str(e)}")
            
            retries += 1
            if retries < max_retries:
                time.sleep(config.WEB_SCRAPING_CONFIG['rate_limit_delay'])
        
        logger.error(f"Failed to fetch HTML from {url} after {max_retries} attempts")
        return None
    
    def scrape_covers_injuries(self) -> List[Dict[str, Any]]:
        """
        Scrape injury reports from Covers.com.
        
        Returns:
            List of injury report items
        """
        url = config.WEB_SCRAPING_CONFIG['covers_injury_url']
        logger.info(f"Scraping injury reports from {url}")
        
        html_content = self.fetch_html(url)
        if not html_content:
            return []
        
        try:
            parser = InjuryReportParser()
            parser.feed(html_content)
            
            # Convert to standard format
            items = []
            for injury in parser.injuries:
                item = {
                    'title': f"{injury.get('player', 'Unknown Player')} - {injury.get('status', 'Status Unknown')}",
                    'description': f"Position: {injury.get('position', 'N/A')}, Status: {injury.get('status', 'N/A')}",
                    'feed_name': 'Covers.com Injury Report',
                    'team': injury.get('team', 'Unknown'),
                    'player': injury.get('player', 'Unknown'),
                    'position': injury.get('position', 'N/A'),
                    'status': injury.get('status', 'N/A'),
                    'pubDate': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'link': url,
                }
                items.append(item)
            
            logger.info(f"Scraped {len(items)} injury reports from Covers.com")
            return items
            
        except Exception as e:
            logger.error(f"Error parsing Covers.com injury data: {str(e)}")
            return []
    
    def fetch_depth_chart(self, team: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch depth chart data from Ourlads.com.
        
        Args:
            team: Optional team name to filter
            
        Returns:
            Dictionary mapping teams to positions to players
        """
        # Check cache
        current_time = time.time()
        cache_duration = config.DEPTH_CHART_CONFIG['cache_duration']
        
        if (current_time - self.depth_chart_cache_time < cache_duration 
            and self.depth_chart_cache):
            logger.info("Using cached depth chart data")
            return self.depth_chart_cache
        
        url = config.WEB_SCRAPING_CONFIG['ourlads_depth_chart_url']
        logger.info(f"Fetching depth chart from {url}")
        
        html_content = self.fetch_html(url)
        if not html_content:
            # Return cached data if available
            if self.depth_chart_cache:
                logger.info("Returning stale depth chart cache")
                return self.depth_chart_cache
            return {}
        
        try:
            parser = DepthChartParser()
            parser.feed(html_content)
            
            self.depth_chart_cache = parser.depth_chart
            self.depth_chart_cache_time = current_time
            
            logger.info(f"Fetched depth chart for {len(parser.depth_chart)} teams")
            return parser.depth_chart
            
        except Exception as e:
            logger.error(f"Error parsing Ourlads depth chart: {str(e)}")
            # Return cached data if available
            if self.depth_chart_cache:
                logger.info("Returning stale depth chart cache after error")
                return self.depth_chart_cache
            return {}
    
    def get_player_position(self, player_name: str, team: Optional[str] = None) -> Optional[str]:
        """
        Get a player's position from the depth chart.
        
        Args:
            player_name: Name of the player
            team: Optional team name to narrow search
            
        Returns:
            Position string or None if not found
        """
        depth_chart = self.fetch_depth_chart(team)
        
        # Search for player in depth chart
        for team_name, positions in depth_chart.items():
            if team and team.lower() not in team_name.lower():
                continue
            
            for position, players in positions.items():
                for player in players:
                    if player_name.lower() in player.lower() or player.lower() in player_name.lower():
                        return position
        
        return None
    
    def enrich_items_with_positions(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich news items with position information from depth chart.
        
        Args:
            items: List of news items
            
        Returns:
            List of items enriched with position data
        """
        if not config.DEPTH_CHART_CONFIG['enabled']:
            return items
        
        logger.info(f"Enriching {len(items)} items with depth chart positions")
        
        # Fetch depth chart once
        depth_chart = self.fetch_depth_chart()
        
        for item in items:
            # Try to extract player name and team from title or description
            if 'player' not in item or 'position' not in item:
                # Use simple heuristics to extract player names
                text = item.get('title', '') + ' ' + item.get('description', '')
                
                # This is a simplified extraction - in production would need better NLP
                # For now, if the item already has player/position from scraping, use that
                if 'player' in item and item.get('player') != 'Unknown':
                    position = self.get_player_position(
                        item['player'], 
                        item.get('team')
                    )
                    if position and not item.get('position'):
                        item['position'] = position
        
        return items
