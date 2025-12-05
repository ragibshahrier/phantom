#!/usr/bin/env python
"""
Check what events exist in the database.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from scheduler.models import Event, User

print("\n" + "="*60)
print("EVENTS IN DATABASE")
print("="*60)

events = Event.objects.all().order_by('-created_at')

if events.count() == 0:
    print("\n✗ No events found in database!")
else:
    print(f"\n✓ Found {events.count()} event(s):\n")
    for event in events:
        print(f"ID: {event.id}")
        print(f"User: {event.user.username}")
        print(f"Title: {event.title}")
        print(f"Category: {event.category.name}")
        print(f"Start: {event.start_time}")
        print(f"End: {event.end_time}")
        print(f"Created: {event.created_at}")
        print("-" * 60)

print("\n" + "="*60)
print("USERS IN DATABASE")
print("="*60)

users = User.objects.all()
for user in users:
    event_count = Event.objects.filter(user=user).count()
    print(f"User: {user.username} (ID: {user.id}) - {event_count} events")

print("\n" + "="*60)
