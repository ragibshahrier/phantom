#!/usr/bin/env python
"""
Comprehensive test for event creation via chat API.
This test will help debug why events aren't being created.
"""
import os
import sys
import django
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from scheduler.models import Event, Category
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def setup_test_data():
    """Create test user and categories."""
    print("\n" + "="*60)
    print("SETUP: Creating test data")
    print("="*60)
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'name': 'Test User',
            'email': 'test@example.com',
            'timezone': 'UTC'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")
    
    # Ensure categories exist
    categories_data = [
        {'name': 'Exam', 'priority_level': 5, 'color': '#FF0000', 'description': 'Exams and tests'},
        {'name': 'Study', 'priority_level': 4, 'color': '#FFA500', 'description': 'Study sessions'},
        {'name': 'Gym', 'priority_level': 3, 'color': '#00FF00', 'description': 'Gym and workouts'},
        {'name': 'Social', 'priority_level': 2, 'color': '#0000FF', 'description': 'Social events'},
        {'name': 'Gaming', 'priority_level': 1, 'color': '#FF00FF', 'description': 'Gaming sessions'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Created category: {category.name}")
        else:
            print(f"✓ Category exists: {category.name}")
    
    return user

def get_auth_token(user):
    """Get JWT token for user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_parsers(user_input):
    """Test the parsers directly."""
    print("\n" + "="*60)
    print("TEST 1: Testing Parsers Directly")
    print("="*60)
    print(f"Input: {user_input}")
    
    from ai_agent.parsers import TemporalExpressionParser, TaskCategoryExtractor
    from django.utils import timezone
    
    # Test temporal parser
    temporal_parser = TemporalExpressionParser(
        user_timezone='UTC',
        reference_time=timezone.now()
    )
    temporal_results = temporal_parser.parse(user_input)
    
    print(f"\nTemporal Results: {len(temporal_results)} time slots found")
    for i, (start, end) in enumerate(temporal_results, 1):
        print(f"  {i}. Start: {start}")
        print(f"     End:   {end}")
    
    # Test category extractor
    category_extractor = TaskCategoryExtractor()
    category = category_extractor.extract_category(user_input)
    task_title = category_extractor.extract_task_title(user_input)
    
    print(f"\nCategory: {category}")
    print(f"Task Title: {task_title}")
    
    # Check if we have all required data
    has_all_data = bool(temporal_results and task_title and category)
    print(f"\nHas all required data: {has_all_data}")
    
    if not has_all_data:
        print("\n⚠ WARNING: Missing required data for event creation!")
        if not temporal_results:
            print("  - No temporal information found")
        if not task_title:
            print("  - No task title extracted")
        if not category:
            print("  - No category detected")
    
    return temporal_results, category, task_title

def test_chat_api(user, user_input):
    """Test the chat API endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Testing Chat API Endpoint")
    print("="*60)
    
    # Get auth token
    token = get_auth_token(user)
    
    # Create client
    client = Client()
    
    # Count events before
    events_before = Event.objects.filter(user=user).count()
    print(f"Events before: {events_before}")
    
    # Make API request
    response = client.post(
        '/api/chat/',
        data=json.dumps({'message': user_input}),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    
    print(f"\nAPI Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data.get('response', 'N/A')}")
        print(f"Intent: {data.get('intent', 'N/A')}")
        print(f"Category: {data.get('category', 'N/A')}")
        print(f"Task Title: {data.get('task_title', 'N/A')}")
        print(f"Temporal Info: {data.get('temporal_info', 'N/A')}")
        print(f"Events Created: {len(data.get('events_created', []))}")
        
        if data.get('events_created'):
            print("\nCreated Events:")
            for event in data['events_created']:
                print(f"  - {event['title']} ({event['start_time']} to {event['end_time']})")
    else:
        print(f"Error: {response.content.decode()}")
    
    # Count events after
    events_after = Event.objects.filter(user=user).count()
    print(f"\nEvents after: {events_after}")
    print(f"Events created: {events_after - events_before}")
    
    return response

def test_direct_event_creation(user, temporal_results, category, task_title):
    """Test creating an event directly."""
    print("\n" + "="*60)
    print("TEST 3: Testing Direct Event Creation")
    print("="*60)
    
    if not (temporal_results and category and task_title):
        print("⚠ Skipping - missing required data")
        return
    
    try:
        category_obj = Category.objects.get(name=category)
        print(f"✓ Found category: {category_obj.name}")
        
        start_time, end_time = temporal_results[0]
        event = Event.objects.create(
            user=user,
            title=task_title,
            description="Test event",
            category=category_obj,
            start_time=start_time,
            end_time=end_time,
            is_flexible=True
        )
        print(f"✓ Created event: {event.title}")
        print(f"  ID: {event.id}")
        print(f"  Start: {event.start_time}")
        print(f"  End: {event.end_time}")
        
        # Clean up
        event.delete()
        print("✓ Cleaned up test event")
        
    except Category.DoesNotExist:
        print(f"✗ Category '{category}' not found in database!")
    except Exception as e:
        print(f"✗ Error creating event: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("EVENT CREATION DIAGNOSTIC TEST")
    print("="*60)
    
    # Setup
    user = setup_test_data()
    
    # Test input
    test_inputs = [
        "Schedule a study session tomorrow at 2pm",
        "Add gym workout next Monday morning",
        "Create exam review on Friday at 3pm",
    ]
    
    for user_input in test_inputs:
        print("\n" + "="*60)
        print(f"TESTING: {user_input}")
        print("="*60)
        
        # Test parsers
        temporal_results, category, task_title = test_parsers(user_input)
        
        # Test API
        test_chat_api(user, user_input)
        
        # Test direct creation
        test_direct_event_creation(user, temporal_results, category, task_title)
        
        print("\n" + "-"*60)
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL DATABASE STATE")
    print("="*60)
    
    total_events = Event.objects.filter(user=user).count()
    print(f"Total events for {user.username}: {total_events}")
    
    if total_events > 0:
        print("\nEvents:")
        for event in Event.objects.filter(user=user).order_by('-created_at')[:10]:
            print(f"  - {event.title} ({event.start_time})")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == '__main__':
    main()
