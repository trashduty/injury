"""
Report Generator Module

This module handles generating news reports in multiple formats
(Markdown and CSV) from aggregated feed items.
"""

import csv
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import config


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generator for creating news reports in various formats."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.output_dir = config.OUTPUT_CONFIG['output_directory']
        self._ensure_output_directory()
        logger.info("Report Generator initialized")
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def _generate_filename(self, format_extension: str) -> str:
        """
        Generate a filename with timestamp.
        
        Args:
            format_extension: File extension (e.g., 'md', 'csv')
            
        Returns:
            Generated filename with path
        """
        if config.OUTPUT_CONFIG['include_timestamp']:
            timestamp = datetime.now().strftime(config.OUTPUT_CONFIG['date_format'])
            filename_base = config.OUTPUT_CONFIG['filename_template'].format(
                timestamp=timestamp
            )
        else:
            filename_base = config.OUTPUT_CONFIG['filename_template'].replace(
                '_{timestamp}', ''
            )
        
        filename = f"{filename_base}.{format_extension}"
        return os.path.join(self.output_dir, filename)
    
    def generate_markdown(self, items: List[Dict[str, Any]], 
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a Markdown report from feed items.
        
        Args:
            items: List of feed items
            metadata: Optional metadata to include in the report
            
        Returns:
            Path to the generated Markdown file
        """
        logger.info(f"Generating Markdown report for {len(items)} items")
        
        filepath = self._generate_filename('md')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# News Aggregator Report\n\n")
            
            # Write metadata if provided
            if metadata:
                f.write("## Report Information\n\n")
                f.write(f"- **Generated:** {metadata.get('generated_at', 'N/A')}\n")
                f.write(f"- **Total Items:** {metadata.get('total_items', len(items))}\n")
                f.write(f"- **Feeds Processed:** {metadata.get('feeds_count', 'N/A')}\n")
                f.write("\n---\n\n")
            
            # Write items
            f.write("## News Items\n\n")
            
            for i, item in enumerate(items, 1):
                f.write(f"### {i}. {item.get('title', 'Untitled')}\n\n")
                
                # Source/Feed name
                if item.get('feed_name'):
                    f.write(f"**Source:** {item['feed_name']}\n\n")
                
                # Link
                if item.get('link'):
                    f.write(f"**Link:** [{item['link']}]({item['link']})\n\n")
                
                # Publication date
                if item.get('pubDate'):
                    f.write(f"**Published:** {item['pubDate']}\n\n")
                
                # Description
                if item.get('description'):
                    # Truncate long descriptions
                    desc = item['description']
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    f.write(f"{desc}\n\n")
                
                f.write("---\n\n")
        
        logger.info(f"Markdown report saved to: {filepath}")
        return filepath
    
    def generate_csv(self, items: List[Dict[str, Any]], 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a CSV report from feed items.
        
        Args:
            items: List of feed items
            metadata: Optional metadata (not used in CSV but kept for consistency)
            
        Returns:
            Path to the generated CSV file
        """
        logger.info(f"Generating CSV report for {len(items)} items")
        
        filepath = self._generate_filename('csv')
        
        # Define CSV columns
        fieldnames = ['title', 'link', 'feed_name', 'pubDate', 'description', 'guid']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            
            # Write header
            writer.writeheader()
            
            # Write items
            for item in items:
                # Prepare row with defaults for missing fields
                row = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'feed_name': item.get('feed_name', ''),
                    'pubDate': item.get('pubDate', ''),
                    'description': item.get('description', ''),
                    'guid': item.get('guid', ''),
                }
                writer.writerow(row)
        
        logger.info(f"CSV report saved to: {filepath}")
        return filepath
    
    def generate_all_formats(self, items: List[Dict[str, Any]], 
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate reports in all configured formats.
        
        Args:
            items: List of feed items
            metadata: Optional metadata to include in reports
            
        Returns:
            Dictionary mapping format name to filepath
        """
        logger.info(f"Generating reports in all formats for {len(items)} items")
        
        generated_files = {}
        
        for format_name in config.OUTPUT_CONFIG['formats']:
            try:
                if format_name.lower() == 'markdown':
                    filepath = self.generate_markdown(items, metadata)
                    generated_files['markdown'] = filepath
                elif format_name.lower() == 'csv':
                    filepath = self.generate_csv(items, metadata)
                    generated_files['csv'] = filepath
                else:
                    logger.warning(f"Unknown format: {format_name}")
            except Exception as e:
                logger.error(f"Error generating {format_name} report: {str(e)}")
        
        logger.info(f"Generated {len(generated_files)} reports")
        return generated_files
    
    def get_report_metadata(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate metadata for a report.
        
        Args:
            items: List of feed items
            
        Returns:
            Dictionary with report metadata
        """
        # Count unique feeds
        feeds = set(item.get('feed_name', 'Unknown') for item in items)
        
        metadata = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_items': len(items),
            'feeds_count': len(feeds),
            'feeds': list(feeds),
        }
        
        return metadata
