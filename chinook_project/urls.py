from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from chinook_app import views as chinook_views


urlpatterns = [
    # ===== ADMIN PANEL =====
    path('admin/', admin.site.urls),
    
    # ===== AUTHENTICATION (Django Allauth) =====
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
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error pages
handler404 = chinook_views.custom_404
handler500 = chinook_views.custom_500
handler403 = chinook_views.custom_403
handler400 = chinook_views.custom_400