# Duration Parsing Feature

## Problem
The AI agent was creating all events with a fixed 1-hour duration, regardless of what the user specified.

## Solution
Added intelligent duration parsing that extracts duration from natural language input.

## How It Works

### Duration Extraction Patterns

The parser now recognizes these patterns:

1. **"for X hours"**
   - "study session for 2 hours" → 2 hours
   - "meeting for 1.5 hours" → 1.5 hours
   - "gym for 3 hours" → 3 hours

2. **"for X minutes"**
   - "call for 30 minutes" → 30 minutes
   - "meeting for 45 minutes" → 45 minutes
   - "workout for 90 minutes" → 90 minutes (1.5 hours)

3. **"X hour/minute [activity]"**
   - "2 hour study session" → 2 hours
   - "30 minute meeting" → 30 minutes
   - "90 minute workout" → 90 minutes

4. **Default (no duration specified)**
   - "study at 3pm" → 1 hour (default)

### Supported Variations

- **Hours**: hour, hr, hours, hrs
- **Minutes**: minute, min, minutes, mins
- **Decimal hours**: 1.5 hours, 2.5 hours
- **With/without "for"**: "for 2 hours" or "2 hour session"

## Examples

### Input → Output

```
"study session today at 2pm for 2 hours"
→ Start: 2:00 PM
→ End: 4:00 PM
→ Duration: 2 hours ✓

"meeting tomorrow at 3pm for 30 minutes"
→ Start: 3:00 PM
→ End: 3:30 PM
→ Duration: 30 minutes ✓

"gym at 5pm for 1.5 hours"
→ Start: 5:00 PM
→ End: 6:30 PM
→ Duration: 1.5 hours ✓

"sleep at 10pm for 8 hours"
→ Start: 10:00 PM
→ End: 6:00 AM (next day)
→ Duration: 8 hours ✓

"call at 9am for 45 minutes"
→ Start: 9:00 AM
→ End: 9:45 AM
→ Duration: 45 minutes ✓

"workout today at 6am for 90 minutes"
→ Start: 6:00 AM
→ End: 7:30 AM
→ Duration: 90 minutes (1.5 hours) ✓

"study at 3pm"
→ Start: 3:00 PM
→ End: 4:00 PM
→ Duration: 1 hour (default) ✓
```

## Technical Implementation

### New Method: `_extract_duration()`

```python
def _extract_duration(self, text: str) -> timedelta:
    """
    Extract duration from text like "for 2 hours", "for 30 minutes", "2 hour session".
    
    Returns:
        timedelta object representing the duration (defaults to 1 hour if not found)
    """
    text_lower = text.lower()
    
    # Try hours first
    hours_match = re.search(r'(?:for\s+)?(\d+(?:\.\d+)?)\s*(?:hour|hr|hours|hrs)', text_lower)
    if hours_match:
        hours = float(hours_match.group(1))
        return timedelta(hours=hours)
    
    # Try minutes
    minutes_match = re.search(r'(?:for\s+)?(\d+)\s*(?:minute|min|minutes|mins)', text_lower)
    if minutes_match:
        minutes = int(minutes_match.group(1))
        return timedelta(minutes=minutes)
    
    # Default to 1 hour if no duration specified
    return timedelta(hours=1)
```

### Updated All Temporal Patterns

Every temporal pattern now uses the extracted duration:

```python
# Extract duration once for all patterns
duration = self._extract_duration(text_lower)

# Then use it for all patterns
end = start + duration  # Instead of: end = start + timedelta(hours=1)
```

## Benefits

1. **Flexible Duration**: Users can specify any duration they want
2. **Natural Language**: Works with natural phrases like "for 2 hours"
3. **Smart Defaults**: Falls back to 1 hour if no duration specified
4. **Decimal Support**: Handles 1.5 hours, 2.5 hours, etc.
5. **Multiple Units**: Supports both hours and minutes
6. **Consistent**: Works across all temporal patterns (today, tomorrow, weekdays, etc.)

## Use Cases

### Study Sessions
```
"study session tomorrow at 2pm for 3 hours"
→ 2:00 PM - 5:00 PM ✓
```

### Meetings
```
"team meeting at 10am for 45 minutes"
→ 10:00 AM - 10:45 AM ✓
```

### Workouts
```
"gym session at 6am for 90 minutes"
→ 6:00 AM - 7:30 AM ✓
```

### Sleep
```
"sleep at 11pm for 8 hours"
→ 11:00 PM - 7:00 AM ✓
```

### Quick Tasks
```
"call at 3pm for 15 minutes"
→ 3:00 PM - 3:15 PM ✓
```

## Edge Cases Handled

1. **No duration specified**: Defaults to 1 hour
2. **Decimal hours**: 1.5, 2.5, etc. work correctly
3. **Large durations**: 8 hours, 10 hours work fine
4. **Small durations**: 15 minutes, 5 minutes work fine
5. **Overnight events**: Sleep from 10pm for 8 hours correctly ends at 6am next day

## Testing

All test cases passed:

```
✓ 2 hours → 2:00 PM - 4:00 PM
✓ 30 minutes → 3:00 PM - 3:30 PM
✓ 1.5 hours → 5:00 PM - 6:30 PM
✓ 8 hours → 10:00 PM - 6:00 AM (next day)
✓ 45 minutes → 9:00 AM - 9:45 AM
✓ 90 minutes → 6:00 AM - 7:30 AM
✓ No duration → 3:00 PM - 4:00 PM (1 hour default)
```

## Future Enhancements

1. **Duration Ranges**: "2-3 hours", "30-45 minutes"
2. **All Day Events**: "all day meeting"
3. **Until Time**: "study from 2pm until 5pm"
4. **Smart Defaults by Category**:
   - Exams: 2-3 hours default
   - Study: 1-2 hours default
   - Gym: 1 hour default
   - Social: 2 hours default
   - Gaming: 2 hours default

## Summary

✅ **Duration parsing implemented**
✅ **Supports hours and minutes**
✅ **Works with all temporal patterns**
✅ **Smart 1-hour default**
✅ **Natural language friendly**

Users can now specify exactly how long their events should be!
