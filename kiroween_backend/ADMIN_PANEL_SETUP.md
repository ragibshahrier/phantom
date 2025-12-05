# Django Admin Panel Configuration

## Overview
All models from the Phantom Scheduler application have been registered with the Django admin panel with custom configurations for better management and visibility.

## Registered Models

### Scheduler App (`scheduler/admin.py`)

#### 1. **User** (`UserAdmin`)
- **List Display**: username, email, name, timezone, is_staff, created_at
- **Filters**: is_staff, is_superuser, is_active, timezone
- **Search**: username, email, name
- **Features**:
  - Extended from Django's built-in UserAdmin
  - Custom fieldsets for scheduling preferences
  - Readonly timestamps
  - Ordered by creation date (newest first)

#### 2. **BlacklistedToken** (`BlacklistedTokenAdmin`)
- **List Display**: user, blacklisted_at, expires_at, token_preview
- **Filters**: blacklisted_at, expires_at
- **Search**: user username, token
- **Features**:
  - Token preview (first 20 characters)
  - All fields readonly (audit trail)
  - Manual creation disabled
  - Ordered by blacklist date (newest first)

#### 3. **Category** (`CategoryAdmin`)
- **List Display**: name, priority_level, color, color_preview
- **Filters**: priority_level
- **Search**: name, description
- **Features**:
  - Visual color preview in admin list
  - Ordered by priority (highest first)
  - Editable for customization

#### 4. **Event** (`EventAdmin`)
- **List Display**: title, user, category, start_time, end_time, is_flexible, is_completed
- **Filters**: category, is_flexible, is_completed, created_at
- **Search**: title, description, user username
- **Features**:
  - Date hierarchy by start_time
  - Organized fieldsets (Basic, Scheduling, Integration, Timestamps)
  - Readonly timestamps
  - Ordered by start time (newest first)

#### 5. **ConversationHistory** (`ConversationHistoryAdmin`)
- **List Display**: user, message_preview, intent_detected, timestamp
- **Filters**: intent_detected, timestamp
- **Search**: user username, message, response
- **Features**:
  - Message preview (first 50 characters)
  - Date hierarchy by timestamp
  - All fields readonly (audit trail)
  - Manual creation disabled
  - Ordered by timestamp (newest first)

#### 6. **SchedulingLog** (`SchedulingLogAdmin`)
- **List Display**: user, action, event, timestamp
- **Filters**: action, timestamp
- **Search**: user username, action, details
- **Features**:
  - Date hierarchy by timestamp
  - All fields readonly (audit trail)
  - Manual creation disabled
  - Ordered by timestamp (newest first)

### AI Agent App (`ai_agent/admin.py`)
- No models defined in this app
- Uses ConversationHistory from scheduler app

### Integrations App (`integrations/admin.py`)
- No models defined in this app
- Uses User.google_calendar_token from scheduler app

## Accessing the Admin Panel

1. **Create a superuser** (if not already created):
   ```bash
   cd kiroween_backend
   python manage.py createsuperuser
   ```

2. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

3. **Access the admin panel**:
   - URL: http://localhost:8000/admin/
   - Login with your superuser credentials

## Admin Panel Features

### Security Features
- **Audit Trails**: BlacklistedToken, ConversationHistory, and SchedulingLog are readonly
- **No Manual Creation**: Audit models cannot be manually created through admin
- **Token Preview**: Sensitive tokens show only preview, not full value

### User Experience
- **Visual Indicators**: Color preview for categories
- **Message Previews**: Long text fields show truncated previews
- **Date Hierarchies**: Easy navigation through time-based data
- **Smart Filtering**: Multiple filter options for each model
- **Search Functionality**: Quick search across relevant fields

### Data Management
- **Bulk Actions**: Standard Django bulk operations available
- **Export**: Can export data using Django admin actions
- **Inline Editing**: Quick edit from list view where appropriate
- **Organized Fieldsets**: Logical grouping of related fields

## Customization

To further customize the admin panel, edit `kiroween_backend/scheduler/admin.py`:

```python
# Example: Add custom action
@admin.action(description='Mark events as completed')
def mark_completed(modeladmin, request, queryset):
    queryset.update(is_completed=True)

# Add to EventAdmin
class EventAdmin(admin.ModelAdmin):
    actions = [mark_completed]
    # ... rest of configuration
```

## Best Practices

1. **Don't modify audit logs** through admin (they're readonly for a reason)
2. **Use filters and search** to find data quickly
3. **Check date hierarchies** for time-based analysis
4. **Review conversation history** to understand user interactions
5. **Monitor scheduling logs** for system activity

## Troubleshooting

### Admin panel not showing models
```bash
# Make sure migrations are applied
python manage.py migrate

# Restart the server
python manage.py runserver
```

### Permission errors
- Ensure you're logged in as a superuser
- Check user permissions in User admin

### Custom fields not showing
- Check fieldsets configuration in admin.py
- Verify model has the field defined
