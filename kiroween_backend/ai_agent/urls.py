"""
URL configuration for ai_agent app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Chat endpoint
    path('chat/', views.chat, name='chat'),
    
    # Conversation history endpoint
    path('chat/history/', views.conversation_history, name='conversation_history'),
]
