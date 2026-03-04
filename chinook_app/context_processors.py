from django.conf import settings

def site_settings(request):
    """Add site settings to all templates."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Chinook Music'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Music Database'),
        'DEBUG': settings.DEBUG,
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'AVATAR_MAX_SIZE': getattr(settings, 'AVATAR_MAX_SIZE', 2 * 1024 * 1024),
        'AVATAR_ALLOWED_EXTENSIONS': getattr(settings, 'AVATAR_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif']),
    }