"""
Test event deletion with realistic event names (no "test" prefix).

Run from kiroween_backend directory:
    python test_deletion_real_scenarios.py
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


def create_realistic_events(user):
    """Create realistic events."""
    social_cat = Category.objects.get(name='Social')
    gym_cat = Category.objects.get(name='Gym')
    study_cat = Category.objects.get(name='Study')
    
    dhaka_tz = pytz.timezone(user.timezone)
    now = timezone.now().astimezone(dhaka_tz)
    
    events = []
    
    # Realistic event names
    event_data = [
        ('dinner with Sarah', social_cat, 19, 2),
        ('morning run', gym_cat, 6, 1),
        ('study calculus', study_cat, 14, 2),
        ('coffee meeting', social_cat, 16, 1),
        ('gym workout', gym_cat, 18, 1),
    ]
    
    for title, category, hour, duration in event_data:
        start = dhaka_tz.localize(datetime(now.year, now.month, now.day, hour, 0, 0))
        if start < now:
            start += timedelta(days=1)
        
        events.append(Event.objects.create(
            user=user,
            title=title,
            description=f'Created for deletion test',
            category=category,
            start_time=start,
            end_time=start + timedelta(hours=duration),
            is_flexible=True
        ))
    
    return events


def test_deletion(user, prompt, expected_title_keywords):
    """Test deletion and verify correct event was deleted."""
    factory = APIRequestFactory()
    request = factory.post('/api/chat/', {'message': prompt}, format='json')
    force_authenticate(request, user=user)
    
    print(f"\n{'='*80}")
    print(f"PROMPT: \"{prompt}\"")
    print(f"{'='*80}")
    
    # Get events before
    events_before = list(Event.objects.filter(user=user).values('id', 'title'))
    print(f"Events before ({len(events_before)}):")
    for e in events_before:
        print(f"  - {e['title']} (ID: {e['id']})")
    
    # Make the request
    response = chat(request)
    
    # Get events after
    events_after = list(Event.objects.filter(user=user).values('id', 'title'))
    print(f"\nEvents after ({len(events_after)}):")
    for e in events_after:
        print(f"  - {e['title']} (ID: {e['id']})")
    
    # Check response
    response_data = response.data
    print(f"\nAgent Response:")
    print(f"{response_data.get('response', 'No response')[:200]}...")
    
    deleted_events = response_data.get('events_deleted', [])
    print(f"\nDeleted: {len(deleted_events)} event(s)")
    
    if deleted_events:
        for event in deleted_events:
            print(f"  - {event['title']} (ID: {event['id']})")
    
    # Verify correct event was deleted
    success = False
    if deleted_events:
        deleted_title = deleted_events[0]['title'].lower()
        # Check if any expected keyword is in the deleted event title
        if any(keyword.lower() in deleted_title for keyword in expected_title_keywords):
            success = True
            print(f"\n✓ Correct event deleted!")
        else:
            print(f"\n✗ Wrong event deleted! Expected keywords: {expected_title_keywords}")
    else:
        print(f"\n✗ No events deleted!")
    
    return success


def main():
    """Run realistic deletion tests."""
    print("\n" + "="*80)
    print("REALISTIC EVENT DELETION TESTS")
    print("="*80)
    
    user = User.objects.first()
    if not user:
        print("No user found!")
        return False
    
    print(f"\nUser: {user.username} (timezone: {user.timezone})")
    
    # Clean up any existing test events
    Event.objects.filter(user=user, description__icontains='deletion test').delete()
    
    # Create realistic events
    print("\nCreating realistic events...")
    events = create_realistic_events(user)
    print(f"Created {len(events)} events:")
    for event in events:
        print(f"  - {event.title} ({event.category.name}) at {event.start_time.strftime('%I:%M %p')}")
    
    # Test cases with natural language
    test_cases = [
        {
            'prompt': 'delete dinner with Sarah',
            'expected': ['dinner', 'sarah'],
            'description': 'Delete specific social event'
        },
        {
            'prompt': 'cancel my morning run',
            'expected': ['morning', 'run'],
            'description': 'Delete morning exercise'
        },
        {
            'prompt': 'remove the calculus study session',
            'expected': ['calculus', 'study'],
            'description': 'Delete study session'
        },
        {
            'prompt': 'delete coffee meeting',
            'expected': ['coffee', 'meeting'],
            'description': 'Delete coffee meeting'
        },
        {
            'prompt': 'cancel gym',
            'expected': ['gym', 'workout'],
            'description': 'Delete gym workout'
        },
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"TEST {i}/{len(test_cases)}: {test_case['description']}")
        print(f"{'#'*80}")
        
        success = test_deletion(user, test_case['prompt'], test_case['expected'])
        results.append({
            'test': test_case['description'],
            'prompt': test_case['prompt'],
            'success': success
        })
        
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
    print("\nCleaning up...")
    Event.objects.filter(user=user, description__icontains='deletion test').delete()
    
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
