"""
Google Calendar API integration for Phantom Scheduler.
Handles OAuth2 authentication and event synchronization.
"""
import logging
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Service for managing Google Calendar API authentication and operations.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL for user to grant access.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL string
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth2 callback
            
        Returns:
            Dictionary containing token information
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
    
    def get_credentials_from_token_data(self, token_data: Dict[str, Any]) -> Credentials:
        """
        Create Credentials object from stored token data.
        
        Args:
            token_data: Dictionary containing token information
            
        Returns:
            Google Credentials object
        """
        expiry = None
        if token_data.get('expiry'):
            expiry = datetime.fromisoformat(token_data['expiry'])
        
        credentials = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes'),
            expiry=expiry
        )
        
        return credentials
    
    def refresh_credentials(self, credentials: Credentials) -> Credentials:
        """
        Refresh expired credentials automatically.
        
        Args:
            credentials: Google Credentials object
            
        Returns:
            Refreshed Credentials object
        """
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            logger.info("Successfully refreshed Google Calendar credentials")
        
        return credentials
    
    def get_calendar_service(self, user):
        """
        Get authenticated Google Calendar service for a user.
        
        Args:
            user: User model instance with google_calendar_token
            
        Returns:
            Google Calendar API service object
            
        Raises:
            ValueError: If user doesn't have Google Calendar connected
        """
        if not user.google_calendar_token:
            raise ValueError("User does not have Google Calendar connected")
        
        token_data = json.loads(user.google_calendar_token)
        credentials = self.get_credentials_from_token_data(token_data)
        
        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            credentials = self.refresh_credentials(credentials)
            
            # Update stored token
            updated_token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }
            user.google_calendar_token = json.dumps(updated_token_data)
            user.save(update_fields=['google_calendar_token'])
            logger.info(f"Updated refreshed token for user {user.username}")
        
        service = build('calendar', 'v3', credentials=credentials)
        return service
    
    def sync_event_to_google(self, event, user, max_retries=3) -> Optional[str]:
        """
        Synchronize a Phantom event to Google Calendar with retry logic.
        
        Args:
            event: Event model instance
            user: User model instance
            max_retries: Maximum number of retry attempts
            
        Returns:
            Google Calendar event ID or None if sync fails
        """
        if not user.google_calendar_token:
            logger.warning(f"User {user.username} does not have Google Calendar connected")
            return None
        
        try:
            service = self.get_calendar_service(user)
            
            # Convert Phantom event to Google Calendar event format
            google_event = {
                'summary': event.title,
                'description': event.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': user.timezone,
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': user.timezone,
                },
                'colorId': self._get_color_id_for_category(event.category),
            }
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    if event.google_calendar_id:
                        # Update existing event
                        result = service.events().update(
                            calendarId='primary',
                            eventId=event.google_calendar_id,
                            body=google_event
                        ).execute()
                        logger.info(f"Updated Google Calendar event {result['id']} for event {event.id}")
                    else:
                        # Create new event
                        result = service.events().insert(
                            calendarId='primary',
                            body=google_event
                        ).execute()
                        logger.info(f"Created Google Calendar event {result['id']} for event {event.id}")
                    
                    return result['id']
                    
                except HttpError as e:
                    if e.resp.status in [429, 500, 503]:  # Rate limit or server errors
                        if attempt < max_retries - 1:
                            # Exponential backoff: 1s, 2s, 4s
                            wait_time = 2 ** attempt
                            logger.warning(
                                f"Google Calendar API error (attempt {attempt + 1}/{max_retries}): "
                                f"{e.resp.status}. Retrying in {wait_time}s..."
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(f"Failed to sync event after {max_retries} attempts: {str(e)}")
                            raise
                    else:
                        # Non-retryable error
                        logger.error(f"Non-retryable Google Calendar API error: {str(e)}")
                        raise
                        
        except Exception as e:
            logger.error(f"Error syncing event {event.id} to Google Calendar: {str(e)}")
            return None
    
    def delete_event_from_google(self, event, user, max_retries=3) -> bool:
        """
        Delete an event from Google Calendar with retry logic.
        
        Args:
            event: Event model instance
            user: User model instance
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not event.google_calendar_id:
            logger.info(f"Event {event.id} has no Google Calendar ID, skipping deletion")
            return True
        
        if not user.google_calendar_token:
            logger.warning(f"User {user.username} does not have Google Calendar connected")
            return False
        
        try:
            service = self.get_calendar_service(user)
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    service.events().delete(
                        calendarId='primary',
                        eventId=event.google_calendar_id
                    ).execute()
                    logger.info(f"Deleted Google Calendar event {event.google_calendar_id} for event {event.id}")
                    return True
                    
                except HttpError as e:
                    if e.resp.status == 404:
                        # Event already deleted or doesn't exist
                        logger.info(f"Google Calendar event {event.google_calendar_id} not found (already deleted)")
                        return True
                    elif e.resp.status in [429, 500, 503]:  # Rate limit or server errors
                        if attempt < max_retries - 1:
                            # Exponential backoff: 1s, 2s, 4s
                            wait_time = 2 ** attempt
                            logger.warning(
                                f"Google Calendar API error (attempt {attempt + 1}/{max_retries}): "
                                f"{e.resp.status}. Retrying in {wait_time}s..."
                            )
                            time.sleep(wait_time)
                        else:
                            logger.error(f"Failed to delete event after {max_retries} attempts: {str(e)}")
                            raise
                    else:
                        # Non-retryable error
                        logger.error(f"Non-retryable Google Calendar API error: {str(e)}")
                        raise
                        
        except Exception as e:
            logger.error(f"Error deleting event {event.id} from Google Calendar: {str(e)}")
            return False
    
    def _get_color_id_for_category(self, category) -> str:
        """
        Map category priority to Google Calendar color ID.
        
        Args:
            category: Category model instance
            
        Returns:
            Google Calendar color ID (1-11)
        """
        # Map priority levels to color IDs
        priority_to_color = {
            5: '11',  # Exam - Red
            4: '9',   # Study - Blue
            3: '10',  # Gym - Green
            2: '5',   # Social - Yellow
            1: '8',   # Gaming - Gray
        }
        return priority_to_color.get(category.priority_level, '1')  # Default to lavender
