# Timezone Fix for Event Scheduling

## Problem
When users scheduled events via chat (e.g., "schedule dinner at 11pm"), the events were being displayed at incorrect times in the frontend (e.g., showing as 5am instead of 11pm). This was a 6-hour difference.

## Root Cause
The issue had two parts:

1. **User Timezone Not Set**: The user's timezone in the database was set to 'UTC' instead of their actual timezone (Asia/Dhaka, which is UTC+6).

2. **Timezone Handling in Parser**: The `TemporalExpressionParser` was creating datetime objects, but the timezone localization wasn't being done correctly. When parsing times like "11pm", the parser needed to:
   - Parse the time in the user's local timezone (23:00 Asia/Dhaka)
   - Create a timezone-aware datetime object
   - Let Django automatically convert to UTC for storage (23:00+06:00 = 17:00 UTC)
   - Let the frontend convert back to local time for display

## Solution

### 1. Fixed Parser Timezone Handling
Updated `kiroween_backend/ai_agent/parsers.py`:

- Modified `_get_time_of_day()` to return a tuple of (hour, minute) instead of just hour
- Updated all datetime creation methods to:
  1. Create a naive datetime first (without timezone)
  2. Use `user_timezone.localize()` to properly attach the user's timezone
  3. This ensures Django receives timezone-aware datetimes that it can correctly convert to UTC

### 2. Updated User Timezone
Changed the user's timezone from 'UTC' to 'Asia/Dhaka' in the database.

## How It Works Now

1. **User Input**: "schedule dinner at 11pm"
2. **Parser**: Creates datetime with 23:00 in Asia/Dhaka timezone (23:00+06:00)
3. **Django Storage**: Converts to UTC and stores as 17:00 UTC
4. **API Response**: Returns "2024-12-05T17:00:00Z" (UTC)
5. **Frontend**: JavaScript's `new Date()` automatically converts to local timezone
6. **Display**: Shows as 11:00 PM in the user's local timezone

## Testing
To test the fix:
```bash
# Check user timezone
python manage.py shell -c "from scheduler.models import User; u = User.objects.first(); print(f'Timezone: {u.timezone}')"

# Test parser
python manage.py shell -c "from ai_agent.parsers import TemporalExpressionParser; from django.utils import timezone; parser = TemporalExpressionParser(user_timezone='Asia/Dhaka', reference_time=timezone.now()); results = parser.parse('schedule dinner at 11pm tomorrow'); [print(f'Start: {start}') for start, end in results]"
```

## Future Improvements
- Add timezone detection from the frontend (using JavaScript's `Intl.DateTimeFormat().resolvedOptions().timeZone`)
- Allow users to set their timezone in preferences
- Add timezone validation when creating/updating user accounts
