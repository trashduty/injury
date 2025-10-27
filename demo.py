#!/usr/bin/env python3
"""
Demo script to test report generation and email delivery with mock data.
"""

import logging
from news_aggregator import configure_logging
from report_generator import ReportGenerator
from email_delivery import EmailDelivery

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Mock feed items
mock_items = [
    {
        'title': 'Breaking News: Python 3.13 Released',
        'link': 'https://example.com/python-3.13',
        'feed_name': 'Tech News',
        'pubDate': 'Mon, 27 Oct 2025 10:00:00 GMT',
        'description': 'Python 3.13 introduces exciting new features including improved performance and better type hints.',
        'guid': 'tech-001'
    },
    {
        'title': 'AI Breakthrough: New Language Model Announced',
        'link': 'https://example.com/ai-breakthrough',
        'feed_name': 'AI News',
        'pubDate': 'Mon, 27 Oct 2025 11:30:00 GMT',
        'description': 'Researchers announce a groundbreaking new language model with unprecedented capabilities.',
        'guid': 'ai-001'
    },
    {
        'title': 'Climate Change: Global Summit Begins',
        'link': 'https://example.com/climate-summit',
        'feed_name': 'World News',
        'pubDate': 'Mon, 27 Oct 2025 09:15:00 GMT',
        'description': 'World leaders gather for the annual climate summit to discuss urgent environmental issues.',
        'guid': 'world-001'
    },
    {
        'title': 'Tech Industry: New Privacy Regulations',
        'link': 'https://example.com/privacy-regulations',
        'feed_name': 'Tech News',
        'pubDate': 'Mon, 27 Oct 2025 08:45:00 GMT',
        'description': 'Government announces comprehensive new privacy regulations affecting major tech companies.',
        'guid': 'tech-002'
    },
    {
        'title': 'Space Exploration: Mars Mission Update',
        'link': 'https://example.com/mars-mission',
        'feed_name': 'Science News',
        'pubDate': 'Mon, 27 Oct 2025 12:00:00 GMT',
        'description': 'NASA provides exciting updates on the ongoing Mars exploration mission.',
        'guid': 'science-001'
    }
]

def main():
    """Run demo with mock data."""
    logger.info("Starting Report Generation Demo")
    
    print("\n" + "="*70)
    print("NEWS AGGREGATOR DEMO")
    print("="*70)
    
    print(f"\n✓ Generated {len(mock_items)} mock news items")
    
    # Generate reports
    print("\n📝 Generating reports...")
    report_gen = ReportGenerator()
    metadata = report_gen.get_report_metadata(mock_items)
    
    print(f"   Report metadata:")
    print(f"   - Generated at: {metadata['generated_at']}")
    print(f"   - Total items: {metadata['total_items']}")
    print(f"   - Feeds processed: {metadata['feeds_count']}")
    print(f"   - Feeds: {', '.join(metadata['feeds'])}")
    
    generated_files = report_gen.generate_all_formats(mock_items, metadata)
    
    print(f"\n✓ Generated {len(generated_files)} report files:")
    for format_name, filepath in generated_files.items():
        print(f"   - {format_name.upper()}: {filepath}")
    
    # Test email (will not actually send without proper config)
    print("\n📧 Testing email delivery...")
    email_handler = EmailDelivery()
    
    import config
    if config.EMAIL_CONFIG.get('enabled'):
        print("   Email is ENABLED - attempting to send...")
        attachments = list(generated_files.values())
        success = email_handler.send_email(mock_items, metadata, attachments)
        
        if success:
            print("   ✓ Email sent successfully!")
        else:
            print("   ✗ Email failed to send (check configuration)")
    else:
        print("   Email is DISABLED in configuration")
        print("   To enable email delivery, set environment variables:")
        print("     - EMAIL_ENABLED=true")
        print("     - EMAIL_HOST=smtp.gmail.com")
        print("     - EMAIL_PORT=587")
        print("     - EMAIL_USERNAME=your-email@gmail.com")
        print("     - EMAIL_PASSWORD=your-app-password")
        print("     - EMAIL_TO=recipient@email.com")
    
    print("\n" + "="*70)
    print("DEMO COMPLETED")
    print("="*70)
    print("\nCheck the 'reports/' directory for generated files.")
    print()

if __name__ == '__main__':
    main()
