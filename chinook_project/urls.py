"""
URL configuration for chinook_project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
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
    
    # API Documentation (optional)
    # path('api-docs/', TemplateView.as_view(template_name='api_docs.html'), name='api_docs'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ===== CUSTOM ERROR HANDLERS =====
# These must be defined here, not in the urlpatterns
handler400 = 'chinook_app.views.custom_400'
handler403 = 'chinook_app.views.custom_403'
handler404 = 'chinook_app.views.custom_404'
handler500 = 'chinook_app.views.custom_500'