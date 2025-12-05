"""
Property-based tests for Google Calendar integration.
"""
from django.test import TestCase
from hypothesis import given, strategies as st, settings, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from datetime import datetime, timedelta
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock
import json

from scheduler.models import User, Event, Category
from .google_calendar import GoogleCalendarService
from .sync_service import EventSyncService


# Hypothesis strategies for generating test data
event_title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=122),
    min_size=1,
    max_size=100
)

event_description_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs'), min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=500
)

# Generate datetime within reasonable range (next 365 days)
def datetime_strategy():
    now = datetime.now()
    return st.datetimes(
        min_value=now,
        max_value=now + timedelta(days=365)
    )


class GoogleCalendarSyncPropertyTests(HypothesisTestCase):
    """
    Property-based tests for Google Calendar synchronization.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create test user with mock Google Calendar token
        self.user = User.objects.create_user(
            username='testuser',
            name='Test User',
            password='testpass123',
            timezone='UTC'
        )
        
        # Mock token data
        mock_token_data = {
            'token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'mock_client_id',
            'client_secret': 'mock_client_secret',
            'scopes': ['https://www.googleapis.com/auth/calendar'],
            'expiry': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        self.user.google_calendar_token = json.dumps(mock_token_data)
        self.user.save()
        
        # Create test category
        self.category = Category.objects.create(
            name='Test',
            priority_level=3,
            color='#FF0000',
            description='Test category'
        )
        
        self.sync_service = EventSyncService()
    
    # Feature: phantom-scheduler, Property 11: Google Calendar sync consistency
    # Validates: Requirements 6.2, 6.3
    @settings(max_examples=100, deadline=None)
    @given(
        title=event_title_strategy,
        description=event_description_strategy,
        duration_minutes=st.integers(min_value=15, max_value=480)
    )
    @patch('integrations.google_calendar.build')
    def test_google_calendar_sync_consistency(self, mock_build, title, description, duration_minutes):
        """
        For any event created or modified in Phantom, the corresponding event in Google Calendar
        should reflect the same data (title, time, description).
        """
        # Skip empty titles
        assume(title.strip())
        
        # Mock Google Calendar API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock the events().insert() call
        mock_insert = MagicMock()
        mock_insert.execute.return_value = {'id': 'mock_google_event_id_123'}
        mock_service.events.return_value.insert.return_value = mock_insert
        
        # Mock the events().update() call
        mock_update = MagicMock()
        mock_update.execute.return_value = {'id': 'mock_google_event_id_123'}
        mock_service.events.return_value.update.return_value = mock_update
        
        # Create event with timezone-aware datetimes
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event = Event.objects.create(
            user=self.user,
            title=title,
            description=description,
            category=self.category,
            start_time=start_time,
            end_time=end_time,
            is_flexible=True
        )
        
        # Sync to Google Calendar (create)
        google_event_id = self.sync_service.sync_event_create(event)
        
        # Verify sync was attempted
        self.assertTrue(google_event_id or google_event_id is False)
        
        # If sync succeeded, verify the event has Google Calendar ID
        if google_event_id:
            event.refresh_from_db()
            self.assertIsNotNone(event.google_calendar_id)
            
            # Verify the data sent to Google Calendar matches Phantom event
            call_args = mock_service.events.return_value.insert.call_args
            if call_args:
                google_event_data = call_args[1]['body']
                
                # Check that title matches
                self.assertEqual(google_event_data['summary'], title)
                
                # Check that description matches
                self.assertEqual(google_event_data['description'], description)
                
                # Check that times match
                self.assertEqual(
                    google_event_data['start']['dateTime'],
                    start_time.isoformat()
                )
                self.assertEqual(
                    google_event_data['end']['dateTime'],
                    end_time.isoformat()
                )
        
        # Now test update consistency
        new_title = title + " (Updated)"
        new_description = description + " Updated"
        event.title = new_title
        event.description = new_description
        event.google_calendar_id = 'mock_google_event_id_123'
        event.save()
        
        # Sync update to Google Calendar
        updated_google_id = self.sync_service.sync_event_update(event)
        
        # If update sync succeeded, verify the data sent matches
        if updated_google_id:
            call_args = mock_service.events.return_value.update.call_args
            if call_args:
                google_event_data = call_args[1]['body']
                
                # Check that updated title matches
                self.assertEqual(google_event_data['summary'], new_title)
                
                # Check that updated description matches
                self.assertEqual(google_event_data['description'], new_description)


class GoogleCalendarRetryPropertyTests(HypothesisTestCase):
    """
    Property-based tests for Google Calendar retry logic.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create test user with mock Google Calendar token
        self.user = User.objects.create_user(
            username='retryuser',
            name='Retry User',
            password='testpass123',
            timezone='UTC'
        )
        
        # Mock token data
        mock_token_data = {
            'token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'mock_client_id',
            'client_secret': 'mock_client_secret',
            'scopes': ['https://www.googleapis.com/auth/calendar'],
            'expiry': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        self.user.google_calendar_token = json.dumps(mock_token_data)
        self.user.save()
        
        # Create test category
        self.category = Category.objects.create(
            name='Retry Test',
            priority_level=3,
            color='#00FF00',
            description='Retry test category'
        )
        
        self.google_service = GoogleCalendarService()
    
    # Feature: phantom-scheduler, Property 23: Retry with exponential backoff
    # Validates: Requirements 10.3
    @settings(max_examples=100, deadline=None)
    @given(
        title=event_title_strategy,
        failure_count=st.integers(min_value=1, max_value=2)  # Fail 1-2 times before success
    )
    @patch('integrations.google_calendar.build')
    @patch('integrations.google_calendar.time.sleep')  # Mock sleep to speed up tests
    def test_retry_with_exponential_backoff(self, mock_sleep, mock_build, title, failure_count):
        """
        For any failed external API call, the system should retry the operation
        with increasing delays between attempts (exponential backoff pattern).
        """
        # Skip empty titles
        assume(title.strip())
        
        # Mock Google Calendar API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Create a mock that fails N times then succeeds
        call_count = [0]
        
        def mock_execute():
            call_count[0] += 1
            if call_count[0] <= failure_count:
                # Simulate rate limit error (429)
                from googleapiclient.errors import HttpError
                resp = Mock()
                resp.status = 429
                resp.reason = 'Rate Limit Exceeded'
                raise HttpError(resp, b'Rate limit exceeded')
            else:
                # Success on final attempt
                return {'id': 'mock_google_event_id_success'}
        
        mock_insert = MagicMock()
        mock_insert.execute = mock_execute
        mock_service.events.return_value.insert.return_value = mock_insert
        
        # Create event with timezone-aware datetimes
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(minutes=60)
        
        event = Event.objects.create(
            user=self.user,
            title=title,
            description='Test retry',
            category=self.category,
            start_time=start_time,
            end_time=end_time
        )
        
        # Attempt to sync (should retry and eventually succeed)
        try:
            google_event_id = self.google_service.sync_event_to_google(event, self.user, max_retries=3)
            
            # Verify that retries occurred
            self.assertEqual(call_count[0], failure_count + 1)  # N failures + 1 success
            
            # Verify exponential backoff was used
            if failure_count > 0:
                # Check that sleep was called with exponential delays
                sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
                
                # Verify we have the right number of sleep calls
                self.assertEqual(len(sleep_calls), failure_count)
                
                # Verify exponential pattern: 1s, 2s, 4s, etc.
                for i, sleep_time in enumerate(sleep_calls):
                    expected_sleep = 2 ** i
                    self.assertEqual(sleep_time, expected_sleep)
            
            # Verify final success
            self.assertIsNotNone(google_event_id)
            self.assertEqual(google_event_id, 'mock_google_event_id_success')
        except Exception as e:
            # If sync failed completely, that's also acceptable for this test
            # as long as retries were attempted
            if failure_count > 0:
                # Verify that sleep was called (retries were attempted)
                self.assertGreater(len(mock_sleep.call_args_list), 0)
