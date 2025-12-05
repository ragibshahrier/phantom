"""
Service for synchronizing Phantom events with Google Calendar.
"""
import logging
from typing import Optional

from .google_calendar import GoogleCalendarService

logger = logging.getLogger(__name__)


class EventSyncService:
    """
    Service to handle event synchronization with Google Calendar.
    """
    
    def __init__(self):
        self.google_service = GoogleCalendarService()
    
    def sync_event_create(self, event) -> bool:
        """
        Sync a newly created event to Google Calendar.
        
        Args:
            event: Event model instance
            
        Returns:
            True if sync successful, False otherwise
        """
        user = event.user
        
        if not user.google_calendar_token:
            logger.debug(f"User {user.username} does not have Google Calendar connected, skipping sync")
            return False
        
        try:
            google_event_id = self.google_service.sync_event_to_google(event, user)
            
            if google_event_id:
                # Update event with Google Calendar ID
                event.google_calendar_id = google_event_id
                event.save(update_fields=['google_calendar_id'])
                logger.info(f"Successfully synced event {event.id} to Google Calendar")
                return True
            else:
                logger.warning(f"Failed to sync event {event.id} to Google Calendar")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing event {event.id} to Google Calendar: {str(e)}")
            return False
    
    def sync_event_update(self, event) -> bool:
        """
        Sync an updated event to Google Calendar.
        
        Args:
            event: Event model instance
            
        Returns:
            True if sync successful, False otherwise
        """
        user = event.user
        
        if not user.google_calendar_token:
            logger.debug(f"User {user.username} does not have Google Calendar connected, skipping sync")
            return False
        
        try:
            google_event_id = self.google_service.sync_event_to_google(event, user)
            
            if google_event_id:
                # Update event with Google Calendar ID if it changed
                if event.google_calendar_id != google_event_id:
                    event.google_calendar_id = google_event_id
                    event.save(update_fields=['google_calendar_id'])
                logger.info(f"Successfully updated event {event.id} in Google Calendar")
                return True
            else:
                logger.warning(f"Failed to update event {event.id} in Google Calendar")
                return False
                
        except Exception as e:
            logger.error(f"Error updating event {event.id} in Google Calendar: {str(e)}")
            return False
    
    def sync_event_delete(self, event) -> bool:
        """
        Delete an event from Google Calendar.
        
        Args:
            event: Event model instance
            
        Returns:
            True if deletion successful, False otherwise
        """
        user = event.user
        
        if not user.google_calendar_token:
            logger.debug(f"User {user.username} does not have Google Calendar connected, skipping sync")
            return False
        
        try:
            success = self.google_service.delete_event_from_google(event, user)
            
            if success:
                logger.info(f"Successfully deleted event {event.id} from Google Calendar")
            else:
                logger.warning(f"Failed to delete event {event.id} from Google Calendar")
            
            return success
                
        except Exception as e:
            logger.error(f"Error deleting event {event.id} from Google Calendar: {str(e)}")
            return False


# Singleton instance
sync_service = EventSyncService()
