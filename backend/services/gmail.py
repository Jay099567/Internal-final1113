import os
import base64
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

logger = logging.getLogger(__name__)

class GmailService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        self.client_config = {
            "web": {
                "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
                "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:3000/oauth/callback')]
            }
        }
    
    def create_oauth_flow(self, redirect_uri: str = None) -> Flow:
        """Create OAuth flow for Gmail authentication"""
        if redirect_uri:
            self.client_config["web"]["redirect_uris"] = [redirect_uri]
        
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes
        )
        flow.redirect_uri = redirect_uri or self.client_config["web"]["redirect_uris"][0]
        return flow
    
    def get_authorization_url(self, redirect_uri: str = None) -> str:
        """Get OAuth authorization URL"""
        flow = self.create_oauth_flow(redirect_uri)
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url
    
    def exchange_code_for_tokens(self, code: str, redirect_uri: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        try:
            flow = self.create_oauth_flow(redirect_uri)
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": credentials.expiry,
                "scopes": credentials.scopes
            }
        except Exception as e:
            logger.error(f"Failed to exchange code for tokens: {str(e)}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=self.client_config["web"]["token_uri"],
                client_id=self.client_config["web"]["client_id"],
                client_secret=self.client_config["web"]["client_secret"]
            )
            
            credentials.refresh(Request())
            
            return {
                "access_token": credentials.token,
                "token_expiry": credentials.expiry,
                "scopes": credentials.scopes
            }
        except Exception as e:
            logger.error(f"Failed to refresh access token: {str(e)}")
            raise
    
    def build_service(self, access_token: str):
        """Build Gmail service with access token"""
        credentials = Credentials(token=access_token)
        return build('gmail', 'v1', credentials=credentials)
    
    def generate_email_alias(self, base_email: str, company: str, job_board: str = "") -> str:
        """Generate email alias using Gmail + trick"""
        # Extract username from email
        username = base_email.split('@')[0]
        domain = base_email.split('@')[1]
        
        # Create alias suffix
        company_clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower())[:10]
        job_board_clean = re.sub(r'[^a-zA-Z0-9]', '', job_board.lower())[:5]
        
        alias_suffix = f"{company_clean}{job_board_clean}".lower()[:15]
        
        alias_email = f"{username}+{alias_suffix}@{domain}"
        return alias_email
    
    async def send_email(self, service, sender_email: str, recipient_email: str, 
                        subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        """Send email using Gmail API"""
        try:
            message = MIMEMultipart('alternative')
            message['To'] = recipient_email
            message['From'] = sender_email
            message['Subject'] = subject
            
            # Add custom headers for stealth
            message['Reply-To'] = sender_email
            message['Return-Path'] = sender_email
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": result['id'],
                "thread_id": result.get('threadId'),
                "sent_at": datetime.utcnow()
            }
        except HttpError as e:
            logger.error(f"Gmail API error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sent_at": datetime.utcnow()
            }
    
    async def list_messages(self, service, query: str = "", max_results: int = 100) -> List[Dict[str, Any]]:
        """List Gmail messages based on query"""
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except HttpError as e:
            logger.error(f"Gmail API error listing messages: {str(e)}")
            return []
    
    async def get_message(self, service, message_id: str) -> Dict[str, Any]:
        """Get specific Gmail message"""
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Parse message
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Extract basic info
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            body = self._extract_message_body(payload)
            
            return {
                "id": message['id'],
                "thread_id": message['threadId'],
                "subject": subject,
                "sender": sender,
                "recipient": recipient,
                "date": date,
                "body": body,
                "snippet": message.get('snippet', ''),
                "raw_payload": payload
            }
        except HttpError as e:
            logger.error(f"Gmail API error getting message: {str(e)}")
            return {}
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract message body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    async def search_emails(self, service, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search emails and return full message details"""
        try:
            # List messages matching query
            message_list = await self.list_messages(service, query, max_results)
            
            # Get full details for each message
            messages = []
            for msg in message_list:
                message_details = await self.get_message(service, msg['id'])
                if message_details:
                    messages.append(message_details)
            
            return messages
        except Exception as e:
            logger.error(f"Error searching emails: {str(e)}")
            return []
    
    async def monitor_inbox(self, service, last_check: datetime = None) -> List[Dict[str, Any]]:
        """Monitor inbox for new messages since last check"""
        try:
            if last_check:
                # Convert to Gmail search format
                date_str = last_check.strftime('%Y/%m/%d')
                query = f"after:{date_str}"
            else:
                query = "is:unread"
            
            new_messages = await self.search_emails(service, query)
            return new_messages
        except Exception as e:
            logger.error(f"Error monitoring inbox: {str(e)}")
            return []
    
    async def get_user_profile(self, service) -> Dict[str, Any]:
        """Get Gmail user profile"""
        try:
            profile = service.users().getProfile(userId='me').execute()
            return {
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal', 0),
                "threads_total": profile.get('threadsTotal', 0),
                "history_id": profile.get('historyId')
            }
        except HttpError as e:
            logger.error(f"Gmail API error getting profile: {str(e)}")
            return {}
    
    def create_tracking_pixel(self, application_id: str) -> str:
        """Create invisible tracking pixel for email tracking"""
        tracking_url = f"https://tracking.jobhunterx.com/pixel/{application_id}.png"
        return f'<img src="{tracking_url}" width="1" height="1" style="display:none;">'
    
    def add_utm_parameters(self, url: str, source: str, medium: str, campaign: str) -> str:
        """Add UTM parameters to URLs for tracking"""
        separator = "&" if "?" in url else "?"
        utm_params = f"utm_source={source}&utm_medium={medium}&utm_campaign={campaign}"
        return f"{url}{separator}{utm_params}"

# Global instance
gmail_service = GmailService()