"""
Error handling for Chinook Music Database.
"""

import logging
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db import DatabaseError

logger = logging.getLogger(__name__)


def log_error(request, exception, error_type='unknown'):
    """Log error details for debugging."""
    error_info = {
        'error_type': error_type,
        'path': request.path,
        'method': request.method,
        'user': str(request.user) if request.user.is_authenticated else 'anonymous',
        'exception': str(exception),
        'exception_type': type(exception).__name__,
    }
    
    logger.error(f"Error occurred: {error_info}")
    
    # For database errors, log additional info
    if isinstance(exception, DatabaseError):
        logger.error(f"Database error details: {exception.args}")
    
    return error_info


def handle_permission_error(request, exception):
    """Handle permission denied errors."""
    error_info = log_error(request, exception, 'permission')
    
    # Log specific permission issues
    if request.user.is_authenticated:
        logger.warning(f"User {request.user.username} attempted to access restricted resource: {request.path}")
    else:
        logger.warning(f"Anonymous user attempted to access restricted resource: {request.path}")
    
    return None


def handle_not_found_error(request, exception):
    """Handle 404 not found errors."""
    error_info = log_error(request, exception, 'not_found')
    
    # Log missing resources
    logger.info(f"404 Not Found: {request.path} - Referrer: {request.META.get('HTTP_REFERER', 'None')}")
    
    return None


def handle_server_error(request, exception):
    """Handle 500 server errors."""
    error_info = log_error(request, exception, 'server')
    
    # For critical errors, could notify admins here
    # send_admin_notification(error_info)
    
    return None


def handle_bad_request_error(request, exception):
    """Handle 400 bad request errors."""
    error_info = log_error(request, exception, 'bad_request')
    
    # Log request details for debugging
    if request.method == 'POST':
        logger.warning(f"Bad POST request to {request.path} - Data: {request.POST.dict()}")
    elif request.method == 'GET':
        logger.warning(f"Bad GET request to {request.path} - Query: {request.GET.dict()}")
    
    return None