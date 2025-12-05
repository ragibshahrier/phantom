"""
Tests for transaction rollback functionality.

Verifies that multi-step database operations use atomic transactions
and properly rollback on failures.

Requirements: 10.4
"""
import pytest
from django.test import TestCase
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, Mock

from scheduler.models import User, Event, Category, SchedulingLog
from scheduler.services import SchedulingEngine


class TransactionRollbackTestCase(TestCase):
    """
    Test cases for transaction rollback on database failures.
    
    Requirements: 10.4
    """
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User',
            timezone='UTC'
        )
        
        self.category = Category.objects.create(
            name='Test',
            priority_level=3,
            color='#FF0000',
            description='Test category'
        )
        
        self.exam_category = Category.objects.create(
            name='Exam',
            priority_level=5,
            color='#FF0000',
            description='Exam category'
        )
    
    def test_optimize_schedule_rollback_on_save_failure(self):
        """
        Test that optimize_schedule rolls back all changes if any event save fails.
        
        Requirements: 10.4
        """
        engine = SchedulingEngine(self.user)
        
        # Create some events
        now = timezone.now()
        event1 = Event.objects.create(
            user=self.user,
            title='Event 1',
            category=self.category,
            start_time=now,
            end_time=now + timedelta(hours=1)
        )
        event2 = Event.objects.create(
            user=self.user,
            title='Event 2',
            category=self.category,
            start_time=now + timedelta(hours=0.5),
            end_time=now + timedelta(hours=1.5)
        )
        
        # Count initial events and logs
        initial_event_count = Event.objects.count()
        initial_log_count = SchedulingLog.objects.count()
        
        # Mock Event.save to raise an exception on the second call
        original_save = Event.save
        call_count = [0]
        
        def mock_save(self, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise IntegrityError("Simulated database error")
            return original_save(self, *args, **kwargs)
        
        with patch.object(Event, 'save', mock_save):
            with self.assertRaises(IntegrityError):
                engine.optimize_schedule(
                    start_date=now - timedelta(hours=1),
                    end_date=now + timedelta(hours=2),
                    save_to_db=True
                )
        
        # Verify rollback: event count should be unchanged
        self.assertEqual(Event.objects.count(), initial_event_count)
        
        # Verify no log was created (transaction rolled back)
        self.assertEqual(SchedulingLog.objects.count(), initial_log_count)
    
    def test_create_exam_study_sessions_rollback_on_failure(self):
        """
        Test that create_exam_study_sessions rolls back all changes on failure.
        
        Requirements: 10.4
        """
        engine = SchedulingEngine(self.user)
        
        # Create an exam event
        exam_time = timezone.now() + timedelta(days=5)
        exam_event = Event.objects.create(
            user=self.user,
            title='Final Exam',
            category=self.exam_category,
            start_time=exam_time,
            end_time=exam_time + timedelta(hours=2)
        )
        
        initial_event_count = Event.objects.count()
        initial_log_count = SchedulingLog.objects.count()
        
        # Mock Event.save to fail on the 4th call (after 3 study sessions are created)
        original_save = Event.save
        call_count = [0]
        
        def mock_save(self, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 4:
                raise IntegrityError("Simulated database error during optimization")
            return original_save(self, *args, **kwargs)
        
        with patch.object(Event, 'save', mock_save):
            with self.assertRaises(IntegrityError):
                engine.create_exam_study_sessions(
                    exam_event=exam_event,
                    num_sessions=3,
                    save_to_db=True
                )
        
        # Verify rollback: only the original exam event should exist
        self.assertEqual(Event.objects.count(), initial_event_count)
        
        # Verify no log was created
        self.assertEqual(SchedulingLog.objects.count(), initial_log_count)
    
    def test_bulk_update_events_rollback_on_failure(self):
        """
        Test that bulk_update_events rolls back all changes on failure.
        
        Requirements: 10.4
        """
        engine = SchedulingEngine(self.user)
        
        # Create multiple events
        now = timezone.now()
        events = []
        for i in range(3):
            event = Event.objects.create(
                user=self.user,
                title=f'Event {i}',
                category=self.category,
                start_time=now + timedelta(hours=i),
                end_time=now + timedelta(hours=i+1)
            )
            events.append(event)
        
        # Modify events
        for i, event in enumerate(events):
            event.title = f'Updated Event {i}'
        
        initial_log_count = SchedulingLog.objects.count()
        
        # Mock Event.save to fail on the 3rd call
        original_save = Event.save
        call_count = [0]
        
        def mock_save(self, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 3:
                raise IntegrityError("Simulated database error")
            return original_save(self, *args, **kwargs)
        
        with patch.object(Event, 'save', mock_save):
            with self.assertRaises(IntegrityError):
                engine.bulk_update_events(events, operation_name='test_bulk_update')
        
        # Verify rollback: events should have original titles
        for i, event in enumerate(events):
            event.refresh_from_db()
            self.assertEqual(event.title, f'Event {i}')
        
        # Verify no log was created
        self.assertEqual(SchedulingLog.objects.count(), initial_log_count)
    
    def test_bulk_delete_events_rollback_on_failure(self):
        """
        Test that bulk_delete_events rolls back all changes on failure.
        
        Requirements: 10.4
        """
        engine = SchedulingEngine(self.user)
        
        # Create multiple events
        now = timezone.now()
        event_ids = []
        for i in range(3):
            event = Event.objects.create(
                user=self.user,
                title=f'Event {i}',
                category=self.category,
                start_time=now + timedelta(hours=i),
                end_time=now + timedelta(hours=i+1)
            )
            event_ids.append(event.id)
        
        initial_event_count = Event.objects.count()
        initial_log_count = SchedulingLog.objects.count()
        
        # Mock SchedulingLog.objects.create to fail
        with patch.object(SchedulingLog.objects, 'create', side_effect=IntegrityError("Simulated log error")):
            with self.assertRaises(IntegrityError):
                engine.bulk_delete_events(event_ids, operation_name='test_bulk_delete')
        
        # Verify rollback: all events should still exist
        self.assertEqual(Event.objects.count(), initial_event_count)
        for event_id in event_ids:
            self.assertTrue(Event.objects.filter(id=event_id).exists())
        
        # Verify no log was created
        self.assertEqual(SchedulingLog.objects.count(), initial_log_count)
    
    def test_transaction_logging_on_failure(self):
        """
        Test that transaction failures are properly logged.
        
        Requirements: 10.4
        """
        import logging
        
        engine = SchedulingEngine(self.user)
        
        now = timezone.now()
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            category=self.category,
            start_time=now,
            end_time=now + timedelta(hours=1)
        )
        
        # Create a custom handler to capture log records
        class LogCapture(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []
            
            def emit(self, record):
                self.records.append(record)
        
        log_capture = LogCapture()
        log_capture.setLevel(logging.ERROR)
        logger = logging.getLogger('scheduler.services')
        logger.addHandler(log_capture)
        
        try:
            # Mock Event.save to fail
            with patch.object(Event, 'save', side_effect=IntegrityError("Test error")):
                with self.assertRaises(IntegrityError):
                    engine.optimize_schedule(
                        start_date=now - timedelta(hours=1),
                        end_date=now + timedelta(hours=2),
                        save_to_db=True
                    )
            
            # Verify error was logged
            error_records = [r for r in log_capture.records if r.levelname == 'ERROR']
            self.assertTrue(len(error_records) > 0, "No error logs captured")
            
            # Find the transaction failure log
            transaction_error = None
            for record in error_records:
                if 'Transaction failed' in record.getMessage():
                    transaction_error = record
                    break
            
            self.assertIsNotNone(transaction_error, "Transaction failure not logged")
            self.assertIn('schedule optimization', transaction_error.getMessage())
            self.assertEqual(transaction_error.user_id, self.user.id)
            self.assertEqual(transaction_error.operation, 'optimize_schedule')
        finally:
            logger.removeHandler(log_capture)


class ViewTransactionRollbackTestCase(TestCase):
    """
    Test cases for transaction rollback in views.
    
    Requirements: 10.4
    """
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            name='Test User',
            timezone='UTC'
        )
        
        self.category = Category.objects.create(
            name='Test',
            priority_level=3,
            color='#FF0000',
            description='Test category'
        )
    
    def test_event_create_rollback_on_log_failure(self):
        """
        Test that event creation rolls back if logging fails.
        
        Requirements: 10.4
        """
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        
        client = APIClient()
        
        # Authenticate
        refresh = RefreshToken.for_user(self.user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        initial_event_count = Event.objects.count()
        initial_log_count = SchedulingLog.objects.count()
        
        # Mock SchedulingLog.objects.create to fail
        with patch.object(SchedulingLog.objects, 'create', side_effect=IntegrityError("Log error")):
            response = client.post('/api/events/', {
                'title': 'Test Event',
                'category': self.category.id,
                'start_time': timezone.now().isoformat(),
                'end_time': (timezone.now() + timedelta(hours=1)).isoformat()
            }, format='json')
        
        # Request should fail
        self.assertEqual(response.status_code, 500)
        
        # Verify rollback: no event was created
        self.assertEqual(Event.objects.count(), initial_event_count)
        
        # Verify no log was created
        self.assertEqual(SchedulingLog.objects.count(), initial_log_count)
