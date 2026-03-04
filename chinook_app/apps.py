from django.apps import AppConfig


class ChinookAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chinook_app'
    
    def ready(self):
        """Initialize error handling when app is ready."""
        try:
            # Import error handlers
            from . import error_handlers
        except ImportError:
            pass