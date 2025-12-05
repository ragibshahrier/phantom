from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, BlacklistedToken, Category, Event, ConversationHistory, SchedulingLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ('username', 'email', 'name', 'timezone', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'timezone')
    search_fields = ('username', 'email', 'name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Scheduling Preferences', {
            'fields': ('name', 'timezone', 'default_event_duration', 'google_calendar_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    """Admin configuration for BlacklistedToken model."""
    list_display = ('user', 'blacklisted_at', 'expires_at', 'token_preview')
    list_filter = ('blacklisted_at', 'expires_at')
    search_fields = ('user__username', 'token')
    ordering = ('-blacklisted_at',)
    readonly_fields = ('token', 'user', 'blacklisted_at', 'expires_at')
    
    def token_preview(self, obj):
        """Show first 20 characters of token."""
        return f"{obj.token[:20]}..." if len(obj.token) > 20 else obj.token
    token_preview.short_description = 'Token Preview'
    
    def has_add_permission(self, request):
        """Disable manual token creation."""
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ('name', 'priority_level', 'color', 'color_preview')
    list_filter = ('priority_level',)
    search_fields = ('name', 'description')
    ordering = ('-priority_level',)
    
    def color_preview(self, obj):
        """Show color preview."""
        return f'<div style="width: 20px; height: 20px; background-color: {obj.color}; border: 1px solid #ccc;"></div>'
    color_preview.short_description = 'Color'
    color_preview.allow_tags = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for Event model."""
    list_display = ('title', 'user', 'category', 'start_time', 'end_time', 'is_flexible', 'is_completed')
    list_filter = ('category', 'is_flexible', 'is_completed', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-start_time',)
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time', 'is_flexible', 'is_completed')
        }),
        ('Integration', {
            'fields': ('google_calendar_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for ConversationHistory model."""
    list_display = ('user', 'message_preview', 'intent_detected', 'timestamp')
    list_filter = ('intent_detected', 'timestamp')
    search_fields = ('user__username', 'message', 'response')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'message', 'response', 'intent_detected', 'timestamp')
    
    def message_preview(self, obj):
        """Show first 50 characters of message."""
        return f"{obj.message[:50]}..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
    
    def has_add_permission(self, request):
        """Disable manual conversation creation."""
        return False


@admin.register(SchedulingLog)
class SchedulingLogAdmin(admin.ModelAdmin):
    """Admin configuration for SchedulingLog model."""
    list_display = ('user', 'action', 'event', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'action', 'event', 'details', 'timestamp')
    
    def has_add_permission(self, request):
        """Disable manual log creation."""
        return False
