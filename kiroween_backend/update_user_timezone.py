"""
Update a user's timezone setting.
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def update_timezone(username, new_timezone):
    """Update a user's timezone."""
    
    try:
        user = User.objects.get(username=username)
        old_timezone = user.timezone
        user.timezone = new_timezone
        user.save()
        
        print(f"✓ Updated timezone for user '{username}'")
        print(f"  Old timezone: {old_timezone}")
        print(f"  New timezone: {new_timezone}")
        
    except User.DoesNotExist:
        print(f"✗ User '{username}' not found")
        print("\nAvailable users:")
        for u in User.objects.all():
            print(f"  - {u.username} (current timezone: {u.timezone})")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python update_user_timezone.py <username> <timezone>")
        print("\nExample: python update_user_timezone.py ragib_test1 Asia/Dhaka")
        print("\nAvailable users:")
        for u in User.objects.all():
            print(f"  - {u.username} (current timezone: {u.timezone})")
    else:
        username = sys.argv[1]
        timezone = sys.argv[2]
        update_timezone(username, timezone)
