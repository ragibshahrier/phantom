"""
Views for external integrations (Google Calendar OAuth).
"""
import json
import logging

from django.shortcuts import redirect
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from .google_calendar import GoogleCalendarService

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Integrations'],
    summary='Connect Google Calendar',
    description='Initiate OAuth2 flow to connect Google Calendar. Returns authorization URL.',
    responses={
        200: {'description': 'Authorization URL generated'},
        500: {'description': 'Failed to initiate connection'}
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_calendar_connect(request):
    """
    Initiate Google Calendar OAuth2 flow.
    Returns authorization URL for user to grant access.
    """
    try:
        service = GoogleCalendarService()
        # Use user ID as state for CSRF protection
        state = str(request.user.id)
        authorization_url = service.get_authorization_url(state=state)
        
        return Response({
            'authorization_url': authorization_url,
            'message': 'Please visit the authorization URL to connect your Google Calendar'
        })
    except Exception as e:
        logger.error(f"Error initiating Google Calendar OAuth: {str(e)}")
        return Response(
            {'error': 'Failed to initiate Google Calendar connection'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Integrations'],
    summary='Google Calendar OAuth callback',
    description='OAuth2 callback endpoint. Called by Google after user authorizes access.',
    responses={
        200: {'description': 'Connection successful'},
        400: {'description': 'Authorization failed or invalid code'},
        500: {'description': 'Failed to complete connection'}
    }
)
@api_view(['GET'])
def google_calendar_callback(request):
    """
    Handle OAuth2 callback from Google.
    Exchange authorization code for tokens and store them.
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        logger.error(f"OAuth error: {error}")
        return Response(
            {'error': f'Authorization failed: {error}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not code:
        return Response(
            {'error': 'No authorization code provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        service = GoogleCalendarService()
        token_data = service.exchange_code_for_tokens(code)
        
        # Get user from state parameter
        from scheduler.models import User
        user_id = int(state)
        user = User.objects.get(id=user_id)
        
        # Store token data
        user.google_calendar_token = json.dumps(token_data)
        user.save(update_fields=['google_calendar_token'])
        
        logger.info(f"Successfully connected Google Calendar for user {user.username}")
        
        # Redirect to frontend success page or return success response
        return Response({
            'message': 'Google Calendar connected successfully',
            'user': user.username
        })
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        return Response(
            {'error': 'Failed to complete Google Calendar connection'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Integrations'],
    summary='Disconnect Google Calendar',
    description='Remove Google Calendar connection by deleting stored tokens.',
    responses={
        200: {'description': 'Disconnected successfully'},
        500: {'description': 'Failed to disconnect'}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_calendar_disconnect(request):
    """
    Disconnect Google Calendar by removing stored tokens.
    """
    try:
        user = request.user
        user.google_calendar_token = None
        user.save(update_fields=['google_calendar_token'])
        
        logger.info(f"Disconnected Google Calendar for user {user.username}")
        
        return Response({
            'message': 'Google Calendar disconnected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting Google Calendar: {str(e)}")
        return Response(
            {'error': 'Failed to disconnect Google Calendar'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Integrations'],
    summary='Check Google Calendar connection status',
    description='Check if the authenticated user has Google Calendar connected.',
    responses={
        200: {'description': 'Connection status'}
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def google_calendar_status(request):
    """
    Check if user has Google Calendar connected.
    """
    user = request.user
    is_connected = bool(user.google_calendar_token)
    
    return Response({
        'connected': is_connected,
        'user': user.username
    })
