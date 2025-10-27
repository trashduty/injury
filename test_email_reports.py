"""
Unit tests for report generation and email delivery functionality.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import tempfile
import shutil
from datetime import datetime

import config
from report_generator import ReportGenerator
from email_delivery import EmailDelivery


class TestReportGenerator(unittest.TestCase):
    """Test cases for report generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.original_output_dir = config.OUTPUT_CONFIG['output_directory']
        config.OUTPUT_CONFIG['output_directory'] = self.test_dir
        
        self.generator = ReportGenerator()
        
        self.sample_items = [
            {
                'title': 'Test Item 1',
                'link': 'https://example.com/item1',
                'feed_name': 'Test Feed',
                'pubDate': 'Mon, 01 Jan 2024 12:00:00 GMT',
                'description': 'Test description 1',
                'guid': 'item1-guid'
            },
            {
                'title': 'Test Item 2',
                'link': 'https://example.com/item2',
                'feed_name': 'Test Feed 2',
                'pubDate': 'Mon, 01 Jan 2024 13:00:00 GMT',
                'description': 'Test description 2',
            }
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        config.OUTPUT_CONFIG['output_directory'] = self.original_output_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_generate_markdown(self):
        """Test Markdown report generation."""
        metadata = {
            'generated_at': '2024-01-01 12:00:00',
            'total_items': 2,
            'feeds_count': 2
        }
        
        filepath = self.generator.generate_markdown(self.sample_items, metadata)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.md'))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check content
        self.assertIn('# News Aggregator Report', content)
        self.assertIn('Test Item 1', content)
        self.assertIn('Test Item 2', content)
        self.assertIn('https://example.com/item1', content)
        self.assertIn('Test Feed', content)
    
    def test_generate_csv(self):
        """Test CSV report generation."""
        filepath = self.generator.generate_csv(self.sample_items)
        
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check headers
        self.assertIn('title', content)
        self.assertIn('link', content)
        self.assertIn('feed_name', content)
        
        # Check data
        self.assertIn('Test Item 1', content)
        self.assertIn('https://example.com/item1', content)
    
    def test_generate_all_formats(self):
        """Test generating all formats."""
        metadata = self.generator.get_report_metadata(self.sample_items)
        generated_files = self.generator.generate_all_formats(
            self.sample_items, metadata
        )
        
        self.assertIn('markdown', generated_files)
        self.assertIn('csv', generated_files)
        
        for filepath in generated_files.values():
            self.assertTrue(os.path.exists(filepath))
    
    def test_get_report_metadata(self):
        """Test metadata generation."""
        metadata = self.generator.get_report_metadata(self.sample_items)
        
        self.assertIn('generated_at', metadata)
        self.assertIn('total_items', metadata)
        self.assertIn('feeds_count', metadata)
        self.assertIn('feeds', metadata)
        
        self.assertEqual(metadata['total_items'], 2)
        self.assertEqual(metadata['feeds_count'], 2)
        self.assertIn('Test Feed', metadata['feeds'])
    
    def test_markdown_with_long_description(self):
        """Test Markdown generation with long descriptions."""
        long_desc = 'A' * 600  # Longer than 500 chars
        items = [{
            'title': 'Test',
            'link': 'https://example.com',
            'description': long_desc
        }]
        
        filepath = self.generator.generate_markdown(items)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should be truncated
        self.assertIn('...', content)
    
    def test_csv_with_missing_fields(self):
        """Test CSV generation with missing fields."""
        items = [{
            'title': 'Only Title',
        }]
        
        filepath = self.generator.generate_csv(items)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have headers even with missing data
        self.assertIn('title', content)
        self.assertIn('Only Title', content)


class TestEmailDelivery(unittest.TestCase):
    """Test cases for email delivery."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.original_config = config.EMAIL_CONFIG.copy()
        
        # Set up test email config
        config.EMAIL_CONFIG.update({
            'enabled': True,
            'host': 'smtp.example.com',
            'port': 587,
            'username': 'test@example.com',
            'password': 'testpass',
            'to_email': 'recipient@example.com',
            'use_tls': True,
            'use_ssl': False,
        })
        
        self.email_handler = EmailDelivery()
        
        self.sample_items = [
            {
                'title': 'Test Item 1',
                'link': 'https://example.com/item1',
                'feed_name': 'Test Feed',
                'pubDate': 'Mon, 01 Jan 2024 12:00:00 GMT',
                'description': 'Test description 1',
            }
        ]
        
        self.sample_metadata = {
            'generated_at': '2024-01-01 12:00:00',
            'total_items': 1,
            'feeds_count': 1
        }
    
    def tearDown(self):
        """Clean up after tests."""
        config.EMAIL_CONFIG = self.original_config
    
    def test_validate_config_success(self):
        """Test email configuration validation with valid config."""
        self.assertTrue(self.email_handler._validate_config())
    
    def test_validate_config_missing_fields(self):
        """Test email configuration validation with missing fields."""
        config.EMAIL_CONFIG['username'] = ''
        
        self.assertFalse(self.email_handler._validate_config())
    
    def test_disabled_email(self):
        """Test that email is not sent when disabled."""
        config.EMAIL_CONFIG['enabled'] = False
        
        result = self.email_handler.send_email(
            self.sample_items,
            self.sample_metadata,
            []
        )
        
        self.assertFalse(result)
    
    def test_format_items_html(self):
        """Test HTML formatting of items."""
        html = self.email_handler._format_items_html(self.sample_items, 10)
        
        self.assertIn('Test Item 1', html)
        self.assertIn('https://example.com/item1', html)
        self.assertIn('Test Feed', html)
        self.assertIn('<div class="item">', html)
    
    def test_format_items_text(self):
        """Test plain text formatting of items."""
        text = self.email_handler._format_items_text(self.sample_items, 10)
        
        self.assertIn('Test Item 1', text)
        self.assertIn('https://example.com/item1', text)
        self.assertIn('Test Feed', text)
    
    def test_create_email_body(self):
        """Test email body creation."""
        html_body, text_body = self.email_handler._create_email_body(
            self.sample_items,
            self.sample_metadata
        )
        
        # Check HTML body
        self.assertIsNotNone(html_body)
        self.assertIn('Test Item 1', html_body)
        
        # Check text body
        self.assertIsNotNone(text_body)
        self.assertIn('Test Item 1', text_body)
    
    def test_create_email_body_with_many_items(self):
        """Test email body creation with more items than max_items_in_summary."""
        many_items = self.sample_items * 20  # Create 20 items
        metadata = {
            'generated_at': '2024-01-01 12:00:00',
            'total_items': len(many_items),
            'feeds_count': 1
        }
        
        html_body, text_body = self.email_handler._create_email_body(
            many_items,
            metadata
        )
        
        # Should include "more items" message
        self.assertIn('more items', html_body.lower())
        self.assertIn('more items', text_body.lower())
    
    @patch('email_delivery.smtplib.SMTP')
    @patch('os.path.exists')
    def test_send_email_success(self, mock_exists, mock_smtp):
        """Test successful email sending."""
        mock_exists.return_value = True
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Create a temporary test file
        test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        test_file.write(b'Test content')
        test_file.close()
        
        try:
            result = self.email_handler.send_email(
                self.sample_items,
                self.sample_metadata,
                [test_file.name]
            )
            
            self.assertTrue(result)
            mock_smtp.assert_called_once()
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
            mock_server.quit.assert_called_once()
        finally:
            os.unlink(test_file.name)
    
    @patch('email_delivery.smtplib.SMTP')
    def test_send_email_authentication_error(self, mock_smtp):
        """Test email sending with authentication error."""
        import smtplib
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, b'Authentication failed'
        )
        mock_smtp.return_value = mock_server
        
        result = self.email_handler.send_email(
            self.sample_items,
            self.sample_metadata,
            []
        )
        
        self.assertFalse(result)
    
    @patch('email_delivery.smtplib.SMTP_SSL')
    def test_send_email_with_ssl(self, mock_smtp_ssl):
        """Test email sending with SSL."""
        config.EMAIL_CONFIG['use_ssl'] = True
        config.EMAIL_CONFIG['use_tls'] = False
        
        mock_server = MagicMock()
        mock_smtp_ssl.return_value = mock_server
        
        self.email_handler.send_email(
            self.sample_items,
            self.sample_metadata,
            []
        )
        
        mock_smtp_ssl.assert_called_once()
        # Should NOT call starttls when using SSL
        mock_server.starttls.assert_not_called()
    
    def test_load_template_not_found(self):
        """Test loading a template that doesn't exist."""
        template = self.email_handler._load_template('nonexistent.html')
        self.assertIsNone(template)


class TestConfigUpdates(unittest.TestCase):
    """Test cases for configuration updates."""
    
    def test_email_config_exists(self):
        """Test that email configuration is present."""
        self.assertIn('enabled', config.EMAIL_CONFIG)
        self.assertIn('host', config.EMAIL_CONFIG)
        self.assertIn('port', config.EMAIL_CONFIG)
        self.assertIn('username', config.EMAIL_CONFIG)
        self.assertIn('password', config.EMAIL_CONFIG)
        self.assertIn('to_email', config.EMAIL_CONFIG)
    
    def test_output_config_exists(self):
        """Test that output configuration is present."""
        self.assertIn('formats', config.OUTPUT_CONFIG)
        self.assertIn('output_directory', config.OUTPUT_CONFIG)
        self.assertIn('filename_template', config.OUTPUT_CONFIG)
    
    def test_email_template_config_exists(self):
        """Test that email template configuration is present."""
        self.assertIn('html_template', config.EMAIL_TEMPLATE_CONFIG)
        self.assertIn('text_template', config.EMAIL_TEMPLATE_CONFIG)
        self.assertIn('subject_template', config.EMAIL_TEMPLATE_CONFIG)
    
    def test_default_output_formats(self):
        """Test default output formats."""
        self.assertIn('markdown', config.OUTPUT_CONFIG['formats'])
        self.assertIn('csv', config.OUTPUT_CONFIG['formats'])


if __name__ == '__main__':
    unittest.main()
