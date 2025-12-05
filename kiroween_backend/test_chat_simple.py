#!/usr/bin/env python
"""
Simple test to debug chat API event creation.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from django.contrib.auth import get_user_model
from scheduler.models import Event, Category
from ai_agent.parsers import TemporalExpressionParser, TaskCategoryExtractor
from django.utils import timezone

User = get_user_model()

def test_parsing():
    """Test if parsing works."""
    print("\n" + "="*60)
    print("Testing Parsers")
    print("="*60)
    
    user_input = "Schedule a study session tomorrow at 2pm"
    print(f"Input: {user_input}")
    
    # Test temporal parser
    temporal_parser = TemporalExpressionParser(
        user_timezone='UTC',
        reference_time=timezone.now()
    )
    temporal_results = temporal_parser.parse(user_input)
    
    print(f"\nTemporal results: {len(temporal_results)} found")
    for start, end in temporal_results:
        print(f"  Start: {start}")
        print(f"  End: {end}")
    
    # Test category extractor
    category_extractor = TaskCategoryExtractor()
    category = category_extractor.extract_category(user_input)
    task_title = category_extractor.extract_task_title(user_input)
    
    print(f"\nCategory: {category}")
    print(f"Task title: {task_title}")
    
    # Check if category exists in database
    if category:
        try:
            cat_obj = Category.objects.get(name=category)
            print(f"✓ Category '{category}' exists in database (ID: {cat_obj.id})")
        except Category.DoesNotExist:
            print(f"✗ Category '{category}' NOT FOUND in database!")
            print("\nAvailable categories:")
            for cat in Category.objects.all():
                print(f"  - {cat.name} (ID: {cat.id})")
    
    return temporal_results, category, task_title

def test_event_creation():
    """Test creating an event directly."""
    print("\n" + "="*60)
    print("Testing Event Creation")
    print("="*60)
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={
            'name': 'Test User',
            'email': 'test@example.com',
            'timezone': 'UTC'
        }
    )
    
    temporal_results, category, task_title = test_parsing()
    
    if not (temporal_results and category and task_title):
        print("\n✗ Missing required data!")
        return
    
    try:
        category_obj = Category.objects.get(name=category)
        start_time, end_time = temporal_results[0]
        
        print(f"\nCreating event...")
        print(f"  User: {user.username}")
        print(f"  Title: {task_title}")
        print(f"  Category: {category_obj.name}")
        print(f"  Start: {start_time}")
        print(f"  End: {end_time}")
        
        event = Event.objects.create(
            user=user,
            title=task_title,
            description="Test event",
            category=category_obj,
            start_time=start_time,
            end_time=end_time,
            is_flexible=True
        )
        
        print(f"\n✓ Event created successfully!")
        print(f"  Event ID: {event.id}")
        print(f"  Event title: {event.title}")
        
        # Verify it's in the database
        db_event = Event.objects.get(id=event.id)
        print(f"✓ Event verified in database: {db_event.title}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_event_creation()
