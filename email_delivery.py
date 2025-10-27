"""
Email Delivery Module

This module handles sending email notifications with reports
attached in multiple formats.
"""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional

import config


logger = logging.getLogger(__name__)


class EmailDelivery:
    """Handler for email delivery with attachments."""
    
    def __init__(self):
        """Initialize the email delivery handler."""
        self.config = config.EMAIL_CONFIG
        self.template_config = config.EMAIL_TEMPLATE_CONFIG
        logger.info("Email Delivery handler initialized")
    
    def _validate_config(self) -> bool:
        """
        Validate email configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_fields = ['host', 'port', 'username', 'password', 'to_email']
        
        for field in required_fields:
            if not self.config.get(field):
                logger.error(f"Missing required email configuration: {field}")
                return False
        
        return True
    
    def _load_template(self, template_path: str) -> Optional[str]:
        """
        Load an email template from file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Template content as string, or None if file not found
        """
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Template file not found: {template_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {str(e)}")
            return None
    
    def _format_items_html(self, items: List[Dict[str, Any]], max_items: int) -> str:
        """
        Format items as HTML for email body.
        
        Args:
            items: List of feed items
            max_items: Maximum number of items to include
            
        Returns:
            HTML formatted string of items
        """
        html_parts = []
        
        for item in items[:max_items]:
            title = item.get('title', 'Untitled')
            link = item.get('link', '#')
            feed_name = item.get('feed_name', 'Unknown Source')
            pub_date = item.get('pubDate', '')
            description = item.get('description', '')
            
            # Truncate description
            if len(description) > 200:
                description = description[:197] + "..."
            
            html_parts.append(f'''
        <div class="item">
            <h3><a href="{link}">{title}</a></h3>
            <div class="meta">
                <strong>Source:</strong> {feed_name}
                {f'| <strong>Published:</strong> {pub_date}' if pub_date else ''}
            </div>
            {f'<div class="description">{description}</div>' if description else ''}
        </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def _format_items_text(self, items: List[Dict[str, Any]], max_items: int) -> str:
        """
        Format items as plain text for email body.
        
        Args:
            items: List of feed items
            max_items: Maximum number of items to include
            
        Returns:
            Plain text formatted string of items
        """
        text_parts = []
        
        for i, item in enumerate(items[:max_items], 1):
            title = item.get('title', 'Untitled')
            link = item.get('link', '')
            feed_name = item.get('feed_name', 'Unknown Source')
            pub_date = item.get('pubDate', '')
            description = item.get('description', '')
            
            # Truncate description
            if len(description) > 200:
                description = description[:197] + "..."
            
            text_parts.append(f"{i}. {title}")
            text_parts.append(f"   Source: {feed_name}")
            if link:
                text_parts.append(f"   Link: {link}")
            if pub_date:
                text_parts.append(f"   Published: {pub_date}")
            if description:
                text_parts.append(f"   {description}")
            text_parts.append("")
        
        return '\n'.join(text_parts)
    
    def _create_email_body(self, items: List[Dict[str, Any]], 
                          metadata: Dict[str, Any]) -> tuple[str, str]:
        """
        Create HTML and plain text email body.
        
        Args:
            items: List of feed items
            metadata: Report metadata
            
        Returns:
            Tuple of (html_body, text_body)
        """
        max_items = self.template_config['max_items_in_summary']
        report_date = metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d'))
        total_items = metadata.get('total_items', len(items))
        feeds_count = metadata.get('feeds_count', 0)
        
        # Prepare common template variables
        template_vars = {
            'report_date': report_date,
            'total_items': total_items,
            'feeds_count': feeds_count,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'separator': '=' * 70,
        }
        
        # Add "more items" message if needed
        if total_items > max_items:
            remaining = total_items - max_items
            template_vars['more_items_message'] = (
                f"<p><em>... and {remaining} more items. "
                f"See attached files for complete report.</em></p>"
            )
            text_more_message = (
                f"\n... and {remaining} more items. "
                f"See attached files for complete report.\n"
            )
        else:
            template_vars['more_items_message'] = ""
            text_more_message = ""
        
        # Generate HTML body
        html_template = self._load_template(self.template_config['html_template'])
        if html_template:
            template_vars['items_html'] = self._format_items_html(items, max_items)
            html_body = html_template.format(**template_vars)
        else:
            # Fallback HTML
            html_body = f"""
            <html>
            <body>
                <h1>News Aggregator Report</h1>
                <p>Report Date: {report_date}</p>
                <p>Total Items: {total_items}</p>
                <p>See attached files for the complete report.</p>
            </body>
            </html>
            """
        
        # Generate plain text body
        text_template = self._load_template(self.template_config['text_template'])
        if text_template:
            template_vars['items_text'] = self._format_items_text(items, max_items)
            template_vars['more_items_message'] = text_more_message
            text_body = text_template.format(**template_vars)
        else:
            # Fallback text
            text_body = f"""
NEWS AGGREGATOR REPORT

Report Date: {report_date}
Total Items: {total_items}
Feeds Processed: {feeds_count}

See attached files for the complete report.

Generated on {template_vars['generation_time']}
            """
        
        return html_body, text_body
    
    def send_email(self, items: List[Dict[str, Any]], 
                   metadata: Dict[str, Any],
                   attachments: List[str]) -> bool:
        """
        Send email with report attachments.
        
        Args:
            items: List of feed items
            metadata: Report metadata
            attachments: List of file paths to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.config.get('enabled'):
            logger.info("Email delivery is disabled in configuration")
            return False
        
        if not self._validate_config():
            logger.error("Email configuration validation failed")
            return False
        
        try:
            logger.info("Preparing email message")
            
            # Extract non-sensitive config values for logging
            smtp_host = self.config['host']
            smtp_port = self.config['port']
            username = self.config['username']
            password = self.config['password']
            to_email = self.config['to_email']
            from_email = self.config.get('from_email', username)
            use_ssl = self.config.get('use_ssl')
            use_tls = self.config.get('use_tls')
            
            # Create message
            msg = MIMEMultipart('alternative')
            
            # Set email headers
            subject_date = datetime.now().strftime('%Y-%m-%d')
            msg['Subject'] = self.template_config['subject_template'].format(
                date=subject_date
            )
            msg['From'] = from_email
            msg['To'] = to_email
            
            # Create email body
            html_body, text_body = self._create_email_body(items, metadata)
            
            # Attach both plain text and HTML versions
            part_text = MIMEText(text_body, 'plain')
            part_html = MIMEText(html_body, 'html')
            
            msg.attach(part_text)
            msg.attach(part_html)
            
            # Attach files
            for filepath in attachments:
                if os.path.exists(filepath):
                    logger.info(f"Attaching file: {filepath}")
                    
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    
                    filename = os.path.basename(filepath)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    
                    msg.attach(part)
                else:
                    logger.warning(f"Attachment file not found: {filepath}")
            
            # Send email
            # Note: Detailed connection info not logged to avoid potential security issues
            logger.info("Connecting to SMTP server")
            
            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port)
            
            if use_tls and not use_ssl:
                server.starttls()
            
            logger.info("Authenticating with SMTP server")
            # Perform login - credentials are not logged for security
            server.login(username, password)
            
            logger.info("Sending email message")
            server.send_message(msg)
            server.quit()
            
            logger.info("Email sent successfully")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
