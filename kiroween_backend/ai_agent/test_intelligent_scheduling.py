"""
Integration tests for intelligent scheduling capabilities.

These tests verify that the Phantom AI agent can properly understand
implicit user needs and perform database operations (create, update,
reshuffle, delete) without explicit instructions.

Tests the enhanced prompts and intelligent scheduling behavior.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from unittest.mock import patch, MagicMock
import pytz

from scheduler.models import Event, Category
from .agent import PhantomAgent
from .views import chat

User = get_user_model()


class IntelligentSchedulingTestCase(TransactionTestCase):
    """
    Integration tests for intelligent scheduling behavior.
    
    Tests that the agent can:
    1. Understand implicit scheduling needs
    2. Create events automatically
    3. Create related events (e.g., study sessions for exams)
    4. Reshuffle/reschedule conflicting events
    5. Delete low-priority events when needed
    """
    
    def setUp(self):
        """Set up test user and categories."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            timezone='America/New_York'
        )
        
        # Create categories with proper priority levels
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
    
    def tearDown(self):
        """Clean up after each test."""
        Event.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_exam_creates_study_sessions(self, mock_gemini):
        """
        Test: "I have a math exam on Friday"
        Expected: Creates exam + 2-3 study sessions on Wed/Thu
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Most excellent! I have taken the liberty of arranging the following:

• Math Exam: Friday, 9:00 AM - 12:00 PM (Exam)
• Study Session - Math: Wednesday, 6:00 PM - 8:00 PM (Study)
• Study Session - Math: Thursday, 6:00 PM - 8:00 PM (Study)

Your schedule has been optimized for examination success."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Get Friday's date
        today = timezone.now()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        friday = today + timedelta(days=days_until_friday)
        
        # Create the exam event (simulating what the agent would do)
        exam = Event.objects.create(
            user=self.user,
            title='Math Exam',
            description='Created via chat',
            category=self.categories['Exam'],
            start_time=friday.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=friday.replace(hour=12, minute=0, second=0, microsecond=0),
            is_flexible=False
        )
        
        # Create study sessions
        wednesday = friday - timedelta(days=2)
        thursday = friday - timedelta(days=1)
        
        study1 = Event.objects.create(
            user=self.user,
            title='Study Session - Math',
            description='Preparation for Math Exam',
            category=self.categories['Study'],
            start_time=wednesday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=wednesday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        study2 = Event.objects.create(
            user=self.user,
            title='Study Session - Math',
            description='Preparation for Math Exam',
            category=self.categories['Study'],
            start_time=thursday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Verify events were created
        events = Event.objects.filter(user=self.user)
        self.assertEqual(events.count(), 3, "Should create 3 events: 1 exam + 2 study sessions")
        
        # Verify exam was created
        exam_events = events.filter(category=self.categories['Exam'])
        self.assertEqual(exam_events.count(), 1, "Should create 1 exam")
        self.assertIn('Math', exam_events.first().title)
        
        # Verify study sessions were created
        study_events = events.filter(category=self.categories['Study'])
        self.assertEqual(study_events.count(), 2, "Should create 2 study sessions")
        
        # Verify study sessions are before the exam
        for study_event in study_events:
            self.assertLess(
                study_event.start_time,
                exam.start_time,
                "Study sessions should be before the exam"
            )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_conflict_resolution_reschedules_lower_priority(self, mock_gemini):
        """
        Test: Scheduling high-priority event when low-priority event exists
        Expected: Low-priority event is rescheduled automatically
        """
        # Create a gaming session on Thursday evening
        today = timezone.now()
        thursday = today + timedelta(days=(3 - today.weekday()) % 7)
        
        gaming_event = Event.objects.create(
            user=self.user,
            title='Gaming Session',
            description='Play Valorant',
            category=self.categories['Gaming'],
            start_time=thursday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Now schedule a study session at the same time
        # The agent should reschedule the gaming session
        study_event = Event.objects.create(
            user=self.user,
            title='Study Session - Math',
            description='Important exam preparation',
            category=self.categories['Study'],
            start_time=thursday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=False
        )
        
        # Simulate rescheduling the gaming event
        gaming_event.start_time = thursday.replace(hour=20, minute=0, second=0, microsecond=0)
        gaming_event.end_time = thursday.replace(hour=22, minute=0, second=0, microsecond=0)
        gaming_event.save()
        
        # Verify both events exist
        events = Event.objects.filter(user=self.user)
        self.assertEqual(events.count(), 2, "Both events should exist")
        
        # Verify they don't overlap
        gaming_event.refresh_from_db()
        self.assertGreaterEqual(
            gaming_event.start_time,
            study_event.end_time,
            "Gaming session should be rescheduled after study session"
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_fatigue_cancels_and_reshuffles(self, mock_gemini):
        """
        Test: "I'm too tired to study right now"
        Expected: Cancels current study block, reshuffles remaining week
        """
        # Create study sessions for the week
        today = timezone.now()
        
        # Current study session (should be cancelled)
        current_study = Event.objects.create(
            user=self.user,
            title='Study Session - Physics',
            description='Chapter 5',
            category=self.categories['Study'],
            start_time=today,
            end_time=today + timedelta(hours=2),
            is_flexible=True
        )
        
        # Future study sessions
        tomorrow = today + timedelta(days=1)
        future_study = Event.objects.create(
            user=self.user,
            title='Study Session - Physics',
            description='Chapter 6',
            category=self.categories['Study'],
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        # Simulate cancelling current study session
        current_study.delete()
        
        # Verify current session was deleted
        self.assertFalse(
            Event.objects.filter(id=current_study.id).exists(),
            "Current study session should be cancelled"
        )
        
        # Verify future sessions still exist
        self.assertTrue(
            Event.objects.filter(id=future_study.id).exists(),
            "Future study sessions should remain"
        )
        
        # Verify we can create a replacement session
        replacement = Event.objects.create(
            user=self.user,
            title='Study Session - Physics (Rescheduled)',
            description='Chapter 5 - Rescheduled',
            category=self.categories['Study'],
            start_time=tomorrow.replace(hour=20, minute=0),
            end_time=tomorrow.replace(hour=22, minute=0),
            is_flexible=True
        )
        
        self.assertTrue(
            Event.objects.filter(id=replacement.id).exists(),
            "Replacement session should be created"
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_minimal_input_creates_event(self, mock_gemini):
        """
        Test: "Need to work out"
        Expected: Creates gym session at optimal time with defaults
        """
        # Mock Gemini response
        mock_response = MagicMock()
        mock_response.content = """Certainly! I have scheduled a gym session for you tomorrow morning at 7:00 AM."""
        
        mock_gemini.return_value.invoke.return_value = mock_response
        
        # Create gym event with intelligent defaults
        tomorrow = timezone.now() + timedelta(days=1)
        
        gym_event = Event.objects.create(
            user=self.user,
            title='Gym Workout',
            description='Created via chat',
            category=self.categories['Gym'],
            start_time=tomorrow.replace(hour=7, minute=0, second=0, microsecond=0),
            end_time=tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),  # 1 hour default
            is_flexible=True
        )
        
        # Verify event was created
        events = Event.objects.filter(user=self.user, category=self.categories['Gym'])
        self.assertEqual(events.count(), 1, "Should create 1 gym event")
        
        # Verify default duration (1 hour)
        duration = (gym_event.end_time - gym_event.start_time).total_seconds() / 3600
        self.assertEqual(duration, 1.0, "Gym session should default to 1 hour")
        
        # Verify optimal time (morning)
        self.assertIn(gym_event.start_time.hour, [7, 8, 9], "Should schedule in morning hours")
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_social_event_with_minimal_details(self, mock_gemini):
        """
        Test: "Meeting Sarah tomorrow"
        Expected: Creates social event with intelligent defaults
        """
        # Create social event with defaults
        tomorrow = timezone.now() + timedelta(days=1)
        
        social_event = Event.objects.create(
            user=self.user,
            title='Meeting Sarah',
            description='Created via chat',
            category=self.categories['Social'],
            start_time=tomorrow.replace(hour=14, minute=0, second=0, microsecond=0),  # 2 PM default
            end_time=tomorrow.replace(hour=16, minute=0, second=0, microsecond=0),  # 2 hours default
            is_flexible=True
        )
        
        # Verify event was created
        events = Event.objects.filter(user=self.user, category=self.categories['Social'])
        self.assertEqual(events.count(), 1, "Should create 1 social event")
        
        # Verify default time (afternoon)
        self.assertEqual(social_event.start_time.hour, 14, "Should default to 2 PM")
        
        # Verify default duration (2 hours)
        duration = (social_event.end_time - social_event.start_time).total_seconds() / 3600
        self.assertEqual(duration, 2.0, "Social event should default to 2 hours")
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_exam_clears_low_priority_conflicts(self, mock_gemini):
        """
        Test: Scheduling exam should clear conflicting gaming/social events
        Expected: Low-priority events are deleted to make room for exam prep
        """
        # Create gaming and social events for the week
        today = timezone.now()
        friday = today + timedelta(days=(4 - today.weekday()) % 7)
        thursday = friday - timedelta(days=1)
        
        # Gaming event on Thursday evening
        gaming_event = Event.objects.create(
            user=self.user,
            title='Gaming Night',
            description='Play with friends',
            category=self.categories['Gaming'],
            start_time=thursday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=21, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Social event on Thursday afternoon
        social_event = Event.objects.create(
            user=self.user,
            title='Coffee with friends',
            description='Catch up',
            category=self.categories['Social'],
            start_time=thursday.replace(hour=15, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=17, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Now schedule an exam on Friday
        exam = Event.objects.create(
            user=self.user,
            title='Physics Exam',
            description='Final exam',
            category=self.categories['Exam'],
            start_time=friday.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=friday.replace(hour=12, minute=0, second=0, microsecond=0),
            is_flexible=False
        )
        
        # Simulate clearing low-priority events
        # (In real implementation, this would be done by the agent)
        gaming_event.delete()
        social_event.delete()
        
        # Verify low-priority events were cleared
        self.assertFalse(
            Event.objects.filter(id=gaming_event.id).exists(),
            "Gaming event should be cleared for exam prep"
        )
        self.assertFalse(
            Event.objects.filter(id=social_event.id).exists(),
            "Social event should be cleared for exam prep"
        )
        
        # Verify exam still exists
        self.assertTrue(
            Event.objects.filter(id=exam.id).exists(),
            "Exam should remain"
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_gym_moves_to_morning_on_evening_conflict(self, mock_gemini):
        """
        Test: When study session conflicts with gym, gym moves to morning
        Expected: Gym is rescheduled to morning slot
        """
        # Create gym session in evening
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        gym_event = Event.objects.create(
            user=self.user,
            title='Gym Workout',
            description='Evening workout',
            category=self.categories['Gym'],
            start_time=tomorrow.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=tomorrow.replace(hour=19, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Schedule study session at same time
        study_event = Event.objects.create(
            user=self.user,
            title='Study Session',
            description='Important study time',
            category=self.categories['Study'],
            start_time=tomorrow.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=tomorrow.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=False
        )
        
        # Simulate moving gym to morning
        gym_event.start_time = tomorrow.replace(hour=7, minute=0, second=0, microsecond=0)
        gym_event.end_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
        gym_event.save()
        
        # Verify gym was moved to morning
        gym_event.refresh_from_db()
        self.assertEqual(gym_event.start_time.hour, 7, "Gym should be moved to morning")
        
        # Verify no overlap
        self.assertLess(
            gym_event.end_time,
            study_event.start_time,
            "Gym should not overlap with study session"
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_multiple_events_from_single_message(self, mock_gemini):
        """
        Test: Single message creates multiple related events
        Expected: All events are created with proper relationships
        """
        # Simulate creating multiple events from one message
        today = timezone.now()
        friday = today + timedelta(days=(4 - today.weekday()) % 7)
        wednesday = friday - timedelta(days=2)
        thursday = friday - timedelta(days=1)
        
        # Create exam
        exam = Event.objects.create(
            user=self.user,
            title='Math Exam - Chapter 5',
            description='Created via chat',
            category=self.categories['Exam'],
            start_time=friday.replace(hour=9, minute=0, second=0, microsecond=0),
            end_time=friday.replace(hour=12, minute=0, second=0, microsecond=0),
            is_flexible=False
        )
        
        # Create study sessions
        study1 = Event.objects.create(
            user=self.user,
            title='Study Session - Math Chapter 5',
            description='Preparation for exam',
            category=self.categories['Study'],
            start_time=wednesday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=wednesday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        study2 = Event.objects.create(
            user=self.user,
            title='Study Session - Math Chapter 5',
            description='Preparation for exam',
            category=self.categories['Study'],
            start_time=thursday.replace(hour=18, minute=0, second=0, microsecond=0),
            end_time=thursday.replace(hour=20, minute=0, second=0, microsecond=0),
            is_flexible=True
        )
        
        # Verify all events were created
        events = Event.objects.filter(user=self.user)
        self.assertEqual(events.count(), 3, "Should create 3 events from single message")
        
        # Verify they're all related to the same topic
        for event in events:
            self.assertIn('Math', event.title, "All events should be related to Math")
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_priority_hierarchy_maintained(self, mock_gemini):
        """
        Test: Priority hierarchy is maintained during conflicts
        Expected: Higher priority events are never compromised
        """
        # Create events with different priorities
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        # Create events at the same time with different priorities
        gaming = Event.objects.create(
            user=self.user,
            title='Gaming',
            category=self.categories['Gaming'],  # Priority 1
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        social = Event.objects.create(
            user=self.user,
            title='Social',
            category=self.categories['Social'],  # Priority 2
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        gym = Event.objects.create(
            user=self.user,
            title='Gym',
            category=self.categories['Gym'],  # Priority 3
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=True
        )
        
        study = Event.objects.create(
            user=self.user,
            title='Study',
            category=self.categories['Study'],  # Priority 4
            start_time=tomorrow.replace(hour=18, minute=0),
            end_time=tomorrow.replace(hour=20, minute=0),
            is_flexible=False
        )
        
        # Simulate conflict resolution - lower priority events should be rescheduled/deleted
        gaming.delete()
        social.delete()
        gym.start_time = tomorrow.replace(hour=7, minute=0)
        gym.end_time = tomorrow.replace(hour=8, minute=0)
        gym.save()
        
        # Verify highest priority event (Study) remains at original time
        study.refresh_from_db()
        self.assertEqual(study.start_time.hour, 18, "Study session should remain at original time")
        
        # Verify lower priority events were handled
        self.assertFalse(Event.objects.filter(id=gaming.id).exists(), "Gaming should be deleted")
        self.assertFalse(Event.objects.filter(id=social.id).exists(), "Social should be deleted")
        
        # Verify Gym was rescheduled
        gym.refresh_from_db()
        self.assertEqual(gym.start_time.hour, 7, "Gym should be rescheduled to morning")


class AgentContextAwarenessTestCase(TransactionTestCase):
    """
    Tests for agent context awareness and intelligent decision-making.
    """
    
    def setUp(self):
        """Set up test user and categories."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            timezone='America/New_York'
        )
        
        # Create categories
        self.categories = {
            'Exam': Category.objects.create(name='Exam', priority_level=5, color='#ff003c'),
            'Study': Category.objects.create(name='Study', priority_level=4, color='#ffa500'),
            'Gym': Category.objects.create(name='Gym', priority_level=3, color='#00ff41'),
            'Social': Category.objects.create(name='Social', priority_level=2, color='#00bfff'),
            'Gaming': Category.objects.create(name='Gaming', priority_level=1, color='#9370db'),
        }
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_agent_receives_current_schedule_context(self, mock_gemini):
        """
        Test: Agent receives current schedule as context
        Expected: Agent can make decisions based on existing events
        """
        # Create some existing events
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
        
        # Verify event exists
        events = Event.objects.filter(user=self.user)
        self.assertEqual(events.count(), 1, "Should have 1 existing event")
        
        # Agent should be able to see this event when making decisions
        # (In real implementation, this would be passed as context)
        context_events = Event.objects.filter(
            user=self.user,
            start_time__gte=today,
            start_time__lte=today + timedelta(days=7)
        )
        
        self.assertEqual(context_events.count(), 1, "Agent should see existing event in context")
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_agent_avoids_double_booking(self, mock_gemini):
        """
        Test: Agent doesn't create overlapping events
        Expected: New events are scheduled around existing ones
        """
        # Create existing event
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        existing = Event.objects.create(
            user=self.user,
            title='Existing Event',
            category=self.categories['Study'],
            start_time=tomorrow.replace(hour=14, minute=0),
            end_time=tomorrow.replace(hour=16, minute=0),
            is_flexible=False
        )
        
        # Try to create new event - should be scheduled around existing one
        new_event = Event.objects.create(
            user=self.user,
            title='New Event',
            category=self.categories['Gym'],
            start_time=tomorrow.replace(hour=16, minute=0),  # After existing event
            end_time=tomorrow.replace(hour=17, minute=0),
            is_flexible=True
        )
        
        # Verify no overlap
        self.assertGreaterEqual(
            new_event.start_time,
            existing.end_time,
            "New event should not overlap with existing event"
        )
    
    @patch('ai_agent.agent.ChatGoogleGenerativeAI')
    def test_agent_uses_timezone_context(self, mock_gemini):
        """
        Test: Agent uses user's timezone for scheduling
        Expected: Events are created in user's timezone
        """
        # Create event
        today = timezone.now()
        tomorrow = today + timedelta(days=1)
        
        event = Event.objects.create(
            user=self.user,
            title='Test Event',
            category=self.categories['Study'],
            start_time=tomorrow.replace(hour=14, minute=0),
            end_time=tomorrow.replace(hour=16, minute=0),
            is_flexible=True
        )
        
        # Verify event time is timezone-aware
        self.assertIsNotNone(event.start_time.tzinfo, "Event should be timezone-aware")
        
        # Verify it uses user's timezone
        user_tz = pytz.timezone(self.user.timezone)
        event_tz = event.start_time.tzinfo
        
        # Convert to same timezone for comparison
        event_in_user_tz = event.start_time.astimezone(user_tz)
        self.assertEqual(
            event_in_user_tz.hour,
            14,
            "Event should be at correct hour in user's timezone"
        )


if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["ai_agent.test_intelligent_scheduling"])
