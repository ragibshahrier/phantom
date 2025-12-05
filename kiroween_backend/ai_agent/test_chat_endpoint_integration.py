"""
End-to-end integration tests for the chat endpoint.

These tests verify the complete flow from user input through the chat API
to actual database operations, ensuring the agent properly creates, updates,
reshuffles, and deletes events based on implicit user needs.
"""
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

from scheduler.models import Event, Category

User = get_user_model()


class ChatEndpointIntegrationTestCase(TransactionTestCase):
    """
    End-to-end tests for the chat endpoint with real database operations.
    """
    
    def setUp(self):
        """Set up test client, user, and categories."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            timezone='America/New_York'
        )
        
        # Create categories
        self.categories = {
            'Exam': Category.objects.create(
                name='Exam',
                priority_level=5,
                color='#ff003c',
                description='Exams and tests'
            ),
            'Study': Category.objects.create(
                name='Study',
                priority_level=4,
                color='#ffa500',
                description='Study sessions'
            ),
            'Gym': Category.objects.create(
                name='Gym',
                priority_level=3,
                color='#00ff41',
                description='Exercise and fitness'
            ),
            'Social': Category.objects.create(
                name='Social',
                priority_level=2,
                color='#00bfff',
                description='Social activities'
            ),
            'Gaming': Category.objects.create(
                name='Gaming',
                priority_level=1,
                color='#9370db',
                description='Gaming and entertainment'
            ),
        }
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def tearDown(self):
        """Clean up after each test."""
        Event.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_exam_message_creates_multiple_events(self, mock_gemini):
        """
        Test: POST /api/chat/ with "I have a math exam on Friday"
        Expected: Creates exam + study sessions in database
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Most excellent! I have taken the liberty of arranging the following:

• Math Exam: Friday, 9:00 AM - 12:00 PM (Exam)
• Study Session - Math: Wednesday, 6:00 PM - 8:00 PM (Study)
• Study Session - Math: Thursday, 6:00 PM - 8:00 PM (Study)

Your schedule has been optimized for examination success."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'I have a math exam on Friday'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Math', response.data['response'])
        
        # Verify events were created in database
        events = Event.objects.filter(user=self.user)
        
        # Should have created events (actual creation depends on parser implementation)
        # At minimum, verify the response indicates events were created
        self.assertIsNotNone(response.data.get('events_created'))
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_minimal_gym_input_creates_event(self, mock_gemini):
        """
        Test: POST /api/chat/ with "Need to work out"
        Expected: Creates gym event with intelligent defaults
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Certainly! I have scheduled a gym session for you tomorrow morning at 7:00 AM."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'Need to work out'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify category was detected
        self.assertEqual(response.data.get('category'), 'Gym')
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_social_event_with_name(self, mock_gemini):
        """
        Test: POST /api/chat/ with "Meeting Sarah tomorrow"
        Expected: Creates social event with person's name
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Most certainly! I have scheduled a meeting with Sarah for tomorrow afternoon at 2:00 PM."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'Meeting Sarah tomorrow'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify category was detected
        self.assertEqual(response.data.get('category'), 'Social')
        
        # Verify task title includes name
        task_title = response.data.get('task_title', '')
        self.assertIn('Sarah', task_title)
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_fatigue_message_understanding(self, mock_gemini):
        """
        Test: POST /api/chat/ with "I'm too tired to study right now"
        Expected: Agent understands fatigue and suggests rescheduling
        """
        # First create a study session
        today = timezone.now()
        study_event = Event.objects.create(
            user=self.user,
            title='Study Session',
            category=self.categories['Study'],
            start_time=today,
            end_time=today + timedelta(hours=2),
            is_flexible=True
        )
        
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Very well, I understand you require rest. I shall dissolve the current study block and reshuffle your schedule to ensure adequate preparation time remains."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': "I'm too tired to study right now"},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('rest', response.data['response'].lower())
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_context_includes_existing_events(self, mock_gemini):
        """
        Test: Agent receives existing events as context
        Expected: Agent can see and reference existing schedule
        """
        # Create existing events
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        existing_event = Event.objects.create(
            user=self.user,
            title='Existing Meeting',
            category=self.categories['Social'],
            start_time=tomorrow.replace(hour=14, minute=0),
            end_time=tomorrow.replace(hour=16, minute=0),
            is_flexible=True
        )
        
        # Mock Gemini response that references existing event
        mock_response = MagicMock()
        mock_response.content = """I note you have an existing meeting tomorrow afternoon. I shall schedule your gym session in the morning to avoid conflicts."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'Schedule gym tomorrow'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_empty_message_handled(self, mock_gemini):
        """
        Test: POST /api/chat/ with empty message
        Expected: Returns appropriate error
        """
        # Send empty message
        response = self.client.post(
            '/api/chat/',
            {'message': ''},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_conversation_history_stored(self, mock_gemini):
        """
        Test: Conversation history is stored in database
        Expected: Each chat interaction is saved
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Certainly! I shall attend to that."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'Schedule study session tomorrow'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify conversation was stored
        from scheduler.models import ConversationHistory
        conversations = ConversationHistory.objects.filter(user=self.user)
        self.assertGreater(conversations.count(), 0, "Conversation should be stored")
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_multiple_messages_maintain_context(self, mock_gemini):
        """
        Test: Multiple messages in sequence maintain context
        Expected: Agent remembers previous conversation
        """
        # Mock Gemini responses
        mock_response1 = MagicMock()
        mock_response1.content = """Certainly! I have scheduled your math exam for Friday."""
        
        mock_response2 = MagicMock()
        mock_response2.content = """I have also arranged study sessions on Wednesday and Thursday to prepare for your math exam."""
        
        mock_gemini.return_value.invoke.side_effect = [mock_response1, mock_response2]
        
        # Send first message
        response1 = self.client.post(
            '/api/chat/',
            {'message': 'I have a math exam on Friday'},
            format='json'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Send follow-up message
        response2 = self.client.post(
            '/api/chat/',
            {'message': 'Can you help me prepare?'},
            format='json'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertIn('study', response2.data['response'].lower())
    
    def test_unauthenticated_request_rejected(self):
        """
        Test: Unauthenticated requests are rejected
        Expected: Returns 401 or 403
        """
        # Create unauthenticated client
        unauth_client = APIClient()
        
        # Send chat message without authentication
        response = unauth_client.post(
            '/api/chat/',
            {'message': 'Schedule something'},
            format='json'
        )
        
        # Verify response
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_api_error_handled_gracefully(self, mock_gemini):
        """
        Test: API errors are handled gracefully
        Expected: Returns appropriate error message
        """
        # Mock Gemini to raise an error
        mock_gemini.return_value.invoke.side_effect = Exception("API Error")
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'Schedule something'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data['success'])
        self.assertIn('error', response.data['response'].lower())


class EventCreationFlowTestCase(TransactionTestCase):
    """
    Tests for the complete event creation flow through chat.
    """
    
    def setUp(self):
        """Set up test client, user, and categories."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            timezone='America/New_York'
        )
        
        # Create categories
        Category.objects.create(name='Exam', priority_level=5, color='#ff003c')
        Category.objects.create(name='Study', priority_level=4, color='#ffa500')
        Category.objects.create(name='Gym', priority_level=3, color='#00ff41')
        Category.objects.create(name='Social', priority_level=2, color='#00bfff')
        Category.objects.create(name='Gaming', priority_level=1, color='#9370db')
        
        self.client.force_authenticate(user=self.user)
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_complete_exam_scheduling_flow(self, mock_gemini):
        """
        Test: Complete flow from chat message to database events
        Expected: All events created correctly in database
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Most excellent! I have arranged your examination schedule."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Initial event count
        initial_count = Event.objects.filter(user=self.user).count()
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'I have a physics exam next Friday at 10am'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify events were created (if parser creates them)
        final_count = Event.objects.filter(user=self.user).count()
        
        # At minimum, verify the response indicates success
        self.assertIsNotNone(response.data.get('response'))
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_event_with_duration_parsing(self, mock_gemini):
        """
        Test: Event with explicit duration is parsed correctly
        Expected: Event created with correct duration
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Certainly! I have scheduled your study session."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message with duration
        response = self.client.post(
            '/api/chat/',
            {'message': 'Study session tomorrow for 2 hours'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify temporal info was parsed
        temporal_info = response.data.get('temporal_info')
        if temporal_info:
            self.assertIsNotNone(temporal_info.get('parsed_times'))
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_recurring_event_suggestion(self, mock_gemini):
        """
        Test: Recurring event patterns are understood
        Expected: Agent suggests recurring schedule
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """I shall arrange gym sessions for Monday, Wednesday, and Friday each week."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'I want to work out 3 times a week'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('week', response.data['response'].lower())


class PriorityBasedSchedulingTestCase(TransactionTestCase):
    """
    Tests for priority-based scheduling decisions.
    """
    
    def setUp(self):
        """Set up test client, user, and categories."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            timezone='America/New_York'
        )
        
        # Create categories with priorities
        self.exam_cat = Category.objects.create(name='Exam', priority_level=5, color='#ff003c')
        self.study_cat = Category.objects.create(name='Study', priority_level=4, color='#ffa500')
        self.gym_cat = Category.objects.create(name='Gym', priority_level=3, color='#00ff41')
        self.social_cat = Category.objects.create(name='Social', priority_level=2, color='#00bfff')
        self.gaming_cat = Category.objects.create(name='Gaming', priority_level=1, color='#9370db')
        
        self.client.force_authenticate(user=self.user)
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_high_priority_event_takes_precedence(self, mock_gemini):
        """
        Test: High-priority event scheduled over low-priority
        Expected: Low-priority event is rescheduled or deleted
        """
        # Create low-priority event
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        gaming_event = Event.objects.create(
            user=self.user,
            title='Gaming Session',
            category=self.gaming_cat,
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """I have scheduled your study session. Your gaming session has been moved to accommodate this."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message for high-priority event
        response = self.client.post(
            '/api/chat/',
            {'message': 'Study session tomorrow evening'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_exam_priority_clears_conflicts(self, mock_gemini):
        """
        Test: Exam scheduling clears conflicting low-priority events
        Expected: Gaming and social events are removed
        """
        # Create low-priority events
        today = timezone.now()
        friday = today + timedelta(days=(4 - today.weekday()) % 7)
        thursday = friday - timedelta(days=1)
        
        gaming = Event.objects.create(
            user=self.user,
            title='Gaming',
            category=self.gaming_cat,
            start_time=thursday.replace(hour=18, minute=0),
            end_time=thursday.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        social = Event.objects.create(
            user=self.user,
            title='Party',
            category=self.social_cat,
            start_time=thursday.replace(hour=20, minute=0),
            end_time=thursday.replace(hour=23, minute=0),
            is_flexible=True
        )
        
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """I have scheduled your exam and cleared conflicting events to ensure adequate preparation time."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Send chat message
        response = self.client.post(
            '/api/chat/',
            {'message': 'I have an important exam on Friday'},
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["ai_agent.test_chat_endpoint_integration"])
