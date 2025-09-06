"""
Email Notification System for Data Processing Completion

This module provides functionality to send email notifications when data processing tasks complete.
It supports SMTP configuration and maintains a list of recipients for different types of notifications.
"""

import smtplib
import json
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logger

logger = setup_logger(__name__, 'email_notifier.log')


class EmailNotifier:
    """Email notification system for data processing completion alerts."""
    
    def __init__(self, config_path: str = "email_config.json"):
        """
        Initialize the email notifier with configuration.
        
        Args:
            config_path: Path to the email configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load email configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"✅ Email configuration loaded from {self.config_path}")
                return config
            else:
                logger.warning(f"⚠️ Email config file not found: {self.config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Error loading email config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default email configuration."""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password",
            "use_tls": True,
            "recipients": {
                "data_processing": [
                    "data-team@ymca.org",
                    "manager@ymca.org"
                ],
                "reports": [
                    "reports@ymca.org",
                    "analytics@ymca.org"
                ],
                "errors": [
                    "it-support@ymca.org",
                    "admin@ymca.org"
                ]
            },
            "enabled": False,
            "templates": {
                "data_processing_complete": {
                    "subject": "YMCA Data Processing Complete - {date}",
                    "body": """
Data processing has completed successfully.

Processing Details:
- Date: {date}
- Processing Type: {processing_type}
- Files Processed: {files_processed}
- Total Records: {total_records}
- Output Files: {output_files}

Summary:
{summary}

The processed data is ready for review and reporting.

Best regards,
YMCA Data Processing System
"""
                },
                "processing_error": {
                    "subject": "YMCA Data Processing Error - {date}",
                    "body": """
An error occurred during data processing.

Error Details:
- Date: {date}
- Processing Type: {processing_type}
- Error Message: {error_message}
- Files Being Processed: {files_processed}

Please review the logs and take appropriate action.

Best regards,
YMCA Data Processing System
"""
                }
            }
        }
    
    def create_default_config(self) -> str:
        """Create a default configuration file."""
        config = self._get_default_config()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Default email configuration created: {self.config_path}")
            logger.info("⚠️ Please update the configuration with your SMTP settings")
            return self.config_path
        except Exception as e:
            logger.error(f"❌ Error creating default config: {e}")
            raise
    
    def send_processing_complete_notification(
        self, 
        processing_type: str,
        files_processed: List[str],
        output_files: List[str],
        total_records: int = 0,
        summary: str = "",
        recipient_group: str = "data_processing",
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send notification when data processing completes successfully.
        
        Args:
            processing_type: Type of processing completed (e.g., "Data Preparation", "Statistics Generation")
            files_processed: List of input files that were processed
            output_files: List of output files that were generated
            total_records: Number of records processed
            summary: Additional summary information
            recipient_group: Group of recipients to notify
            attachments: Optional list of file paths to attach
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        if not self.config.get("enabled", False):
            logger.info("📧 Email notifications are disabled")
            return False
            
        try:
            template = self.config["templates"]["data_processing_complete"]
            
            # Format the email content
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = template["subject"].format(date=current_date)
            
            body = template["body"].format(
                date=current_date,
                processing_type=processing_type,
                files_processed="\n".join([f"- {f}" for f in files_processed]),
                total_records=total_records,
                output_files="\n".join([f"- {f}" for f in output_files]),
                summary=summary or "Processing completed successfully."
            )
            
            recipients = self.config["recipients"].get(recipient_group, [])
            
            return self._send_email(subject, body, recipients, attachments)
            
        except Exception as e:
            logger.error(f"❌ Error sending processing complete notification: {e}")
            return False
    
    def send_processing_error_notification(
        self,
        processing_type: str,
        error_message: str,
        files_processed: List[str],
        recipient_group: str = "errors"
    ) -> bool:
        """
        Send notification when data processing encounters an error.
        
        Args:
            processing_type: Type of processing that failed
            error_message: Description of the error
            files_processed: List of files being processed when error occurred
            recipient_group: Group of recipients to notify
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        if not self.config.get("enabled", False):
            logger.info("📧 Email notifications are disabled")
            return False
            
        try:
            template = self.config["templates"]["processing_error"]
            
            # Format the email content
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = template["subject"].format(date=current_date)
            
            body = template["body"].format(
                date=current_date,
                processing_type=processing_type,
                error_message=error_message,
                files_processed="\n".join([f"- {f}" for f in files_processed])
            )
            
            recipients = self.config["recipients"].get(recipient_group, [])
            
            return self._send_email(subject, body, recipients)
            
        except Exception as e:
            logger.error(f"❌ Error sending processing error notification: {e}")
            return False
    
    def _send_email(
        self, 
        subject: str, 
        body: str, 
        recipients: List[str], 
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email using SMTP configuration.
        
        Args:
            subject: Email subject
            body: Email body content
            recipients: List of recipient email addresses
            attachments: Optional list of file paths to attach
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not recipients:
            logger.warning("⚠️ No recipients specified for email notification")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["sender_email"]
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._attach_file(msg, file_path)
                    else:
                        logger.warning(f"⚠️ Attachment file not found: {file_path}")
            
            # Create SMTP session
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            
            if self.config.get("use_tls", True):
                server.starttls()
            
            server.login(self.config["sender_email"], self.config["sender_password"])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.config["sender_email"], recipients, text)
            server.quit()
            
            logger.info(f"✅ Email notification sent successfully to {len(recipients)} recipients")
            logger.info(f"📧 Subject: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")
            return False
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message."""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            
            msg.attach(part)
            logger.info(f"📎 Attached file: {os.path.basename(file_path)}")
            
        except Exception as e:
            logger.error(f"❌ Error attaching file {file_path}: {e}")
    
    def test_connection(self) -> bool:
        """Test the email connection and configuration."""
        if not self.config.get("enabled", False):
            logger.info("📧 Email notifications are disabled")
            return False
            
        try:
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            
            if self.config.get("use_tls", True):
                server.starttls()
            
            server.login(self.config["sender_email"], self.config["sender_password"])
            server.quit()
            
            logger.info("✅ Email connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Email connection test failed: {e}")
            return False
    
    def get_recipient_groups(self) -> List[str]:
        """Get list of available recipient groups."""
        return list(self.config["recipients"].keys())
    
    def add_recipient(self, group: str, email: str) -> bool:
        """Add a recipient to a specific group."""
        try:
            if group not in self.config["recipients"]:
                self.config["recipients"][group] = []
            
            if email not in self.config["recipients"][group]:
                self.config["recipients"][group].append(email)
                
                # Save updated config
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
                
                logger.info(f"✅ Added recipient {email} to group {group}")
                return True
            else:
                logger.info(f"ℹ️ Recipient {email} already exists in group {group}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding recipient: {e}")
            return False


def create_default_email_config(config_path: str = "email_config.json") -> str:
    """
    Create a default email configuration file.
    
    Args:
        config_path: Path where to create the configuration file
        
    Returns:
        str: Path to the created configuration file
    """
    notifier = EmailNotifier(config_path)
    return notifier.create_default_config()


# Convenience function for quick notifications
def notify_processing_complete(
    processing_type: str,
    files_processed: List[str],
    output_files: List[str],
    total_records: int = 0,
    summary: str = "",
    config_path: str = "email_config.json"
) -> bool:
    """
    Quick function to send processing complete notification.
    
    Args:
        processing_type: Type of processing completed
        files_processed: List of input files processed
        output_files: List of output files generated
        total_records: Number of records processed
        summary: Additional summary information
        config_path: Path to email configuration file
        
    Returns:
        bool: True if notification was sent successfully
    """
    notifier = EmailNotifier(config_path)
    return notifier.send_processing_complete_notification(
        processing_type=processing_type,
        files_processed=files_processed,
        output_files=output_files,
        total_records=total_records,
        summary=summary
    )


def notify_processing_error(
    processing_type: str,
    error_message: str,
    files_processed: List[str],
    config_path: str = "email_config.json"
) -> bool:
    """
    Quick function to send processing error notification.
    
    Args:
        processing_type: Type of processing that failed
        error_message: Description of the error
        files_processed: List of files being processed
        config_path: Path to email configuration file
        
    Returns:
        bool: True if notification was sent successfully
    """
    notifier = EmailNotifier(config_path)
    return notifier.send_processing_error_notification(
        processing_type=processing_type,
        error_message=error_message,
        files_processed=files_processed
    )


if __name__ == "__main__":
    # Create default configuration if running directly
    config_file = create_default_email_config()
    print(f"Default email configuration created: {config_file}")
    print("Please update the configuration with your SMTP settings before using.")