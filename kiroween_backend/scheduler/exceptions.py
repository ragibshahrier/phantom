"""
Custom exception handlers for Phantom Scheduler.
"""
import logging
import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    AuthenticationFailed,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    
    Logs all errors with context and returns appropriate status codes
    without exposing internal details to users.
    
    Args:
        exc: The exception instance
        context: Dictionary containing request and view information
        
    Returns:
        Response object with error details
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get request information for logging
    request = context.get('request')
    view = context.get('view')
    
    # Build context information for logging
    log_context = {
        'path': request.path if request else 'unknown',
        'method': request.method if request else 'unknown',
        'user': str(request.user) if request and hasattr(request, 'user') else 'anonymous',
        'view': view.__class__.__name__ if view else 'unknown',
        'exception_type': exc.__class__.__name__,
    }
    
    # If response is None, it's an unhandled exception
    if response is None:
        # Log the full error with stack trace
        logger.error(
            f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
            extra=log_context,
            exc_info=True
        )
        
        # Handle specific Django exceptions
        if isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    'error': 'Validation error',
                    'detail': 'The provided data is invalid.',
                    'status_code': status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, Http404):
            response = Response(
                {
                    'error': 'Not found',
                    'detail': 'The requested resource was not found.',
                    'status_code': status.HTTP_404_NOT_FOUND
                },
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # Generic error response for unexpected exceptions
            response = Response(
                {
                    'error': 'Internal server error',
                    'detail': 'An unexpected error occurred. Please try again later.',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Log handled exceptions based on severity
        status_code = response.status_code
        
        if status_code >= 500:
            # Server errors - log as ERROR
            logger.error(
                f"Server error: {exc.__class__.__name__}: {str(exc)}",
                extra=log_context,
                exc_info=True
            )
        elif status_code >= 400:
            # Client errors - log as WARNING
            logger.warning(
                f"Client error: {exc.__class__.__name__}: {str(exc)}",
                extra=log_context
            )
        
        # Ensure response has consistent structure
        if isinstance(response.data, dict):
            if 'error' not in response.data:
                response.data['error'] = get_error_type(exc)
            if 'status_code' not in response.data:
                response.data['status_code'] = status_code
    
    return response


def get_error_type(exc):
    """
    Get a user-friendly error type from exception.
    
    Args:
        exc: The exception instance
        
    Returns:
        String describing the error type
    """
    if isinstance(exc, ValidationError):
        return 'Validation error'
    elif isinstance(exc, NotFound):
        return 'Not found'
    elif isinstance(exc, PermissionDenied):
        return 'Permission denied'
    elif isinstance(exc, AuthenticationFailed):
        return 'Authentication failed'
    else:
        return 'Error'
