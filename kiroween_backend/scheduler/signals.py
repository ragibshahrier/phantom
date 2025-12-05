"""
Django signals for automatic Google Calendar synchronization.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Event

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Event)
def sync_event_to_google_calendar(sender, instance, created, **kwargs):
    """
    Automatically sync event to Google Calendar after save.
    """
    # Import here to avoid circular imports
    from integrations.sync_service import sync_service
    
    try:
        if created:
            # New event created
            sync_service.sync_event_create(instance)
        else:
            # Existing event updated
            sync_service.sync_event_update(instance)
    except Exception as e:
        # Log error but don't fail the save operation
        logger.error(f"Error in post_save signal for event {instance.id}: {str(e)}")


@receiver(post_delete, sender=Event)
def delete_event_from_google_calendar(sender, instance, **kwargs):
    """
    Automatically delete event from Google Calendar after deletion.
    """
    # Import here to avoid circular imports
    from integrations.sync_service import sync_service
    
    try:
        sync_service.sync_event_delete(instance)
    except Exception as e:
        # Log error but don't fail the delete operation
        logger.error(f"Error in post_delete signal for event {instance.id}: {str(e)}")
