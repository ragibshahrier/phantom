"""
Check recent events in the database to see their actual stored times.
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from scheduler.models import Event
from django.contrib.auth import get_user_model
import pytz

User = get_user_model()

def check_recent_events():
    """Check the most recent events and their timezone information."""
    
    print("=" * 80)
    print("Recent Events in Database")
    print("=" * 80)
    
    # Get all users
    users = User.objects.all()
    
    for user in users:
        print(f"\nUser: {user.username}")
        print(f"Timezone: {user.timezone}")
        
        # Get recent events for this user
        events = Event.objects.filter(user=user).order_by('-created_at')[:5]
        
        if not events:
            print("  No events found")
            continue
        
        user_tz = pytz.timezone(user.timezone)
        
        for event in events:
            print(f"\n  Event ID: {event.id}")
            print(f"  Title: {event.title}")
            print(f"  Created: {event.created_at}")
            print(f"  Start Time (DB/UTC): {event.start_time}")
            print(f"  Start Time TZ: {event.start_time.tzinfo}")
            
            # Convert to user's timezone
            start_in_user_tz = event.start_time.astimezone(user_tz)
            print(f"  Start Time (User TZ): {start_in_user_tz}")
            print(f"  Hour in User TZ: {start_in_user_tz.hour}:00")
            
            # Show what the API would return
            print(f"  API Response (ISO): {event.start_time.isoformat()}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    check_recent_events()
