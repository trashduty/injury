"""
Example usage of the NCAA Football Depth Chart Scraper

This script demonstrates how to use the depth_chart_scraper module
to scrape depth chart data and export it to CSV.
"""

from depth_chart_scraper import DepthChartScraper, ALLOWED_URL


def main():
    """Main example function."""
    print("NCAA Football Depth Chart Scraper - Example Usage")
    print("=" * 70)
    print()
    
    # 1. Create scraper instance
    print("Step 1: Creating scraper instance...")
    scraper = DepthChartScraper()
    print("✓ Scraper created successfully")
    print()
    
    # 2. Show the allowed URL
    print("Step 2: Checking allowed URL...")
    print(f"  Allowed URL: {ALLOWED_URL}")
    print("  This is the only URL the scraper will access")
    print()
    
    # 3. Scrape depth chart data
    print("Step 3: Scraping depth chart data...")
    print("  This will:")
    print("  - Verify connection to the website")
    print("  - Fetch HTML content")
    print("  - Parse depth chart data")
    print("  - Extract starter positions")
    print()
    
    depth_chart_data = scraper.scrape_depth_chart()
    
    if depth_chart_data:
        print(f"✓ Successfully scraped {len(depth_chart_data)} depth chart entries")
        print()
        
        # 4. Export to CSV
        print("Step 4: Exporting to CSV...")
        output_file = 'ncaa_depth_chart.csv'
        success = scraper.export_to_csv(depth_chart_data, output_file)
        
        if success:
            print(f"✓ Data exported to {output_file}")
            print()
            print("CSV Format:")
            print("  team,player,position")
            print("  Alabama,John Doe,QB")
            print("  Georgia,Jane Smith,RB")
            print("  ...")
        else:
            print("✗ Failed to export data to CSV")
    else:
        print("✗ No depth chart data was scraped")
        print()
        print("This could be because:")
        print("  - The website structure changed")
        print("  - Connection issues")
        print("  - The parser needs to be updated")
    
    print()
    print("=" * 70)
    print("Example completed!")


if __name__ == '__main__':
    main()
