"""
Business logic services for the Phantom scheduler application.
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Callable, Any
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
import logging

from .models import Event, SchedulingLog

logger = logging.getLogger(__name__)


def with_transaction_rollback(operation_name: str):
    """
    Decorator to wrap functions with atomic transaction and error logging.
    
    Ensures database operations are atomic (all-or-nothing) and logs
    transaction failures with detailed context.
    
    Args:
        operation_name: Name of the operation for logging purposes
        
    Returns:
        Decorator function
        
    Requirements: 10.4
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                with transaction.atomic():
                    result = func(*args, **kwargs)
                    logger.debug(f"Transaction completed successfully: {operation_name}")
                    return result
            except Exception as e:
                # Extract context from args if available
                context = {
                    'operation': operation_name,
                    'function': func.__name__,
                }
                
                # Try to extract user_id if first arg is self with user attribute
                if args and hasattr(args[0], 'user'):
                    context['user_id'] = args[0].user.id
                
                logger.error(
                    f"Transaction failed for operation '{operation_name}': {str(e)}",
                    exc_info=True,
                    extra=context
                )
                # Re-raise to allow caller to handle
                raise
        
        return wrapper
    return decorator


class SchedulingEngine:
    """
    Core scheduling logic for conflict resolution and optimization.
    
    Provides methods for:
    - Detecting overlapping events (conflicts)
    - Finding free time slots
    - Priority-based conflict resolution
    - Schedule optimization
    
    Requirements: 2.1, 2.2, 2.4, 2.5, 4.2, 4.3, 4.5
    """
    
    def __init__(self, user):
        """
        Initialize the scheduling engine for a specific user.
        
        Args:
            user: User instance for whom to manage scheduling
        """
        self.user = user
    
    def detect_conflicts(self, events: List[Event]) -> List[Tuple[Event, Event]]:
        """
        Detect all overlapping events in a list.
        
        Two events conflict if their time ranges overlap:
        - Event A: [start_a, end_a)
        - Event B: [start_b, end_b)
        - Conflict if: start_a < end_b AND start_b < end_a
        
        Args:
            events: List of Event objects to check for conflicts
            
        Returns:
            List of tuples containing pairs of conflicting events
            
        Requirements: 4.2
        """
        conflicts = []
        
        # Sort events by start time for efficient comparison
        sorted_events = sorted(events, key=lambda e: e.start_time)
        
        # Check each pair of events for overlap
        for i in range(len(sorted_events)):
            for j in range(i + 1, len(sorted_events)):
                event_a = sorted_events[i]
                event_b = sorted_events[j]
                
                # If event_b starts after event_a ends, no more conflicts possible
                # for event_a (since events are sorted by start time)
                if event_b.start_time >= event_a.end_time:
                    break
                
                # Check for overlap: start_a < end_b AND start_b < end_a
                if event_a.start_time < event_b.end_time and event_b.start_time < event_a.end_time:
                    conflicts.append((event_a, event_b))
        
        return conflicts
    
    def find_free_slots(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        duration_minutes: int,
        existing_events: Optional[List[Event]] = None
    ) -> List[Tuple[datetime, datetime]]:
        """
        Find available time slots in a date range.
        
        Args:
            start_date: Start of the search range
            end_date: End of the search range
            duration_minutes: Required duration for the slot in minutes
            existing_events: Optional list of events to consider (if None, queries from DB)
            
        Returns:
            List of tuples (slot_start, slot_end) representing free time slots
            
        Requirements: 4.2
        """
        # Get events in the date range if not provided
        if existing_events is None:
            existing_events = list(
                Event.objects.filter(
                    user=self.user,
                    start_time__lt=end_date,
                    end_time__gt=start_date
                ).order_by('start_time')
            )
        else:
            # Filter and sort provided events
            existing_events = [
                e for e in existing_events 
                if e.start_time < end_date and e.end_time > start_date
            ]
            existing_events = sorted(existing_events, key=lambda e: e.start_time)
        
        free_slots = []
        duration_delta = timedelta(minutes=duration_minutes)
        
        # Start searching from the beginning of the range
        current_time = start_date
        
        for event in existing_events:
            # Check if there's a gap before this event
            if current_time < event.start_time:
                gap_duration = event.start_time - current_time
                if gap_duration >= duration_delta:
                    free_slots.append((current_time, event.start_time))
            
            # Move current_time to the end of this event
            if event.end_time > current_time:
                current_time = event.end_time
        
        # Check if there's a gap after the last event
        if current_time < end_date:
            gap_duration = end_date - current_time
            if gap_duration >= duration_delta:
                free_slots.append((current_time, end_date))
        
        return free_slots
    
    def events_overlap(self, event1: Event, event2: Event) -> bool:
        """
        Check if two events overlap in time.
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            True if events overlap, False otherwise
        """
        return (event1.start_time < event2.end_time and 
                event2.start_time < event1.end_time)
    
    def get_event_duration(self, event: Event) -> timedelta:
        """
        Calculate the duration of an event.
        
        Args:
            event: Event to calculate duration for
            
        Returns:
            timedelta representing the event duration
        """
        return event.end_time - event.start_time
    
    def resolve_conflicts(self, events: List[Event]) -> List[Event]:
        """
        Resolve scheduling conflicts based on priority levels.
        
        Higher priority events are preserved, lower priority events are rescheduled
        to the next available free slot. Events maintain their original duration and category.
        
        Args:
            events: List of Event objects that may contain conflicts
            
        Returns:
            List of Event objects with conflicts resolved (some may have updated times)
            
        Requirements: 2.1, 2.4
        """
        if not events:
            return []
        
        # Sort events by priority (highest first), then by start time
        sorted_events = sorted(
            events, 
            key=lambda e: (-e.category.priority_level, e.start_time)
        )
        
        # Track which events are finalized (no conflicts)
        finalized_events = []
        events_to_reschedule = []
        
        for event in sorted_events:
            # Check if this event conflicts with any finalized event
            has_conflict = False
            for finalized in finalized_events:
                if self.events_overlap(event, finalized):
                    has_conflict = True
                    break
            
            if has_conflict:
                # This event needs to be rescheduled
                events_to_reschedule.append(event)
            else:
                # No conflict, finalize this event
                finalized_events.append(event)
        
        # Reschedule conflicting events to next available slots
        for event in events_to_reschedule:
            duration = self.get_event_duration(event)
            duration_minutes = int(duration.total_seconds() / 60)
            
            # Find the next available slot after the event's original start time
            search_start = event.start_time
            search_end = event.start_time + timedelta(days=30)  # Search up to 30 days ahead
            
            free_slots = self.find_free_slots(
                search_start,
                search_end,
                duration_minutes,
                existing_events=finalized_events
            )
            
            if free_slots:
                # Reschedule to the first available slot
                new_start, slot_end = free_slots[0]
                new_end = new_start + duration
                
                # Update event times (but preserve duration and category)
                event.start_time = new_start
                event.end_time = new_end
                
                # Add to finalized events
                finalized_events.append(event)
            else:
                # No available slot found, keep original time
                # (This shouldn't happen with a 30-day search window, but handle gracefully)
                finalized_events.append(event)
        
        return finalized_events
    
    def optimize_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        save_to_db: bool = True
    ) -> List[Event]:
        """
        Optimize all events in a date range by resolving conflicts.
        
        Uses Django atomic transactions for all-or-nothing updates.
        Logs all optimization operations.
        
        Args:
            start_date: Start of the optimization range
            end_date: End of the optimization range
            save_to_db: Whether to save changes to database (default True)
            
        Returns:
            List of optimized Event objects
            
        Requirements: 4.3, 4.5, 10.4
        """
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get all events in the date range
        events = list(
            Event.objects.filter(
                user=self.user,
                start_time__lt=end_date,
                end_time__gt=start_date
            ).select_related('category').order_by('start_time')
        )
        
        if not events:
            return []
        
        # Resolve conflicts
        optimized_events = self.resolve_conflicts(events)
        
        # Save changes atomically if requested
        if save_to_db:
            try:
                with transaction.atomic():
                    # Update all events in database
                    for event in optimized_events:
                        event.save()
                    
                    # Log the optimization operation
                    SchedulingLog.objects.create(
                        user=self.user,
                        action='OPTIMIZE',
                        event=None,  # Optimization affects multiple events
                        details={
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'num_events': len(optimized_events),
                            'event_ids': [e.id for e in optimized_events]
                        }
                    )
                    
                    logger.info(
                        f"Schedule optimization completed successfully for user {self.user.id}: "
                        f"{len(optimized_events)} events optimized"
                    )
            except Exception as e:
                logger.error(
                    f"Transaction failed during schedule optimization for user {self.user.id}: {str(e)}",
                    exc_info=True,
                    extra={
                        'user_id': self.user.id,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'num_events': len(optimized_events),
                        'operation': 'optimize_schedule'
                    }
                )
                # Re-raise the exception to be handled by the caller
                raise
        
        return optimized_events
    
    def create_exam_study_sessions(
        self,
        exam_event: Event,
        num_sessions: int = 3,
        session_duration_minutes: int = 120,
        save_to_db: bool = True
    ) -> List[Event]:
        """
        Automatically create study sessions before an exam event.
        
        Creates 2-3 study sessions in the days preceding the exam.
        Applies priority rules to clear conflicts.
        
        Args:
            exam_event: The exam event that triggers study session creation
            num_sessions: Number of study sessions to create (default 3)
            session_duration_minutes: Duration of each study session (default 120 minutes)
            save_to_db: Whether to save changes to database (default True)
            
        Returns:
            List of created study Event objects
            
        Requirements: 1.3, 2.2, 10.4
        """
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get or create Study category
        from .models import Category
        study_category, _ = Category.objects.get_or_create(
            name='Study',
            defaults={
                'priority_level': 4,
                'color': '#FFA500',
                'description': 'Study sessions'
            }
        )
        
        # Create study sessions in the days before the exam
        study_sessions = []
        session_duration = timedelta(minutes=session_duration_minutes)
        
        for i in range(num_sessions):
            # Schedule study sessions 1, 2, 3 days before the exam
            days_before = num_sessions - i
            study_start = exam_event.start_time - timedelta(days=days_before)
            
            # Adjust to a reasonable time (e.g., 2 PM)
            study_start = study_start.replace(hour=14, minute=0, second=0, microsecond=0)
            study_end = study_start + session_duration
            
            study_session = Event(
                user=self.user,
                title=f'Study for {exam_event.title}',
                description=f'Preparation session {i+1} for {exam_event.title}',
                category=study_category,
                start_time=study_start,
                end_time=study_end,
                is_flexible=True,
                is_completed=False
            )
            study_sessions.append(study_session)
        
        # Save study sessions and resolve conflicts if requested
        if save_to_db:
            try:
                with transaction.atomic():
                    # Save all study sessions first
                    for session in study_sessions:
                        session.save()
                    
                    # Get all events in the affected date range
                    earliest_study = min(s.start_time for s in study_sessions)
                    latest_study = max(s.end_time for s in study_sessions)
                    
                    all_events = list(
                        Event.objects.filter(
                            user=self.user,
                            start_time__lt=latest_study,
                            end_time__gt=earliest_study
                        ).select_related('category')
                    )
                    
                    # Resolve conflicts (study sessions have priority 4, which is high)
                    optimized_events = self.resolve_conflicts(all_events)
                    
                    # Save all optimized events
                    for event in optimized_events:
                        event.save()
                    
                    # Log the operation
                    SchedulingLog.objects.create(
                        user=self.user,
                        action='CREATE',
                        event=exam_event,
                        details={
                            'action_type': 'exam_study_sessions',
                            'exam_title': exam_event.title,
                            'num_sessions': num_sessions,
                            'study_session_ids': [s.id for s in study_sessions]
                        }
                    )
                    
                    logger.info(
                        f"Exam study sessions created successfully for user {self.user.id}: "
                        f"{num_sessions} sessions for exam '{exam_event.title}'"
                    )
            except Exception as e:
                logger.error(
                    f"Transaction failed during exam study session creation for user {self.user.id}: {str(e)}",
                    exc_info=True,
                    extra={
                        'user_id': self.user.id,
                        'exam_event_id': exam_event.id,
                        'exam_title': exam_event.title,
                        'num_sessions': num_sessions,
                        'operation': 'create_exam_study_sessions'
                    }
                )
                # Re-raise the exception to be handled by the caller
                raise
        
        return study_sessions
    
    def bulk_update_events(
        self,
        events: List[Event],
        operation_name: str = 'bulk_update'
    ) -> List[Event]:
        """
        Update multiple events atomically with transaction support.
        
        Ensures all updates succeed or all fail together. Logs transaction failures.
        
        Args:
            events: List of Event objects to update
            operation_name: Name of the operation for logging purposes
            
        Returns:
            List of updated Event objects
            
        Raises:
            Exception: If transaction fails, with detailed logging
            
        Requirements: 10.4
        """
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not events:
            return []
        
        try:
            with transaction.atomic():
                # Update all events
                updated_events = []
                for event in events:
                    event.save()
                    updated_events.append(event)
                
                # Log the bulk operation
                SchedulingLog.objects.create(
                    user=self.user,
                    action='BULK_UPDATE',
                    event=None,
                    details={
                        'operation': operation_name,
                        'num_events': len(updated_events),
                        'event_ids': [e.id for e in updated_events]
                    }
                )
                
                logger.info(
                    f"Bulk update completed successfully for user {self.user.id}: "
                    f"{len(updated_events)} events updated in operation '{operation_name}'"
                )
                
                return updated_events
                
        except Exception as e:
            logger.error(
                f"Transaction failed during bulk update for user {self.user.id}: {str(e)}",
                exc_info=True,
                extra={
                    'user_id': self.user.id,
                    'operation': operation_name,
                    'num_events': len(events),
                    'event_ids': [e.id for e in events if e.id]
                }
            )
            # Re-raise the exception to be handled by the caller
            raise
    
    def bulk_delete_events(
        self,
        event_ids: List[int],
        operation_name: str = 'bulk_delete'
    ) -> int:
        """
        Delete multiple events atomically with transaction support.
        
        Ensures all deletions succeed or all fail together. Logs transaction failures.
        
        Args:
            event_ids: List of event IDs to delete
            operation_name: Name of the operation for logging purposes
            
        Returns:
            Number of events deleted
            
        Raises:
            Exception: If transaction fails, with detailed logging
            
        Requirements: 10.4
        """
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        if not event_ids:
            return 0
        
        try:
            with transaction.atomic():
                # Get events to delete (for logging before deletion)
                events_to_delete = list(
                    Event.objects.filter(
                        user=self.user,
                        id__in=event_ids
                    ).values('id', 'title', 'start_time', 'end_time')
                )
                
                # Delete all events
                deleted_count, _ = Event.objects.filter(
                    user=self.user,
                    id__in=event_ids
                ).delete()
                
                # Log the bulk deletion
                SchedulingLog.objects.create(
                    user=self.user,
                    action='BULK_DELETE',
                    event=None,
                    details={
                        'operation': operation_name,
                        'num_events': deleted_count,
                        'deleted_events': events_to_delete
                    }
                )
                
                logger.info(
                    f"Bulk delete completed successfully for user {self.user.id}: "
                    f"{deleted_count} events deleted in operation '{operation_name}'"
                )
                
                return deleted_count
                
        except Exception as e:
            logger.error(
                f"Transaction failed during bulk delete for user {self.user.id}: {str(e)}",
                exc_info=True,
                extra={
                    'user_id': self.user.id,
                    'operation': operation_name,
                    'event_ids': event_ids
                }
            )
            # Re-raise the exception to be handled by the caller
            raise
