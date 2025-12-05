"""
Views for the Phantom scheduler application.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db import transaction
import jwt
from django.conf import settings
import logging
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import User, BlacklistedToken, Event, Category, SchedulingLog
from .serializers import (
    UserRegistrationSerializer, EventSerializer, EventListSerializer,
    CategorySerializer, UserPreferencesSerializer
)

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Authentication'],
    summary='Register new user',
    description='Create a new user account with username, name, and password. '
                'Passwords are securely hashed before storage.',
    request=UserRegistrationSerializer,
    responses={
        201: {'description': 'User registered successfully'},
        400: {'description': 'Invalid input data or username already exists'},
        500: {'description': 'Internal server error'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user account.
    
    Validates username uniqueness, password strength, and creates a new user
    with hashed password.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                logger.info(f"User registered successfully: {user.username}")
                return Response(
                    {
                        'message': 'User registered successfully',
                        'username': user.username,
                        'name': user.name
                    },
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Registration failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    summary='User login',
    description='Authenticate with username and password to receive JWT access and refresh tokens. '
                'Access tokens expire in 15 minutes, refresh tokens in 7 days.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string', 'format': 'password'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {'description': 'Login successful'},
        400: {'description': 'Missing username or password'},
        401: {'description': 'Invalid credentials'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate user and return JWT tokens.
    
    Returns both access token (15 min expiry) and refresh token (7 days expiry).
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Use a valid refresh token to obtain a new access token without re-authenticating.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: {'description': 'New access token generated'},
        400: {'description': 'Refresh token not provided'},
        401: {'description': 'Invalid, expired, or blacklisted refresh token'}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and generates new access token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if token is blacklisted
    if BlacklistedToken.objects.filter(token=refresh_token).exists():
        return Response(
            {'error': 'Token has been blacklisted'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        
        return Response({
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@extend_schema(
    tags=['Authentication'],
    summary='User logout',
    description='Logout by blacklisting the refresh token. After logout, the refresh token '
                'cannot be used to obtain new access tokens.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
            },
            'required': ['refresh']
        }
    },
    responses={
        200: {'description': 'Successfully logged out'},
        400: {'description': 'Invalid refresh token'},
        401: {'description': 'Authentication required'}
    }
)
@api_view(['POST'])
def logout(request):
    """
    Logout user by blacklisting refresh token.
    
    Adds refresh token to blacklist to prevent future use.
    Requirements: 17.1, 17.2, 17.3, 17.4
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # Decode and validate the refresh token
            token = RefreshToken(refresh_token)
            
            # Get expiration time from token and make it timezone-aware
            expires_at = timezone.make_aware(datetime.fromtimestamp(token['exp']))
            
            # Check if token is already blacklisted
            if BlacklistedToken.objects.filter(token=refresh_token).exists():
                return Response(
                    {'message': 'Token already blacklisted'},
                    status=status.HTTP_200_OK
                )
            
            # Add to blacklist with expiration time
            BlacklistedToken.objects.create(
                token=refresh_token,
                user=request.user,
                expires_at=expires_at
            )
            
            logger.info(f"User logged out successfully: {request.user.username}")
            
            return Response(
                {'message': 'Successfully logged out'},
                status=status.HTTP_200_OK
            )
    except Exception as e:
        logger.error(f"Logout failed for user {request.user.username}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Invalid refresh token'},
            status=status.HTTP_400_BAD_REQUEST
        )



@extend_schema_view(
    list=extend_schema(
        tags=['Events'],
        summary='List events',
        description='Retrieve all events for the authenticated user with optional filtering.',
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATETIME,
                description='Filter events that end after this date (ISO 8601 format)',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATETIME,
                description='Filter events that start before this date (ISO 8601 format)',
                required=False
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.INT,
                description='Filter by category ID',
                required=False
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.INT,
                description='Filter by minimum priority level',
                required=False
            ),
        ],
        responses={200: EventListSerializer(many=True)}
    ),
    create=extend_schema(
        tags=['Events'],
        summary='Create event',
        description='Create a new calendar event for the authenticated user.',
        request=EventSerializer,
        responses={
            201: EventSerializer,
            400: {'description': 'Invalid input data'},
            401: {'description': 'Authentication required'}
        }
    ),
    retrieve=extend_schema(
        tags=['Events'],
        summary='Get event',
        description='Retrieve a specific event by ID.',
        responses={
            200: EventSerializer,
            404: {'description': 'Event not found'}
        }
    ),
    update=extend_schema(
        tags=['Events'],
        summary='Update event',
        description='Update an existing event.',
        request=EventSerializer,
        responses={
            200: EventSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Event not found'}
        }
    ),
    partial_update=extend_schema(
        tags=['Events'],
        summary='Partially update event',
        description='Partially update an existing event.',
        request=EventSerializer,
        responses={
            200: EventSerializer,
            400: {'description': 'Invalid input data'},
            404: {'description': 'Event not found'}
        }
    ),
    destroy=extend_schema(
        tags=['Events'],
        summary='Delete event',
        description='Delete an event.',
        responses={
            204: {'description': 'Event deleted successfully'},
            404: {'description': 'Event not found'}
        }
    )
)
class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Event CRUD operations.
    
    Provides create, list, retrieve, update, and destroy actions.
    Filters events by authenticated user and supports query parameter filtering.
    
    Requirements: 8.1, 8.2, 8.3, 8.4, 11.3
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use optimized serializer for list views."""
        if self.action == 'list':
            return EventListSerializer
        return EventSerializer
    
    def get_queryset(self):
        """
        Filter events by authenticated user and apply query parameters.
        
        Supports filtering by:
        - date_range: start_date and end_date parameters (returns events that intersect with range)
        - category: category ID
        - priority: minimum priority level
        
        Requirements: 5.2, 8.2, 11.3
        """
        queryset = Event.objects.filter(user=self.request.user).select_related('category')
        
        # Date range filtering - return events that intersect with the requested range
        # An event intersects with the range if: event.start_time < range_end AND event.end_time > range_start
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            start_dt = parse_datetime(start_date)
            end_dt = parse_datetime(end_date)
            if start_dt and end_dt:
                # Events that intersect with the range
                queryset = queryset.filter(
                    start_time__lt=end_dt,
                    end_time__gt=start_dt
                )
        elif start_date:
            start_dt = parse_datetime(start_date)
            if start_dt:
                # Events that end after the start date
                queryset = queryset.filter(end_time__gt=start_dt)
        elif end_date:
            end_dt = parse_datetime(end_date)
            if end_dt:
                # Events that start before the end date
                queryset = queryset.filter(start_time__lt=end_dt)
        
        # Category filtering
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Priority filtering (minimum priority level)
        priority = self.request.query_params.get('priority')
        if priority:
            try:
                min_priority = int(priority)
                queryset = queryset.filter(category__priority_level__gte=min_priority)
            except ValueError:
                pass  # Ignore invalid priority values
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the user to the authenticated user when creating an event."""
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new event.
        
        Returns 201 with event details on success.
        Requirements: 8.1
        """
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                # Log the event creation
                SchedulingLog.objects.create(
                    user=request.user,
                    action='CREATE',
                    event=serializer.instance,
                    details={
                        'title': serializer.instance.title,
                        'start_time': serializer.instance.start_time.isoformat(),
                        'end_time': serializer.instance.end_time.isoformat(),
                        'category': serializer.instance.category.name
                    }
                )
                
                logger.info(f"Event created: {serializer.instance.title} for user {request.user.username}")
                
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Event creation failed for user {request.user.username}: {str(e)}", exc_info=True)
            raise
    
    def list(self, request, *args, **kwargs):
        """
        List all events for the authenticated user.
        
        Supports query parameter filtering.
        Requirements: 8.2, 11.3
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific event.
        
        Requirements: 8.2
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update an event.
        
        Returns updated event data.
        Requirements: 8.3
        """
        try:
            with transaction.atomic():
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                
                # Log the event update
                SchedulingLog.objects.create(
                    user=request.user,
                    action='UPDATE',
                    event=serializer.instance,
                    details={
                        'title': serializer.instance.title,
                        'start_time': serializer.instance.start_time.isoformat(),
                        'end_time': serializer.instance.end_time.isoformat(),
                        'category': serializer.instance.category.name
                    }
                )
                
                logger.info(f"Event updated: {serializer.instance.title} for user {request.user.username}")
                
                return Response(serializer.data)
        except Exception as e:
            logger.error(f"Event update failed for user {request.user.username}: {str(e)}", exc_info=True)
            raise
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an event.
        
        Returns 204 on success.
        Requirements: 8.4
        """
        try:
            with transaction.atomic():
                instance = self.get_object()
                event_title = instance.title
                
                # Log the event deletion before deleting
                SchedulingLog.objects.create(
                    user=request.user,
                    action='DELETE',
                    event=None,  # Event will be deleted
                    details={
                        'event_id': instance.id,
                        'title': event_title,
                        'start_time': instance.start_time.isoformat(),
                        'end_time': instance.end_time.isoformat(),
                        'category': instance.category.name
                    }
                )
                
                self.perform_destroy(instance)
                
                logger.info(f"Event deleted: {event_title} for user {request.user.username}")
                
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Event deletion failed for user {request.user.username}: {str(e)}", exc_info=True)
            raise


@extend_schema_view(
    list=extend_schema(
        tags=['Categories'],
        summary='List categories',
        description='Retrieve all task categories with their priority levels.',
        responses={200: CategorySerializer(many=True)}
    ),
    create=extend_schema(
        tags=['Categories'],
        summary='Create category',
        description='Create a new task category with priority level.',
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: {'description': 'Invalid input data'}
        }
    ),
    retrieve=extend_schema(
        tags=['Categories'],
        summary='Get category',
        description='Retrieve a specific category by ID.',
        responses={
            200: CategorySerializer,
            404: {'description': 'Category not found'}
        }
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category operations.
    
    Provides listing and creating categories.
    Requirements: 2.3, 11.4
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # Only allow list, create, and retrieve


@extend_schema_view(
    list=extend_schema(
        tags=['Preferences'],
        summary='Get user preferences',
        description='Retrieve preferences for the authenticated user (timezone, default event duration, etc.).',
        responses={200: UserPreferencesSerializer}
    ),
    update=extend_schema(
        tags=['Preferences'],
        summary='Update user preferences',
        description='Update user preferences.',
        request=UserPreferencesSerializer,
        responses={
            200: UserPreferencesSerializer,
            400: {'description': 'Invalid input data'}
        }
    )
)
class UserPreferencesViewSet(viewsets.ViewSet):
    """
    ViewSet for user preferences.
    
    Provides retrieval and update of user preferences.
    Requirements: 11.5
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Get user preferences.
        """
        serializer = UserPreferencesSerializer(request.user)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """
        Update user preferences.
        """
        serializer = UserPreferencesSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
