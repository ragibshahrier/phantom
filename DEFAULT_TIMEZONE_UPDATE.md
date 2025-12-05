# Default Timezone Update: Asia/Dhaka

## Summary
Changed the default timezone for new users from `UTC` to `Asia/Dhaka` to ensure all new users in Bangladesh automatically get the correct timezone setting.

## Changes Made

### 1. Model Update
**File**: `kiroween_backend/scheduler/models.py`

Changed the User model's timezone field default value:
```python
# Before
timezone = models.CharField(max_length=50, default='UTC')

# After
timezone = models.CharField(max_length=50, default='Asia/Dhaka')
```

### 2. Database Migration
Created and applied migration:
```bash
python manage.py makemigrations --name change_default_timezone_to_asia_dhaka
python manage.py migrate
```

Migration file: `scheduler/migrations/0006_change_default_timezone_to_asia_dhaka.py`

## Impact

### New Users
- All new users created after this change will automatically have `Asia/Dhaka` as their timezone
- This applies to:
  - User registration via API (`/api/register/`)
  - User creation via Django admin
  - User creation via `create_user()` method

### Existing Users
- Existing users are **NOT affected** by this change
- Their timezone settings remain as they were
- To update existing users, use the utility script:
  ```bash
  cd kiroween_backend
  .\venv\Scripts\python.exe update_user_timezone.py <username> Asia/Dhaka
  ```

## Testing

Both tests passed successfully:

### Test 1: Direct User Creation
```
✓ SUCCESS: New user has correct default timezone (Asia/Dhaka)
```

### Test 2: Registration Endpoint
```
✓ SUCCESS: Registered user has correct default timezone (Asia/Dhaka)
```

## Benefits

1. **Correct Time Display**: Events scheduled at "5pm" will now correctly display at 5pm Bangladesh time
2. **Better User Experience**: No need for users to manually update their timezone
3. **Reduced Support Issues**: Eliminates timezone-related confusion for new users
4. **Localized by Default**: Application is now properly localized for Bangladesh users

## Verification

To verify the default timezone is working:

1. **Create a new user** via registration or admin panel
2. **Check their timezone** - it should be `Asia/Dhaka`
3. **Schedule an event** at a specific time (e.g., "5pm")
4. **Verify the time** displays correctly in Bangladesh time

## Utility Scripts

### Check User Timezones
```bash
cd kiroween_backend
.\venv\Scripts\python.exe check_recent_events.py
```

### Update Existing User Timezone
```bash
cd kiroween_backend
.\venv\Scripts\python.exe update_user_timezone.py <username> Asia/Dhaka
```

## Notes

- The timezone string `Asia/Dhaka` is the standard IANA timezone identifier for Bangladesh
- This is the same as `Asia/Dhaka` (UTC+6:00)
- Django stores all datetimes in UTC in the database and converts them based on the user's timezone setting
- The API returns times in UTC (ISO 8601 format), and the frontend should convert them to the user's local timezone

## Rollback (if needed)

If you need to revert this change:

1. Edit `scheduler/models.py` and change back to `default='UTC'`
2. Create a new migration:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

However, this is **not recommended** as it would affect new users going forward.
