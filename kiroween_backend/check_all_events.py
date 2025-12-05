import django
import os
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phantom.settings')
django.setup()

from scheduler.models import Event, User

u = User.objects.first()
events = Event.objects.filter(user=u).order_by('-created_at')[:10]

print(f'User: {u.username} (timezone: {u.timezone})')
print(f'Found {events.count()} events:\n')

dhaka_tz = pytz.timezone('Asia/Dhaka')

for e in events:
    dhaka_time = e.start_time.astimezone(dhaka_tz)
    print(f'{e.title}:')
    print(f'  DB (UTC): {e.start_time}')
    print(f'  Dhaka: {dhaka_time}')
    print(f'  Hour in Dhaka: {dhaka_time.hour}:00')
    print()
