"""
URL configuration for scheduler app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for viewsets
router = DefaultRouter()
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'preferences', views.UserPreferencesViewSet, basename='preferences')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/token/refresh/', views.token_refresh, name='token_refresh'),
    
    # Include router URLs
    path('', include(router.urls)),
]
