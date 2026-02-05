# chinook_app/urls.py
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ===== OVERRIDE ALLAUTH PASSWORD RESET WITH SECURITY QUESTIONS =====
    path(
        'accounts/password/reset/',
        views.CustomPasswordResetView.as_view(),
        name='account_reset_password'
    ),
    path(
        'accounts/password/change/',
        views.change_password_with_security_questions,
        name='account_change_password'
    ),

    # Or add it as a new endpoint (recommended for testing)
    path(
        'accounts/change-password-security/',
        views.change_password_with_security_questions,
        name='change_password_with_security'
    ),

    # ===== SECURITY QUESTION PASSWORD RESET FLOW =====
    path(
        'accounts/password/reset/security-questions/',
        views.SecurityQuestionPasswordResetView.as_view(),
        name='security_question_reset'
    ),
    path(
        'accounts/password/reset/verify-questions/',
        views.SecurityQuestionVerificationView.as_view(),
        name='security_question_verify'
    ),
    path(
        'accounts/password/reset/set-password/',
        views.QuestionBasedPasswordResetView.as_view(),
        name='password_reset_from_questions'
    ),

    # ===== HOME & CORE PAGES =====
    path('', views.index, name='home'),

    # ===== BROWSE PAGES =====
    path('artists/', views.all_artists, name='all_artists'),
    path('albums/', views.all_albums, name='all_albums'),

    # ===== SEARCH & FILTER PAGES =====
    path('search-artist/', views.search_artist, name='search_artist'),
    path('search-album/', views.search_album, name='search_album'),
    path('search-track/', views.search_track, name='search_track'),
    path('artist-albums/', views.artist_albums, name='artist_albums'),
    path('album-tracks/', views.album_tracks, name='album_tracks'),

    # ===== CREATE OPERATIONS =====
    path('add-artist/', views.add_artist, name='add_artist'),
    path('add-album/', views.add_album, name='add_album'),

    # ===== UPDATE OPERATIONS =====
    path('update-artist/', views.update_artist, name='update_artist'),
    path('update-album/', views.update_album, name='update_album'),

    # ===== DELETE OPERATIONS =====
    path('delete-artist/', views.delete_artist, name='delete_artist'),
    path('delete-album/', views.delete_album, name='delete_album'),

    # Frontend delete URLs (if you want separate endpoints)
    path('artist/<int:artist_id>/delete/', views.delete_artist_frontend, name='delete_artist_frontend'),
    path('album/<int:album_id>/delete/', views.delete_album_frontend, name='delete_album_frontend'),
 
    # ===== TRACK & REVIEW SYSTEM =====
    path('track/<int:track_id>/', views.track_detail, name='track_detail'),
    path(
        'track/<int:track_id>/review/',
        views.add_review,
        name='add_review'
    ),
    path(
        'review/<int:review_id>/update/',
        views.update_review,
        name='update_review'
    ),
    path(
        'review/<int:review_id>/delete/',
        views.delete_review,
        name='delete_review'
    ),

    # ===== USER PROFILE MANAGEMENT =====
    path('profile/', views.profile_view, name='profile'),
    path(
        'profile/delete-avatar/',
        views.delete_avatar,
        name='delete_avatar'
    ),
    
    # ADD THIS LINE FOR SECURITY QUESTIONS SETUP
    path(
        'profile/setup-security-questions/',
        views.setup_security_questions,
        name='setup_security_questions'
    ),

    # ===== ADMIN USER MANAGEMENT =====
    path('user-management/', views.user_management, name='user_management'),

    # ===== INCLUDE DJANGO-ALLAUTH URLS =====
    path('accounts/', include('allauth.urls')),

    # Add these URLs
    path(
        'album/<int:album_id>/delete/',
        views.delete_album_frontend,
        name='delete_album_frontend'
    ),
    path(
        'artist/<int:artist_id>/delete/',
        views.delete_artist_frontend,
        name='delete_artist_frontend'
    ),

    path(
        'accounts/change-password/',
        views.change_password_with_security_questions,
        name='change_password_with_security'
    ),

    path(
        'accounts/password/change/',
        views.change_password_with_security_questions,
        name='account_change_password'
    ),

    # Keep your custom URL for testing
    path(
        'accounts/change-password-security/',
        views.change_password_with_security_questions,
        name='change_password_with_security'
    ),
]