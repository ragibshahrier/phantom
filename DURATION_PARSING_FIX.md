# Duration Parsing Fix

## Issue Found
The time extraction regex was too greedy and would match duration numbers (like "30" from "30 minute") instead of the actual time (like "10am").

### Example of the Bug:
```
Input: "30 minute meeting at 10am"
Bug: Extracted "30" as hour → ValueError: hour must be in 0..23
Fix: Now correctly extracts "10am" as the time
```

## Solution
Updated the `_get_time_of_day()` method to require am/pm suffix for time extraction, preventing it from matching duration numbers.

### Before:
```python
time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?', text)
```
This would match ANY number, including duration numbers.

### After:
```python
time_match = re.search(r'(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)', text)
```
This REQUIRES am/pm, so it only matches actual times.

## Test Results

All 10 test cases now pass:

```
✅ "study session today at 2pm for 2 hours" → 2:00 PM - 4:00 PM (2 hours)
✅ "meeting tomorrow at 3pm for 30 minutes" → 3:00 PM - 3:30 PM (30 min)
✅ "gym at 5pm for 1.5 hours" → 5:00 PM - 6:30 PM (1.5 hours)
✅ "sleep at 10pm for 8 hours" → 10:00 PM - 6:00 AM (8 hours)
✅ "call at 9am for 45 minutes" → 9:00 AM - 9:45 AM (45 min)
✅ "workout today at 6am for 90 minutes" → 6:00 AM - 7:30 AM (90 min)
✅ "study at 3pm" → 3:00 PM - 4:00 PM (1 hour default)
✅ "2 hour study session at 3pm" → 3:00 PM - 5:00 PM (2 hours)
✅ "30 minute meeting at 10am" → 10:00 AM - 10:30 AM (30 min) ← FIXED!
✅ "schedule sleep time at 10pm for 8 hours" → 10:00 PM - 6:00 AM (8 hours)
```

## What Works Now

### Duration Formats:
- ✅ "for X hours" → "for 2 hours", "for 1.5 hours"
- ✅ "for X minutes" → "for 30 minutes", "for 45 minutes"
- ✅ "X hour [activity]" → "2 hour study session"
- ✅ "X minute [activity]" → "30 minute meeting"
- ✅ No duration → defaults to 1 hour

### Time Formats:
- ✅ "at 10am", "at 3pm"
- ✅ "at 5:30pm", "at 9:15am"
- ✅ "today at 2pm", "tomorrow at 3pm"
- ✅ Standalone: "at 10pm" (assumes today/tomorrow)

### Combined:
- ✅ "30 minute meeting at 10am" (duration before time)
- ✅ "meeting at 10am for 30 minutes" (duration after time)
- ✅ "2 hour study session at 3pm" (duration in description)

## Deployment Note

This fix is ready for deployment. Make sure to:

1. Commit the changes:
   ```bash
   git add kiroween_backend/ai_agent/parsers.py
   git commit -m "Fix: Duration parsing - prevent time extraction from duration numbers"
   git push origin main
   ```

2. Railway will auto-deploy the fix

3. Test on production:
   ```bash
   # Try these in your deployed chat:
   "30 minute meeting at 10am"
   "2 hour study session at 3pm"
   "sleep at 10pm for 8 hours"
   ```

## Summary

✅ **Fixed**: Time extraction no longer confuses duration numbers with times
✅ **Tested**: All 10 test cases pass
✅ **Ready**: For deployment to Railway

Duration parsing is now robust and handles all common input patterns correctly!
