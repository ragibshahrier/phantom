"""
URL patterns for integrations app.
"""
from django.urls import path
from . import views

app_name = 'integrations'

urlpatterns = [
    path('google-calendar/connect/', views.google_calendar_connect, name='google_calendar_connect'),
    path('google-calendar/callback/', views.google_calendar_callback, name='google_calendar_callback'),
    path('google-calendar/disconnect/', views.google_calendar_disconnect, name='google_calendar_disconnect'),
    path('google-calendar/status/', views.google_calendar_status, name='google_calendar_status'),
]
