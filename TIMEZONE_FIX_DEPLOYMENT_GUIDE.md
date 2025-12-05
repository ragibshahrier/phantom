# Timezone Fix - Deployment Guide

## ⚠️ IMPORTANT: Server Restart Required

The timezone fix has been implemented in the code, but **you MUST restart your backend server** for the changes to take effect.

## Why Restart is Needed

Python/Django loads modules into memory when the server starts. Changes to `.py` files are not automatically reloaded unless you:
1. Restart the server, OR
2. Have auto-reload enabled (which may not catch all changes)

## How to Restart

### If using `python manage.py runserver`:
1. Stop the server (Ctrl+C in the terminal)
2. Start it again: `python manage.py runserver`

### If using a process manager:
1. Stop the process
2. Start it again

## Verification Steps

After restarting the server:

1. **Delete all old events** (they were created with the wrong timezone):
   ```bash
   python manage.py shell -c "from scheduler.models import Event, User; u = User.objects.first(); Event.objects.filter(user=u).delete(); print('All events deleted')"
   ```

2. **Test the parser** (should show correct timezone):
   ```bash
   python verify_timezone_fix.py
   ```
   Expected output:
   ```
   ✓ Parser is working correctly!
     8pm in Asia/Dhaka = 14:00 UTC
   ```

3. **Create a new event via chat**:
   - In the frontend, send: "schedule dinner at 8pm"
   - Check the timeline - it should show 8:00 PM

4. **Verify in admin panel**:
   - Go to Django admin
   - Check the event's start_time
   - It should show 14:00 (2pm UTC, which is 8pm in Dhaka)

## Why NOT to Subtract 6 Hours

Manually subtracting 6 hours is a **bad solution** because:

1. **Hardcoded for one timezone**: Only works for UTC+6 (Asia/Dhaka)
2. **Breaks for other users**: Users in different timezones will see wrong times
3. **Daylight Saving Time**: Won't handle DST changes
4. **Not maintainable**: Future developers won't understand why 6 hours is subtracted
5. **Django already handles this**: Django's timezone system is designed to do this automatically

## The Correct Solution (Already Implemented)

The fix I implemented:
1. ✅ Parser converts reference time from UTC to user's timezone
2. ✅ Parser creates datetime in user's timezone (e.g., 20:00+06:00)
3. ✅ Django automatically converts to UTC for storage (20:00+06:00 → 14:00 UTC)
4. ✅ API returns UTC time with 'Z' suffix (14:00Z)
5. ✅ Frontend's JavaScript automatically converts to local timezone (14:00 UTC → 20:00 Dhaka)

## Current Status

✅ Parser code is fixed
✅ User timezone is set to Asia/Dhaka
✅ Tests verify correct behavior
⚠️ **Backend server needs restart**
⚠️ **Old events need to be deleted**

## Next Steps

1. **Restart your backend server**
2. **Delete old events** (created before the fix)
3. **Test with a new event**: "schedule dinner at 8pm"
4. **Verify it shows 8pm in the frontend**

If you still see issues after restarting, please let me know and I'll investigate further.
