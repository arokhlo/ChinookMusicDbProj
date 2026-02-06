from django.conf import settings

def site_settings(request):
    """Add site settings to all templates."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Chinook Music'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Music Database'),
        'DEBUG': settings.DEBUG,
    }