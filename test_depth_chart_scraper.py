"""
Unit tests for depth_chart_scraper module.

Tests cover URL verification, connection checking, HTML parsing,
CSV export, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import socket
import csv
import os
import tempfile

from depth_chart_scraper import (
    DepthChartScraper,
    DepthChartParser,
    ALLOWED_URL,
    SCRAPER_CONFIG
)


class TestDepthChartParser(unittest.TestCase):
    """Test cases for depth chart HTML parser."""
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        parser = DepthChartParser()
        self.assertEqual(len(parser.depth_chart), 0)
        self.assertIsNone(parser.current_team)
        self.assertIsNone(parser.current_position)
    
    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        parser = DepthChartParser()
        parser.feed('<html><body></body></html>')
        self.assertEqual(len(parser.depth_chart), 0)


class TestDepthChartScraper(unittest.TestCase):
    """Test cases for depth chart scraper."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = DepthChartScraper()
    
    def test_initialization(self):
        """Test scraper initializes correctly."""
        self.assertEqual(self.scraper.last_request_time, 0)
    
    def test_verify_url_allowed(self):
        """Test URL verification accepts allowed URL."""
        result = self.scraper._verify_url(ALLOWED_URL)
        self.assertTrue(result)
    
    def test_verify_url_not_allowed(self):
        """Test URL verification rejects non-whitelisted URLs."""
        result = self.scraper._verify_url('https://example.com/other-site')
        self.assertFalse(result)
    
    def test_verify_url_different_domain(self):
        """Test URL verification rejects different domains."""
        result = self.scraper._verify_url('https://www.nfl.com/depth-charts')
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_verify_connection_success(self, mock_socket):
        """Test successful connection verification."""
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        
        result = self.scraper.verify_connection(ALLOWED_URL)
        
        self.assertTrue(result)
        mock_sock_instance.connect.assert_called_once()
        mock_sock_instance.close.assert_called_once()
    
    @patch('socket.socket')
    def test_verify_connection_dns_error(self, mock_socket):
        """Test connection verification handles DNS errors."""
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect.side_effect = socket.gaierror("DNS resolution failed")
        mock_socket.return_value = mock_sock_instance
        
        result = self.scraper.verify_connection(ALLOWED_URL)
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_verify_connection_timeout(self, mock_socket):
        """Test connection verification handles timeout."""
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect.side_effect = socket.timeout()
        mock_socket.return_value = mock_sock_instance
        
        result = self.scraper.verify_connection(ALLOWED_URL)
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_verify_connection_refused(self, mock_socket):
        """Test connection verification handles connection refused."""
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect.side_effect = ConnectionRefusedError()
        mock_socket.return_value = mock_sock_instance
        
        result = self.scraper.verify_connection(ALLOWED_URL)
        
        self.assertFalse(result)
    
    @patch('socket.socket')
    def test_verify_connection_generic_error(self, mock_socket):
        """Test connection verification handles generic errors."""
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect.side_effect = Exception("Generic error")
        mock_socket.return_value = mock_sock_instance
        
        result = self.scraper.verify_connection(ALLOWED_URL)
        
        self.assertFalse(result)
    
    @patch('depth_chart_scraper.DepthChartScraper.verify_connection')
    @patch('depth_chart_scraper.urlopen')
    def test_fetch_html_success(self, mock_urlopen, mock_verify):
        """Test successful HTML fetching."""
        mock_verify.return_value = True
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html>test</html>'
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response
        
        content = self.scraper.fetch_html(ALLOWED_URL)
        
        self.assertEqual(content, '<html>test</html>')
        mock_urlopen.assert_called_once()
        mock_verify.assert_called_once()
    
    @patch('depth_chart_scraper.DepthChartScraper.verify_connection')
    def test_fetch_html_connection_verification_fails(self, mock_verify):
        """Test fetch HTML when connection verification fails."""
        mock_verify.return_value = False
        
        content = self.scraper.fetch_html(ALLOWED_URL)
        
        self.assertIsNone(content)
        mock_verify.assert_called_once()
    
    def test_fetch_html_url_not_allowed(self):
        """Test fetch HTML with non-whitelisted URL."""
        content = self.scraper.fetch_html('https://example.com/other')
        
        self.assertIsNone(content)
    
    @patch('depth_chart_scraper.DepthChartScraper.verify_connection')
    @patch('depth_chart_scraper.urlopen')
    def test_fetch_html_http_404_error(self, mock_urlopen, mock_verify):
        """Test handling of 404 HTTP error."""
        from urllib.error import HTTPError
        
        mock_verify.return_value = True
        mock_urlopen.side_effect = HTTPError(
            ALLOWED_URL,
            404,
            'Not Found',
            {},
            None
        )
        
        content = self.scraper.fetch_html(ALLOWED_URL)
        
        self.assertIsNone(content)
        # Should not retry on 404
        self.assertEqual(mock_urlopen.call_count, 1)
    
    @patch('depth_chart_scraper.DepthChartScraper.verify_connection')
    @patch('depth_chart_scraper.urlopen')
    def test_fetch_html_http_403_error(self, mock_urlopen, mock_verify):
        """Test handling of 403 HTTP error."""
        from urllib.error import HTTPError
        
        mock_verify.return_value = True
        mock_urlopen.side_effect = HTTPError(
            ALLOWED_URL,
            403,
            'Forbidden',
            {},
            None
        )
        
        content = self.scraper.fetch_html(ALLOWED_URL)
        
        self.assertIsNone(content)
        # Should not retry on 403
        self.assertEqual(mock_urlopen.call_count, 1)
    
    @patch('depth_chart_scraper.DepthChartScraper.verify_connection')
    @patch('depth_chart_scraper.urlopen')
    def test_fetch_html_retry_logic(self, mock_urlopen, mock_verify):
        """Test retry logic for failed fetches."""
        from urllib.error import URLError
        
        mock_verify.return_value = True
        mock_urlopen.side_effect = URLError('Connection refused')
        
        content = self.scraper.fetch_html(ALLOWED_URL)
        
        self.assertIsNone(content)
        # Should retry max_retries times
        self.assertEqual(mock_urlopen.call_count, SCRAPER_CONFIG['max_retries'])
    
    @patch('depth_chart_scraper.DepthChartScraper.fetch_html')
    def test_scrape_depth_chart_no_data(self, mock_fetch):
        """Test scraping when no data is available."""
        mock_fetch.return_value = None
        
        data = self.scraper.scrape_depth_chart()
        
        self.assertEqual(len(data), 0)
    
    @patch('depth_chart_scraper.DepthChartScraper.fetch_html')
    def test_scrape_depth_chart_with_data(self, mock_fetch):
        """Test scraping with valid HTML data."""
        mock_fetch.return_value = '<html><body>Test</body></html>'
        
        data = self.scraper.scrape_depth_chart()
        
        # Should return a list (may be empty if parser doesn't find valid data)
        self.assertIsInstance(data, list)
    
    @patch('depth_chart_scraper.DepthChartScraper.fetch_html')
    def test_scrape_depth_chart_default_url(self, mock_fetch):
        """Test scraping uses default URL when none provided."""
        mock_fetch.return_value = '<html><body>Test</body></html>'
        
        data = self.scraper.scrape_depth_chart()
        
        # Should call fetch_html with ALLOWED_URL
        mock_fetch.assert_called_once_with(ALLOWED_URL)
    
    @patch('depth_chart_scraper.DepthChartScraper.fetch_html')
    def test_scrape_depth_chart_custom_url(self, mock_fetch):
        """Test scraping with custom URL (must be whitelisted)."""
        mock_fetch.return_value = '<html><body>Test</body></html>'
        
        data = self.scraper.scrape_depth_chart(url=ALLOWED_URL)
        
        # Should call fetch_html with provided URL
        mock_fetch.assert_called_once_with(ALLOWED_URL)
    
    def test_export_to_csv_no_data(self):
        """Test CSV export with no data."""
        result = self.scraper.export_to_csv([])
        
        self.assertFalse(result)
    
    def test_export_to_csv_with_data(self):
        """Test CSV export with valid data."""
        test_data = [
            {'team': 'Alabama', 'player': 'John Doe', 'position': 'QB'},
            {'team': 'Georgia', 'player': 'Jane Smith', 'position': 'RB'}
        ]
        
        # Use temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_filename = f.name
        
        try:
            result = self.scraper.export_to_csv(test_data, temp_filename)
            
            self.assertTrue(result)
            
            # Verify CSV content
            with open(temp_filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]['team'], 'Alabama')
                self.assertEqual(rows[0]['player'], 'John Doe')
                self.assertEqual(rows[0]['position'], 'QB')
                self.assertEqual(rows[1]['team'], 'Georgia')
                self.assertEqual(rows[1]['player'], 'Jane Smith')
                self.assertEqual(rows[1]['position'], 'RB')
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_export_to_csv_io_error(self, mock_open_func):
        """Test CSV export handles IO errors."""
        test_data = [
            {'team': 'Alabama', 'player': 'John Doe', 'position': 'QB'}
        ]
        
        result = self.scraper.export_to_csv(test_data)
        
        self.assertFalse(result)


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration constants."""
    
    def test_allowed_url_is_ncaa_football(self):
        """Test that allowed URL is NCAA football depth charts."""
        self.assertEqual(ALLOWED_URL, 'https://www.ourlads.com/ncaa-football-depth-charts/')
    
    def test_scraper_config_has_required_fields(self):
        """Test that scraper config has all required fields."""
        required_fields = ['timeout', 'max_retries', 'rate_limit_delay', 'user_agent']
        
        for field in required_fields:
            self.assertIn(field, SCRAPER_CONFIG)
    
    def test_scraper_config_values_are_reasonable(self):
        """Test that scraper config values are reasonable."""
        self.assertGreater(SCRAPER_CONFIG['timeout'], 0)
        self.assertGreater(SCRAPER_CONFIG['max_retries'], 0)
        self.assertGreater(SCRAPER_CONFIG['rate_limit_delay'], 0)
        self.assertIsInstance(SCRAPER_CONFIG['user_agent'], str)
        self.assertTrue(len(SCRAPER_CONFIG['user_agent']) > 0)


if __name__ == '__main__':
    unittest.main()
