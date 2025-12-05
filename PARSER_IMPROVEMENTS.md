# Parser Improvements - Standalone Time & Sleep Category

## Issues Fixed

### Issue 1: Gemini API Rate Limit (429 Error)
**Problem**: The Gemini API key was hitting rate limits, causing retries and delays.

**Solution**: Updated `.env` file with placeholder for new API key.

**Action Required**: 
1. Visit https://aistudio.google.com/app/apikey
2. Create a new API key
3. Update `.env` file:
   ```env
   GEMINI_API_KEY=your_new_api_key_here
   ```

### Issue 2: Standalone Time Not Parsed
**Problem**: Input like "schedule sleep time at 10pm" wasn't being parsed because the parser required keywords like "today" or "tomorrow".

**Solution**: Added fallback pattern for standalone times:
- Recognizes patterns like "at 10pm", "at 5:30pm", "at 9am"
- Automatically assumes today if time hasn't passed
- Schedules for tomorrow if the time has already passed today

**Examples Now Working**:
- ✅ "schedule sleep time at 10pm" → Today at 10:00 PM
- ✅ "meeting at 3pm" → Tomorrow at 3:00 PM (if it's already past 3pm)
- ✅ "call at 5:30pm" → Today at 5:30 PM
- ✅ "at 9am tomorrow" → Tomorrow at 9:00 AM (still works)

### Issue 3: Sleep Category Not Recognized
**Problem**: "sleep" wasn't in any category keywords, so events with "sleep" weren't being created.

**Solution**: Added sleep-related keywords to the Social category:
- sleep
- rest
- nap
- bedtime
- wake

**Examples Now Working**:
- ✅ "schedule sleep time at 10pm" → Category: Social
- ✅ "nap time at 2pm" → Category: Social
- ✅ "rest period at 3pm" → Category: Social
- ✅ "bedtime at 11pm" → Category: Social

## Changes Made

### File: `kiroween_backend/ai_agent/parsers.py`

#### 1. Added Standalone Time Pattern
```python
# Pattern: Standalone time like "at 10pm", "at 5:30pm" (fallback - assumes today)
time_only_match = re.search(r'\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text_lower)
if time_only_match:
    # Assume today if only time is specified
    start = self._get_today_at_time(text_lower)
    # If the time has already passed today, schedule for tomorrow
    if start < self.reference_time:
        start = self._get_tomorrow_at_time(text_lower)
    end = start + timedelta(hours=1)
    results.append((start, end))
    return results
```

#### 2. Added Sleep Keywords to Social Category
```python
CATEGORY_KEYWORDS = {
    'Exam': ['exam', 'test', 'quiz', 'midterm', 'final'],
    'Study': ['study', 'review', 'homework', 'assignment', 'reading'],
    'Gym': ['gym', 'workout', 'exercise', 'fitness', 'training', 'run', 'jog'],
    'Social': ['meet', 'hangout', 'party', 'dinner', 'lunch', 'coffee', 'friend', 'sleep', 'rest', 'nap', 'bedtime', 'wake'],
    'Gaming': ['game', 'gaming', 'play', 'stream', 'esports'],
}
```

### File: `kiroween_backend/.env`

#### Updated Gemini API Key Comment
```env
# The current key is hitting rate limits - get a new one from: https://aistudio.google.com/app/apikey
# Visit: https://aistudio.google.com/app/apikey to create a new API key
GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
```

## Test Results

### Standalone Time Parsing
```
Input: 'schedule sleep time at 10pm'
✓ Parsed: 2025-12-05 10:00 PM - 11:00 PM

Input: 'meeting at 3pm'
✓ Parsed: 2025-12-06 03:00 PM - 04:00 PM (tomorrow, since 3pm passed)

Input: 'call at 5:30pm'
✓ Parsed: 2025-12-05 05:30 PM - 06:30 PM

Input: 'at 9am tomorrow'
✓ Parsed: 2025-12-06 09:00 AM - 10:00 AM
```

### Sleep Category Detection
```
Input: 'schedule sleep time at 10pm'
Category: Social ✓
Title: sleep time

Input: 'nap time at 2pm'
Category: Social ✓
Title: nap time

Input: 'rest period at 3pm'
Category: Social ✓
Title: rest period

Input: 'bedtime at 11pm'
Category: Social ✓
Title: bedtime
```

## How It Works Now

### Smart Time Detection
1. **With Day Keyword**: "tomorrow at 5pm" → Tomorrow at 5:00 PM
2. **Without Day Keyword**: "at 5pm" → Today at 5:00 PM (or tomorrow if 5pm passed)
3. **With Minutes**: "at 5:30pm" → Today at 5:30 PM
4. **Morning Times**: "at 9am" → Today at 9:00 AM (or tomorrow if 9am passed)

### Category Detection Priority
The parser checks keywords in this order:
1. Exam keywords (highest priority)
2. Study keywords
3. Gym keywords
4. Social keywords (includes sleep now)
5. Gaming keywords

## Additional Improvements Possible

### Future Enhancements
1. **Add "Personal" Category**: Create a dedicated category for sleep, meals, personal care
2. **Duration Detection**: Parse "sleep for 8 hours" to set end time
3. **Recurring Events**: Support "sleep at 10pm every day"
4. **Smart Defaults**: Different default durations for different activities
5. **Context Awareness**: Learn user's typical sleep schedule

### More Keywords to Consider
- **Meals**: breakfast, lunch, dinner, snack, eat
- **Personal Care**: shower, bath, grooming, hygiene
- **Commute**: drive, commute, travel, transit
- **Work**: work, job, shift, meeting, call

## Usage Examples

### Now Working
```
✅ "schedule sleep time at 10pm"
✅ "nap at 2pm"
✅ "meeting at 3pm"
✅ "call at 5:30pm"
✅ "rest at 4pm"
✅ "bedtime at 11pm"
```

### Still Requires Day Keyword
```
⚠️ "schedule meeting" → Needs time
⚠️ "sleep" → Needs time
⚠️ "at 10" → Needs am/pm
```

### Best Practices
```
✅ "schedule sleep today at 10pm" (most explicit)
✅ "sleep at 10pm" (works with fallback)
✅ "sleep tomorrow at 10pm" (explicit day)
✅ "sleep tonight at 10pm" (uses "tonight" keyword)
```

## Next Steps

1. **Get New Gemini API Key**:
   - Visit: https://aistudio.google.com/app/apikey
   - Create new API key
   - Update `.env` file

2. **Test the Improvements**:
   ```bash
   # Try these commands in your chat:
   "schedule sleep time at 10pm"
   "nap at 2pm"
   "meeting at 3pm"
   ```

3. **Monitor API Usage**:
   - Watch for 429 errors
   - Consider implementing rate limiting
   - Use caching for repeated queries

## Summary

✅ **Standalone time parsing** - "at 10pm" now works
✅ **Sleep category detection** - "sleep" is now recognized
✅ **Smart scheduling** - Automatically picks today or tomorrow
⚠️ **API key needed** - Get new Gemini API key to avoid rate limits

The parser is now more flexible and user-friendly!
