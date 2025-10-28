"""
Unit tests for web scraper module.

Tests cover HTML parsing, rate limiting, error handling,
and depth chart functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
import time

from web_scraper import WebScraper, InjuryReportParser, DepthChartParser
import config


class TestInjuryReportParser(unittest.TestCase):
    """Test cases for injury report HTML parser."""
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        parser = InjuryReportParser()
        self.assertEqual(len(parser.injuries), 0)
        self.assertFalse(parser.in_injury_section)
    
    def test_parse_simple_injury_data(self):
        """Test parsing simple injury HTML structure."""
        parser = InjuryReportParser()
        
        # Simple HTML structure
        html = '''
        <div class="injury-report">
            <tr class="player-row">
                <td>John Doe</td>
                <td>QB</td>
                <td>Questionable</td>
                <td>Alabama</td>
            </tr>
        </div>
        '''
        
        parser.feed(html)
        # Parser should extract some data
        self.assertIsInstance(parser.injuries, list)


class TestDepthChartParser(unittest.TestCase):
    """Test cases for depth chart HTML parser."""
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        parser = DepthChartParser()
        self.assertEqual(len(parser.depth_chart), 0)
        self.assertIsNone(parser.current_team)
        self.assertIsNone(parser.current_position)


class TestWebScraper(unittest.TestCase):
    """Test cases for web scraper."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WebScraper()
    
    def test_initialization(self):
        """Test web scraper initializes correctly."""
        self.assertEqual(self.scraper.last_request_time, 0)
        self.assertEqual(len(self.scraper.depth_chart_cache), 0)
        self.assertEqual(self.scraper.depth_chart_cache_time, 0)
    
    def test_rate_limiting(self):
        """Test rate limiting is applied."""
        # First request should not wait
        start_time = time.time()
        self.scraper._rate_limit()
        first_duration = time.time() - start_time
        
        # Immediate second request should wait
        start_time = time.time()
        self.scraper._rate_limit()
        second_duration = time.time() - start_time
        
        # Second request should take at least the rate limit delay
        self.assertGreaterEqual(
            second_duration, 
            config.WEB_SCRAPING_CONFIG['rate_limit_delay'] - 0.1
        )
    
    @patch('web_scraper.urlopen')
    def test_fetch_html_success(self, mock_urlopen):
        """Test successful HTML fetching."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html>test</html>'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response
        
        content = self.scraper.fetch_html('https://example.com')
        
        self.assertEqual(content, '<html>test</html>')
        mock_urlopen.assert_called_once()
    
    @patch('web_scraper.urlopen')
    def test_fetch_html_failure(self, mock_urlopen):
        """Test handling of fetch failures."""
        from urllib.error import HTTPError
        
        mock_urlopen.side_effect = HTTPError(
            'https://example.com',
            404,
            'Not Found',
            {},
            None
        )
        
        content = self.scraper.fetch_html('https://example.com')
        
        self.assertIsNone(content)
    
    @patch('web_scraper.urlopen')
    def test_fetch_html_retry_logic(self, mock_urlopen):
        """Test retry logic for failed fetches."""
        from urllib.error import URLError
        
        mock_urlopen.side_effect = URLError('Connection refused')
        
        # Should retry max_retries times
        self.scraper.fetch_html('https://example.com')
        
        self.assertEqual(
            mock_urlopen.call_count, 
            config.WEB_SCRAPING_CONFIG['max_retries']
        )
    
    @patch('web_scraper.WebScraper.fetch_html')
    def test_scrape_covers_injuries_no_data(self, mock_fetch):
        """Test scraping when no data is available."""
        mock_fetch.return_value = None
        
        items = self.scraper.scrape_covers_injuries()
        
        self.assertEqual(len(items), 0)
    
    @patch('web_scraper.WebScraper.fetch_html')
    def test_scrape_covers_injuries_with_data(self, mock_fetch):
        """Test scraping with valid HTML data."""
        # Simple HTML that parser might extract data from
        mock_fetch.return_value = '<html><body><div class="injury">Test</div></body></html>'
        
        items = self.scraper.scrape_covers_injuries()
        
        # Should return a list (possibly empty if no valid data)
        self.assertIsInstance(items, list)
    
    def test_depth_chart_caching(self):
        """Test depth chart caching mechanism."""
        # Populate cache
        self.scraper.depth_chart_cache = {'Team1': {'QB': ['Player1']}}
        self.scraper.depth_chart_cache_time = time.time()
        
        # Should return cached data
        result = self.scraper.fetch_depth_chart()
        
        self.assertEqual(result, {'Team1': {'QB': ['Player1']}})
    
    @patch('web_scraper.WebScraper.fetch_html')
    def test_fetch_depth_chart_failure_uses_cache(self, mock_fetch):
        """Test that stale cache is used when fetch fails."""
        # Populate cache
        self.scraper.depth_chart_cache = {'Team1': {'QB': ['Player1']}}
        self.scraper.depth_chart_cache_time = 0  # Old cache
        
        # Simulate fetch failure
        mock_fetch.return_value = None
        
        result = self.scraper.fetch_depth_chart()
        
        # Should return stale cache
        self.assertEqual(result, {'Team1': {'QB': ['Player1']}})
    
    def test_get_player_position_empty_chart(self):
        """Test getting position with empty depth chart."""
        position = self.scraper.get_player_position('John Doe')
        
        self.assertIsNone(position)
    
    def test_get_player_position_with_data(self):
        """Test getting position with populated depth chart."""
        # Populate depth chart
        self.scraper.depth_chart_cache = {
            'Alabama': {
                'QB': ['John Doe', 'Jane Smith'],
                'RB': ['Bob Johnson']
            }
        }
        self.scraper.depth_chart_cache_time = time.time()
        
        position = self.scraper.get_player_position('John Doe')
        
        self.assertEqual(position, 'QB')
    
    def test_enrich_items_with_positions(self):
        """Test enriching items with position data."""
        items = [
            {
                'title': 'Test Item',
                'player': 'John Doe',
                'team': 'Alabama'
            }
        ]
        
        # Populate depth chart
        self.scraper.depth_chart_cache = {
            'Alabama': {
                'QB': ['John Doe']
            }
        }
        self.scraper.depth_chart_cache_time = time.time()
        
        enriched = self.scraper.enrich_items_with_positions(items)
        
        self.assertEqual(enriched[0].get('position'), 'QB')
    
    def test_enrich_items_disabled(self):
        """Test enrichment when disabled in config."""
        items = [{'title': 'Test Item'}]
        
        # Temporarily disable
        original_enabled = config.DEPTH_CHART_CONFIG['enabled']
        config.DEPTH_CHART_CONFIG['enabled'] = False
        
        enriched = self.scraper.enrich_items_with_positions(items)
        
        # Should return items unchanged
        self.assertEqual(enriched, items)
        
        # Restore
        config.DEPTH_CHART_CONFIG['enabled'] = original_enabled


class TestWebScraperConfig(unittest.TestCase):
    """Test cases for web scraping configuration."""
    
    def test_web_scraping_config_exists(self):
        """Test that web scraping config is defined."""
        self.assertIn('WEB_SCRAPING_CONFIG', dir(config))
        self.assertIsInstance(config.WEB_SCRAPING_CONFIG, dict)
    
    def test_web_scraping_config_has_required_fields(self):
        """Test that config has all required fields."""
        required_fields = [
            'covers_injury_url',
            'ourlads_depth_chart_url',
            'rate_limit_delay',
            'user_agent',
            'timeout',
            'max_retries'
        ]
        
        for field in required_fields:
            self.assertIn(field, config.WEB_SCRAPING_CONFIG)
    
    def test_depth_chart_config_exists(self):
        """Test that depth chart config is defined."""
        self.assertIn('DEPTH_CHART_CONFIG', dir(config))
        self.assertIsInstance(config.DEPTH_CHART_CONFIG, dict)
        self.assertIn('enabled', config.DEPTH_CHART_CONFIG)
        self.assertIn('cache_duration', config.DEPTH_CHART_CONFIG)


if __name__ == '__main__':
    unittest.main()
