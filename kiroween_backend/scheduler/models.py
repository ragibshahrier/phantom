"""
Database models for the Phantom scheduler application.
"""
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """
    Extended user model with scheduling preferences.
    """
    name = models.CharField(max_length=150)
    timezone = models.CharField(max_length=50, default='Asia/Dhaka')
    default_event_duration = models.IntegerField(default=60)  # minutes
    google_calendar_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class BlacklistedToken(models.Model):
    """
    Store blacklisted refresh tokens for logout functionality.
    """
    token = models.TextField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Blacklisted token for {self.user.username}"


class Category(models.Model):
    """
    Event categories with priority levels.
    Higher priority_level values indicate more important categories.
    Default categories: Exam(5), Study(4), Gym(3), Social(2), Gaming(1)
    """
    name = models.CharField(max_length=50, unique=True)
    priority_level = models.IntegerField()
    color = models.CharField(max_length=7)  # Hex color code
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['-priority_level']

    def __str__(self):
        return f"{self.name} (Priority: {self.priority_level})"


class Event(models.Model):
    """
    Calendar event with scheduling metadata.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    is_flexible = models.BooleanField(default=True)  # Can be rescheduled
    is_completed = models.BooleanField(default=False)
    
    google_calendar_id = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['user', 'category']),
        ]

    def clean(self):
        """Validate that end_time is after start_time."""
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError('End time must be after start time.')

    def save(self, *args, **kwargs):
        """Override save to call clean() for validation."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"


class ConversationHistory(models.Model):
    """
    Store conversation context for better AI responses.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    message = models.TextField()
    response = models.TextField()
    intent_detected = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Conversation histories"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Conversation with {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SchedulingLog(models.Model):
    """
    Audit log for scheduling operations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduling_logs')
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, OPTIMIZE
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, related_name='logs')
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
