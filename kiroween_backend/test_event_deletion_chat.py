"""
Test event deletion functionality via chat with real Gemini API.

Run from kiroween_backend directory:
    python test_event_deletion_chat.py
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from scheduler.models import User, Event, Category
from ai_agent.views import chat
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
import sys


def setup_test_data():
    """Create test user and events."""
    # Get or create test user
    user = User.objects.first()
    if not user:
        print("No user found. Please create a user first.")
        sys.exit(1)
    
    print(f"Using user: {user.username} (timezone: {user.timezone})")
    
    # Get categories
    social_cat = Category.objects.get(name='Social')
    gym_cat = Category.objects.get(name='Gym')
    study_cat = Category.objects.get(name='Study')
    
    # Clear existing test events with "test" in title
    Event.objects.filter(user=user, title__icontains='test').delete()
    
    # Create test events
    dhaka_tz = pytz.timezone(user.timezone)
    now = timezone.now().astimezone(dhaka_tz)
    
    events = []
    
    # Event 1: Test dinner
    dinner_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 20, 0, 0))
    if dinner_start < now:
        dinner_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='test dinner with friends',
        description='Test social dinner event',
        category=social_cat,
        start_time=dinner_start,
        end_time=dinner_start + timedelta(hours=2),
        is_flexible=True
    ))
    
    # Event 2: Test gym
    gym_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 7, 0, 0))
    if gym_start < now:
        gym_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='test morning workout',
        description='Test gym session',
        category=gym_cat,
        start_time=gym_start,
        end_time=gym_start + timedelta(hours=1),
        is_flexible=True
    ))
    
    # Event 3: Test study
    study_start = dhaka_tz.localize(datetime(now.year, now.month, now.day, 14, 0, 0))
    if study_start < now:
        study_start += timedelta(days=1)
    events.append(Event.objects.create(
        user=user,
        title='test study math',
        description='Test study session',
        category=study_cat,
        start_time=study_start,
        end_time=study_start + timedelta(hours=2),
        is_flexible=True
    ))
    
    return user, events


def test_deletion(user, prompt):
    """Test deletion with a specific prompt."""
    factory = APIRequestFactory()
    request = factory.post('/api/chat/', {'message': prompt}, format='json')
    force_authenticate(request, user=user)
    
    print(f"\n{'='*80}")
    print(f"PROMPT: {prompt}")
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
    
    print(f"\nIntent: {response_data.get('intent', 'unknown')}")
    print(f"Events deleted: {len(response_data.get('events_deleted', []))}")
    
    if response_data.get('events_deleted'):
        print("\nDeleted events:")
        for event in response_data['events_deleted']:
            print(f"  - {event['title']} (ID: {event['id']})")
    
    # Check if deletion occurred
    deleted_count = events_before - events_after
    success = deleted_count > 0
    
    print(f"\n{'✓' if success else '✗'} Deletion {'successful' if success else 'failed'} ({deleted_count} events deleted)")
    
    return success


def main():
    """Run deletion tests."""
    print("\n" + "="*80)
    print("EVENT DELETION TEST WITH REAL GEMINI API")
    print("="*80)
    
    # Setup
    print("\nSetting up test data...")
    user, events = setup_test_data()
    print(f"\nCreated {len(events)} test events:")
    for event in events:
        print(f"  - {event.title} ({event.category.name}) at {event.start_time.strftime('%I:%M %p')}")
    
    # Test cases
    test_cases = [
        'delete my test dinner',
        'cancel the test workout',
        'remove test study',
    ]
    
    results = []
    for i, prompt in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST {i}/{len(test_cases)}")
        print(f"{'#'*80}")
        
        success = test_deletion(user, prompt)
        results.append({'prompt': prompt, 'success': success})
        
        # Wait between tests
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
        print(f"{i}. {status} - \"{result['prompt']}\"")
    
    print(f"\n{'='*80}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print(f"{'='*80}")
    
    # Cleanup
    print("\nCleaning up remaining test events...")
    Event.objects.filter(user=user, title__icontains='test').delete()
    
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
