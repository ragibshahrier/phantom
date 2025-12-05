"""
Test event deletion functionality via chat with real Gemini API.

This test creates events and then attempts to delete them using natural language
without explicitly mentioning dates or times.

Run from kiroween_backend directory:
    python test_event_deletion_chat.py
"""
import django
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from scheduler.models import User, Event, Category
from ai_agent.views import chat
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime, timedelta
from django.utils import timezone
import pytz


def setup_test_data():
    """Create test user and events."""
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='test_deletion_user',
        defaults={
            'name': 'Test User',
            'timezone': 'Asia/Dhaka'
        }
    )
    
    # Ensure timezone is set
    if user.timezone != 'Asia/Dhaka':
        user.timezone = 'Asia/Dhaka'
        user.save()
    
    # Get categories
    social_cat, _ = Category.objects.get_or_create(
        name='Social',
        defaults={'priority_level': 2, 'color': '#FF6B6B', 'description': 'Social events'}
    )
    
    gym_cat, _ = Category.objects.get_or_create(
        name='Gym',
        defaults={'priority_level': 3, 'color': '#4ECDC4', 'description': 'Gym and fitness'}
    )
    
    study_cat, _ = Category.objects.get_or_create(
        name='Study',
        defaults={'priority_level': 4, 'color': '#FFA500', 'description': 'Study sessions'}
    )
    
    # Clear existing test events
    Event.objects.filter(user=user).delete()
    
    # Create test events
    dhaka_tz = pytz.timezone('Asia/Dhaka')
    now = timezone.now().astimezone(dhaka_tz)
    
    events = []
    
    # Event 1: Dinner with friends (Social)
    dinner_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 20, 0, 0))
    if dinner_start < now:
        dinner_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='dinner with friends',
        description='Social dinner event',
        category=social_cat,
        start_time=dinner_start,
        end_time=dinner_start + timedelta(hours=2),
        is_flexible=True
    ))
    
    # Event 2: Gym workout
    gym_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 7, 0, 0))
    if gym_start < now:
        gym_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='morning workout',
        description='Gym session',
        category=gym_cat,
        start_time=gym_start,
        end_time=gym_start + timedelta(hours=1),
        is_flexible=True
    ))
    
    # Event 3: Study session
    study_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 14, 0, 0))
    if study_start < now:
        study_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='study math chapter 5',
        description='Study session',
        category=study_cat,
        start_time=study_start,
        end_time=study_start + timedelta(hours=2),
        is_flexible=True
    ))
    
    # Event 4: Coffee meeting
    coffee_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 16, 0, 0))
    if coffee_start < now:
        coffee_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='coffee with Sarah',
        description='Coffee meeting',
        category=social_cat,
        start_time=coffee_start,
        end_time=coffee_start + timedelta(hours=1),
        is_flexible=True
    ))
    
    return user, events


def test_deletion(user, prompt, expected_keywords):
    """Test deletion with a specific prompt."""
    factory = APIRequestFactory()
    request = factory.post('/api/chat/', {'message': prompt}, format='json')
    force_authenticate(request, user=user)
    
    print(f"\n{'='*80}")
    print(f"TEST: {prompt}")
    print(f"{'='*80}")
    
    # Get event count before
    events_before = Event.objects.filter(user=user).count()
    print(f"Events before: {events_before}")
    
    # Make the request
    response = chat(request)
    
    # Get event count after
    events_after = Event.objects.filter(user=user).count()
    print(f"Events after: {events_after}")
    
    # Check response
    response_data = response.data
    print(f"\nAgent Response:")
    print(f"{response_data.get('response', 'No response')}")
    
    print(f"\nIntent detected: {response_data.get('intent', 'unknown')}")
    print(f"Events deleted: {len(response_data.get('events_deleted', []))}")
    
    if response_data.get('events_deleted'):
        print("\nDeleted events:")
        for event in response_data['events_deleted']:
            print(f"  - {event['title']} (ID: {event['id']})")
    
    # Check if deletion occurred
    deleted_count = events_before - events_after
    success = deleted_count > 0
    
    # Check if expected keywords are in response
    response_text = response_data.get('response', '').lower()
    keywords_found = any(keyword.lower() in response_text for keyword in expected_keywords)
    
    print(f"\n{'✓' if success else '✗'} Deletion {'successful' if success else 'failed'}")
    print(f"{'✓' if keywords_found else '✗'} Expected keywords {'found' if keywords_found else 'not found'}")
    
    return success and keywords_found


def main():
    """Run all deletion tests."""
    print("\n" + "="*80)
    print("EVENT DELETION TESTS WITH REAL GEMINI API")
    print("="*80)
    
    # Setup
    print("\nSetting up test data...")
    user, events = setup_test_data()
    print(f"Created {len(events)} test events for user: {user.username}")
    print("\nTest events:")
    for event in events:
        print(f"  - {event.title} ({event.category.name}) at {event.start_time.strftime('%I:%M %p')}")
    
    # Test cases
    test_cases = [
        {
            'prompt': 'delete my dinner',
            'expected_keywords': ['delete', 'dinner', 'removed', 'cancelled'],
            'description': 'Delete by event title keyword'
        },
        {
            'prompt': 'cancel the workout',
            'expected_keywords': ['delete', 'workout', 'gym', 'cancelled'],
            'description': 'Delete by activity type'
        },
        {
            'prompt': 'remove my study session',
            'expected_keywords': ['delete', 'study', 'removed'],
            'description': 'Delete by category'
        },
        {
            'prompt': 'cancel coffee with Sarah',
            'expected_keywords': ['delete', 'coffee', 'sarah', 'cancelled'],
            'description': 'Delete by specific event name'
        },
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST {i}/{len(test_cases)}: {test_case['description']}")
        print(f"{'#'*80}")
        
        success = test_deletion(user, test_case['prompt'], test_case['expected_keywords'])
        results.append({
            'test': test_case['description'],
            'prompt': test_case['prompt'],
            'success': success
        })
        
        # Wait a bit between tests to avoid rate limiting
        import time
        time.sleep(2)
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for i, result in enumerate(results, 1):
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"{i}. {status} - {result['test']}")
        print(f"   Prompt: \"{result['prompt']}\"")
    
    print(f"\n{'='*80}")
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print(f"{'='*80}")
    
    # Cleanup
    print("\nCleaning up test data...")
    Event.objects.filter(user=user).delete()
    # Optionally delete test user
    # user.delete()
    
    return passed == total


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
