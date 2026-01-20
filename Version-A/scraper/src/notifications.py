"""
Job Crawler - Notifications

Handles email notifications using Gmail API or SMTP.
"""

import base64
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Protocol

from jinja2 import Environment, FileSystemLoader, select_autoescape
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from .models import Job
from .config import get_config


class EmailBackend(Protocol):
    """Protocol for email backends."""
    def send_digest(self, to_email: str, jobs: list[Job]) -> None:
        ...


class ConsoleBackend:
    """Backend that prints email to console (for dev/testing)."""
    
    def send_digest(self, to_email: str, jobs: list[Job]) -> None:
        print(f"\n{'='*60}")
        print(f"  [MOCK EMAIL] To: {to_email}")
        print(f"  Subject: Job Crawler Digest - {len(jobs)} new jobs")
        print(f"{'='*60}")
        print(f"  (Email content would go here - {len(jobs)} jobs found)")
        print(f"{'='*60}\n")


class GmailAPIBackend:
    """Backend that sends emails via Gmail API."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, token_path: str = 'token.json', credentials_path: str = 'credentials.json'):
        self.creds = None
        self.token_path = token_path
        self.credentials_path = credentials_path
        self._service: Optional[Resource] = None
        
        # Load template
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _get_service(self) -> Resource:
        """Authenticate and return Gmail service."""
        if self._service:
            return self._service
            
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Gmail credentials not found at {self.credentials_path}")
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        self._service = build('gmail', 'v1', credentials=self.creds)
        return self._service

    def send_digest(self, to_email: str, jobs: list[Job]) -> None:
        """Send daily digest email."""
        if not jobs:
            return

        service = self._get_service()
        
        # Prepare data
        entry_level = [j for j in jobs if j.is_entry_level]
        other = [j for j in jobs if not j.is_entry_level]
        
        template = self.jinja_env.get_template('digest.html')
        html_content = template.render(
            date=datetime.now().strftime('%B %d, %Y'),
            total_count=len(jobs),
            entry_level_count=len(entry_level),
            entry_level_jobs=entry_level,
            other_jobs=other,
            dashboard_url=os.getenv("DASHBOARD_URL", "http://localhost:3000")
        )

        # Create message
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = f"Job Crawler Digest: {len(jobs)} new jobs found"
        message.attach(MIMEText(html_content, 'html'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        try:
            service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")


def get_notification_service() -> EmailBackend:
    """Factory to get the configured notification backend."""
    # Check if we have Gmail credentials
    if os.path.exists('credentials.json') or os.path.exists('token.json'):
        return GmailAPIBackend()
    
    # Fallback to console for development
    print("WARNING: No Gmail credentials found. Using Console backend.")
    return ConsoleBackend()
