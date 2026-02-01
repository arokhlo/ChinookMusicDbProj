from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # ===== ADMIN PANEL =====
    path('admin/', admin.site.urls),
    
    # ===== AUTHENTICATION (Django Allauth) =====
    # Include allauth URLs with password reset ENABLED
    path('accounts/', include('allauth.urls')),
    
    # ===== APPLICATION ROUTES =====
    path('', include('chinook_app.urls')),
    
    # ===== UTILITY ROUTES =====
    # Redirect favicon requests
    path('favicon.ico', lambda request: redirect('/static/favicon.ico', permanent=True)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)