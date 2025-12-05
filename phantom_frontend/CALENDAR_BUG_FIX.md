# Calendar Date Selection Bug Fix

## Problem

When clicking on a date in the calendar, the application was selecting the previous date instead of the clicked date.

## Root Cause

The issue was caused by timezone handling when converting between Date objects and date strings:

### Issue 1: Date String to Date Object Conversion
```typescript
// BEFORE (Problematic)
const newDate = new Date(dateStr + 'T00:00:00');
```

When creating a Date object from a string like `"2024-12-05T00:00:00"`, JavaScript interprets it in the **local timezone**. Depending on your timezone offset, this could result in the date being interpreted as the previous day.

For example:
- If you're in a timezone ahead of UTC (e.g., UTC+8)
- Clicking on December 5th creates: `"2024-12-05T00:00:00"`
- JavaScript interprets this as December 5th at midnight in your local time
- But when converted back to UTC for comparison, it might become December 4th

### Issue 2: Date Object to String Conversion
```typescript
// BEFORE (Problematic)
const selectedDateStr = selectedDate.toISOString().split('T')[0];
```

The `toISOString()` method returns the date in **UTC timezone**, which can cause the date to shift by one day if your local timezone is different from UTC.

For example:
- Local date: December 5th, 2024 at 00:00:00 (your timezone)
- `toISOString()` converts to UTC: might become December 4th, 2024 at 16:00:00 UTC
- Splitting by 'T' gives: `"2024-12-04"` (wrong date!)

## Solution

### Fix 1: Parse Date Components Explicitly
```typescript
// AFTER (Fixed)
const parts = dateStr.split('-');
const year = parseInt(parts[0] || '0', 10);
const month = parseInt(parts[1] || '1', 10);
const day = parseInt(parts[2] || '1', 10);
const newDate = new Date(year, month - 1, day, 0, 0, 0, 0);
```

By parsing the date components and using the `Date` constructor with individual parameters, we ensure the date is created in the **local timezone** without any conversion issues.

### Fix 2: Format Date in Local Timezone
```typescript
// AFTER (Fixed)
const formatDateLocal = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const selectedDateStr = selectedDate ? formatDateLocal(selectedDate) : todayStr;
```

This helper function formats the date using local timezone methods (`getFullYear()`, `getMonth()`, `getDate()`) instead of UTC methods, ensuring the date string matches the user's local date.

## Files Modified

1. **`phantom_frontend/pages/SeanceRoom.tsx`**
   - Added `formatDateLocal()` helper function
   - Updated date string to Date object conversion in `onSelectDate` callback
   - Updated `selectedDateStr` calculation to use local timezone

## Testing

To verify the fix:

1. **Test in different timezones:**
   - Change your system timezone
   - Click on various dates in the calendar
   - Verify the correct date is selected

2. **Test edge cases:**
   - Click on the 1st of the month
   - Click on the last day of the month
   - Click on today's date
   - Click on dates in different months

3. **Test date filtering:**
   - Select a date with events
   - Verify the correct events are displayed
   - Verify the date shown in the header matches the selected date

## Expected Behavior

After the fix:
- ✅ Clicking on December 5th selects December 5th (not December 4th)
- ✅ The selected date matches the clicked date in all timezones
- ✅ Events are filtered correctly for the selected date
- ✅ The "Return to Present" button works correctly
- ✅ Month navigation maintains the correct date

## Technical Details

### Why This Matters

JavaScript's Date handling can be tricky:

1. **ISO String Format (`toISOString()`)**: Always returns UTC time
2. **Date Constructor with String**: Interprets based on format and timezone
3. **Date Constructor with Parameters**: Creates date in local timezone

### Best Practices

When working with dates in JavaScript:

1. **For display/comparison**: Use local timezone methods
   ```typescript
   date.getFullYear()
   date.getMonth()
   date.getDate()
   ```

2. **For API communication**: Use ISO strings
   ```typescript
   date.toISOString()
   ```

3. **For date-only operations**: Parse components explicitly
   ```typescript
   new Date(year, month, day, 0, 0, 0, 0)
   ```

4. **Avoid**: Mixing UTC and local timezone operations

## Related Issues

This fix also resolves:
- Date comparison issues in event filtering
- "Return to Present" button selecting wrong date
- Month navigation date inconsistencies

## Prevention

To prevent similar issues in the future:

1. Always use local timezone methods for UI date operations
2. Create helper functions for common date operations
3. Test in multiple timezones during development
4. Document timezone handling in code comments

---

**Fixed:** December 2024
**Impact:** High (affects all calendar interactions)
**Status:** ✅ Resolved
