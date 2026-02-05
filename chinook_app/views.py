




















import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth import (
    get_user_model, login, update_session_auth_hash
)
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from .models import Artist, Album, Track, Review, UserProfile, SecurityQuestion
from .forms import (
    ArtistForm, AlbumForm, ReviewForm, CustomLoginForm,
    UserProfileForm, UserEmailForm, SecurityQuestionResetForm,
    SecurityQuestionVerificationForm, CustomResetPasswordForm,
    SetNewPasswordForm
)

User = get_user_model()


def admin_required(function=None):
    """Decorator for views that checks if the user is in Admin group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(
            name='Admin'
        ).exists(),
        login_url='/accounts/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_required(function=None):
    """Decorator for views that checks if the user is in Staff group."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(
            name='Staff'
        ).exists(),
        login_url='/accounts/login/'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def can_delete_content(user):
    """Check if user has permission to delete content."""
    return user.is_authenticated and (
        user.groups.filter(name__in=['Admin', 'Superuser', 'Staff']).exists()
    )

@login_required
def change_password_with_security_questions(request):
    """Handle password change with security question verification."""
    
    # First check if user has security questions
    try:
        user_questions = SecurityQuestion.objects.get(user=request.user)
    except SecurityQuestion.DoesNotExist:
        messages.warning(
            request,
            'You need to set up security questions first to change your password. '
            'Redirecting to security questions setup...'
        )
        return redirect('setup_security_questions')
    
    if request.method == 'POST':
        # Check if we're in the security questions phase
        # or password change phase
        if 'security_answers' in request.POST:
            # Verify security questions
            question1_id = request.POST.get('question1_id')
            question2_id = request.POST.get('question2_id')
            answer1 = request.POST.get('answer1', '').strip().lower()
            answer2 = request.POST.get('answer2', '').strip().lower()

            # Verify answers
            correct_answers = 0
            question_fields = [
                ('question_1', 'answer_1'),
                ('question_2', 'answer_2'),
                ('question_3', 'answer_3'),
                ('question_4', 'answer_4'),
                ('question_5', 'answer_5')
            ]

            # Check first question
            for q_field, a_field in question_fields:
                if getattr(user_questions, q_field) == question1_id:
                    if getattr(user_questions, a_field).lower() == answer1:
                        correct_answers += 1
                    break

            # Check second question
            for q_field, a_field in question_fields:
                if getattr(user_questions, q_field) == question2_id:
                    if getattr(user_questions, a_field).lower() == answer2:
                        correct_answers += 1
                    break

            if correct_answers == 2:
                # Answers are correct, proceed to password change
                form = PasswordChangeForm(request.user, request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)
                    messages.success(
                        request, 'Your password was successfully updated!'
                    )
                    return redirect('profile')
                else:
                    # Show password change form with errors
                    return render(
                        request, 'chinook_app/change_password.html', {
                            'form': form,
                            'security_verified': True
                        }
                    )
            else:
                messages.error(
                    request,
                    'Incorrect answers to security questions. '
                    'Please try again.'
                )
                return redirect('change_password_with_security')

        else:
            # Regular password change form submission
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, 'Your password was successfully updated!'
                )
                return redirect('profile')
            else:
                return render(
                    request, 'chinook_app/change_password.html', {
                        'form': form,
                        'security_verified': True
                    }
                )

    else:
        # GET request - show security questions
        # Get all available questions
        available_questions = []
        question_fields = [
            'question_1', 'question_2', 'question_3',
            'question_4', 'question_5'
        ]

        for field in question_fields:
            question_value = getattr(user_questions, field)
            if question_value:  # Only include questions that have values
                available_questions.append(question_value)

        if len(available_questions) < 2:
            messages.error(
                request, 'You need to set up at least 2 security questions.'
            )
            return redirect('setup_security_questions')

        # Randomly select 2 questions
        selected_questions = random.sample(available_questions, 2)

        return render(request, 'chinook_app/change_password.html', {
            'security_questions': selected_questions,
            'question1_id': selected_questions[0],
            'question2_id': selected_questions[1],
            'show_security_questions': True
        })

# ===== SECURITY QUESTION PASSWORD RESET VIEWS =====
@method_decorator(csrf_protect, name='dispatch')
class SecurityQuestionPasswordResetView(View):
    """Handle password reset using security questions - step 1."""

    template_name = 'account/security_question_reset.html'

    def get(self, request):
        form = SecurityQuestionResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SecurityQuestionResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                self.request.session['reset_username'] = username

                # Select 2 random questions from user's security questions
                security_questions = SecurityQuestion.objects.get(user=user)
                all_questions = [
                    (security_questions.question_1,
                     security_questions.answer_1, 1),
                    (security_questions.question_2,
                     security_questions.answer_2, 2),
                    (security_questions.question_3,
                     security_questions.answer_3, 3),
                    (security_questions.question_4,
                     security_questions.answer_4, 4),
                    (security_questions.question_5,
                     security_questions.answer_5, 5),
                ]

                # Randomly select 2 questions
                selected_questions = random.sample(all_questions, 2)

                # Store questions and answers in session
                self.request.session['security_questions'] = [
                    {'question': q[0], 'correct_answer': q[1], 'number': q[2]}
                    for q in selected_questions
                ]
                self.request.session['questions_verified'] = False
                self.request.session['reset_user_id'] = user.id

                return redirect('security_question_verify')

            except User.DoesNotExist:
                messages.error(
                    self.request, 'User not found. Please check the username.'
                )
            except SecurityQuestion.DoesNotExist:
                messages.error(
                    self.request,
                    'Security questions not found for this user. '
                    'Please contact admin.'
                )

        return render(request, self.template_name, {'form': form})

@login_required
def setup_security_questions(request):
    """Set up security questions for existing users."""
    
    # Check if user already has security questions
    try:
        SecurityQuestion.objects.get(user=request.user)
        messages.info(
            request,
            'You already have security questions set up. '
            'You can manage them from the admin panel.'
        )
        return redirect('profile')
    except SecurityQuestion.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Create a form instance with POST data
        from .forms import SecurityQuestionSetupForm
        form = SecurityQuestionSetupForm(request.POST)
        if form.is_valid():
            # Create security questions for user
            security_questions = SecurityQuestion(
                user=request.user,
                question_1=form.cleaned_data['question_1'],
                answer_1=form.cleaned_data['answer_1'].lower().strip(),
                question_2=form.cleaned_data['question_2'],
                answer_2=form.cleaned_data['answer_2'].lower().strip(),
                question_3=form.cleaned_data['question_3'],
                answer_3=form.cleaned_data['answer_3'].lower().strip(),
                question_4=form.cleaned_data['question_4'],
                answer_4=form.cleaned_data['answer_4'].lower().strip(),
                question_5=form.cleaned_data['question_5'],
                answer_5=form.cleaned_data['answer_5'].lower().strip(),
            )
            security_questions.save()
            
            messages.success(
                request,
                'Security questions have been set up successfully! '
                'You can now use them for password recovery.'
            )
            return redirect('profile')
    else:
        from .forms import SecurityQuestionSetupForm
        form = SecurityQuestionSetupForm()
    
    return render(request, 'chinook_app/setup_security_questions.html', {
        'form': form
    })


@login_required
def profile_view(request):
    """Handle user profile updates including security questions."""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    has_security_questions = SecurityQuestion.objects.filter(user=request.user).exists()
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=user_profile
            )
            email_form = UserEmailForm(instance=request.user)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(
                    request, 'Your profile has been updated successfully!'
                )
                return redirect('profile')

        elif 'update_email' in request.POST:
            profile_form = UserProfileForm(instance=user_profile)
            email_form = UserEmailForm(request.POST, instance=request.user)

            if email_form.is_valid():
                email_form.save()
                messages.success(
                    request,
                    'Your email address has been updated successfully!'
                )
                return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user_profile)
        email_form = UserEmailForm(instance=request.user)

    return render(request, 'chinook_app/profile.html', {
        'profile_form': profile_form,
        'email_form': email_form,
        'user_profile': user_profile,
        'has_security_questions': has_security_questions 
    })


@admin_required
def user_management(request):
    """User management page - only accessible by Admin users."""
    users = User.objects.select_related('userprofile').all().order_by(
        '-date_joined'
    )

    if request.method == 'POST' and request.user.is_superuser:
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        try:
            user = User.objects.get(id=user_id)
            if action == 'deactivate':
                user.is_active = False
                user.save()
                messages.success(
                    request, f'User {user.username} has been deactivated.'
                )
            elif action == 'activate':
                user.is_active = True
                user.save()
                messages.success(
                    request, f'User {user.username} has been activated.'
                )
            elif action == 'delete' and request.user.is_superuser:
                username = user.username
                user.delete()
                messages.success(
                    request, f'User {username} has been deleted.'
                )

        except User.DoesNotExist:
            messages.error(request, 'User not found.')

        return redirect('user_management')

    # Calculate statistics
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    staff_users = users.filter(is_staff=True).count()
    superusers = users.filter(is_superuser=True).count()

    return render(request, 'chinook_app/user_management.html', {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'superusers': superusers
    })


@login_required
@staff_required
def delete_album_frontend(request, album_id):
    """Front-end album deletion with confirmation."""
    album = get_object_or_404(Album, AlbumId=album_id)

    if request.method == 'POST':
        # Check if album has tracks
        if Track.objects.filter(AlbumId=album_id).exists():
            messages.error(request, 'Cannot delete album with existing tracks.')
            return redirect('all_albums')

        album_title = album.Title
        album.delete()
        messages.success(request, f'Album "{album_title}" deleted successfully!')
        return redirect('all_albums')

    return render(request, 'chinook_app/delete_confirm.html', {
        'object': album
    })


@login_required
@staff_required
def delete_artist_frontend(request, artist_id):
    """Front-end artist deletion with confirmation."""
    artist = get_object_or_404(Artist, ArtistId=artist_id)

    if request.method == 'POST':
        # Check if artist has albums
        if Album.objects.filter(ArtistId=artist_id).exists():
            messages.error(request, 'Cannot delete artist with existing albums.')
            return redirect('all_artists')

        artist_name = artist.Name
        artist.delete()
        messages.success(request, f'Artist "{artist_name}" deleted successfully!')
        return redirect('all_artists')

    return render(request, 'chinook_app/delete_confirm.html', {
        'object': artist
    })


@method_decorator(csrf_protect, name='dispatch')
class SecurityQuestionVerificationView(View):
    """Handle password reset using security questions - step 2."""

    template_name = 'account/security_question_verify.html'

    def get(self, request):
        security_questions = self.request.session.get('security_questions', [])
        username = self.request.session.get('reset_username')

        if not username or not security_questions:
            messages.error(
                self.request, 'Session expired. Please start over.'
            )
            return redirect('security_question_reset')

        form = SecurityQuestionVerificationForm(
            security_questions=security_questions
        )
        return render(request, self.template_name, {
            'form': form,
            'security_questions': security_questions
        })

    def post(self, request):
        security_questions = self.request.session.get('security_questions', [])
        username = self.request.session.get('reset_username')

        if not username or not security_questions:
            messages.error(
                self.request, 'Session expired. Please start over.'
            )
            return redirect('security_question_reset')

        form = SecurityQuestionVerificationForm(
            request.POST, security_questions=security_questions
        )

        if form.is_valid():
            try:
                user = User.objects.get(username=username)
                correct_answers = 0

                for i, question_data in enumerate(security_questions):
                    user_answer = form.cleaned_data[
                        f'answer_{i+1}'
                    ].lower().strip()
                    correct_answer = question_data[
                        'correct_answer'
                    ].lower().strip()

                    if user_answer == correct_answer:
                        correct_answers += 1

                # Require both answers to be correct
                if correct_answers >= 2:
                    self.request.session['questions_verified'] = True
                    self.request.session['verified_user_id'] = user.id
                    messages.success(
                        self.request,
                        'Security questions verified successfully! '
                        'You can now reset your password.'
                    )
                    return redirect('password_reset_from_questions')
                else:
                    messages.error(
                        self.request,
                        'Incorrect answers. Please try again or contact admin.'
                    )

            except User.DoesNotExist:
                messages.error(self.request, 'User not found.')

        return render(request, self.template_name, {
            'form': form,
            'security_questions': security_questions
        })


@method_decorator(csrf_protect, name='dispatch')
class QuestionBasedPasswordResetView(View):
    """Handle password reset using security questions - step 3."""

    template_name = 'account/password_reset_from_questions.html'

    def get(self, request):
        if not self.request.session.get('questions_verified'):
            messages.error(
                self.request, 'Please verify security questions first.'
            )
            return redirect('security_question_reset')

        form = SetNewPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not self.request.session.get('questions_verified'):
            messages.error(
                self.request, 'Please verify security questions first.'
            )
            return redirect('security_question_reset')

        user_id = self.request.session.get('verified_user_id')
        if not user_id:
            messages.error(
                self.request, 'Session expired. Please start over.'
            )
            return redirect('security_question_reset')

        try:
            user = User.objects.get(id=user_id)
            form = SetNewPasswordForm(request.POST)

            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()

                # Clear session data
                self._clear_reset_session()

                messages.success(
                    self.request,
                    'Your password has been reset successfully! '
                    'You can now log in with your new password.'
                )
                return redirect('account_login')

            return render(request, self.template_name, {'form': form})

        except User.DoesNotExist:
            messages.error(self.request, 'User not found.')
            return redirect('security_question_reset')

    def _clear_reset_session(self):
        """Clear all password reset related session data."""
        session_keys = [
            'security_questions',
            'reset_username',
            'questions_verified',
            'verified_user_id',
            'reset_user_id'
        ]
        for key in session_keys:
            if key in self.request.session:
                del self.request.session[key]


# ===== OVERRIDE ALLAUTH PASSWORD RESET TO REDIRECT TO SECURITY QUESTIONS =====
class CustomPasswordResetView(PasswordResetView):
    """Override allauth password reset to redirect to security questions."""

    form_class = CustomResetPasswordForm

    def form_valid(self, form):
        # Redirect to security question flow instead of sending email
        username = form.cleaned_data.get(
            'email'
        )  # Using email field for username
        if username:
            try:
                user = User.objects.get(username=username)
                self.request.session['reset_username'] = username
                return redirect('security_question_reset')
            except User.DoesNotExist:
                messages.error(
                    self.request, 'User not found. Please check the username.'
                )

        return self.form_invalid(form)


@login_required
def delete_avatar(request):
    """Handle avatar deletion for user profile."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        if user_profile.avatar:
            # Delete the avatar file
            if os.path.isfile(user_profile.avatar.path):
                os.remove(user_profile.avatar.path)
            user_profile.avatar.delete(save=True)
            messages.success(
                request, 'Your avatar has been deleted successfully!'
            )
        return redirect('profile')

    return render(request, 'chinook_app/delete_avatar.html', {
        'user_profile': user_profile
    })


# ===== CORE APPLICATION VIEWS =====
def index(request):
    """Homepage view with statistics and recent content."""
    try:
        # Safely get counts with error handling for missing tables
        artists_count = Artist.objects.count() if hasattr(Artist.objects, 'count') else 0
        albums_count = Album.objects.count() if hasattr(Album.objects, 'count') else 0
        tracks_count = Track.objects.count() if hasattr(Track.objects, 'count') else 0
        
        # Get recent albums if table exists
        try:
            recent_albums = Album.objects.select_related(
                'ArtistId'
            ).order_by('-AlbumId')[:3]
        except:
            recent_albums = []
        
        # Get recent tracks if table exists
        try:
            recent_tracks = Track.objects.select_related(
                'AlbumId', 'AlbumId__ArtistId'
            ).all()[:15]
        except:
            recent_tracks = []
        
        # Get top rated tracks if table exists
        try:
            top_rated_tracks = Track.objects.annotate(
                avg_rating=Avg('review__rating')
            ).filter(avg_rating__gte=4).order_by('-avg_rating')[:5]
        except:
            top_rated_tracks = []
            
    except Exception as e:
        # If any database error occurs, use default values
        print(f"Database error in index view: {e}")  # For debugging
        artists_count = 0
        albums_count = 0
        tracks_count = 0
        recent_albums = []
        recent_tracks = []
        top_rated_tracks = []
    
    stats = {
        'artists_count': artists_count,
        'albums_count': albums_count,
        'tracks_count': tracks_count,
        'recent_albums': recent_albums,
        'recent_tracks': recent_tracks,
        'top_rated_tracks': top_rated_tracks
    }
    return render(request, 'chinook_app/index.html', stats)


def all_artists(request):
    """Display paginated list of all artists."""
    try:
        artists = Artist.objects.all().order_by('Name')
        paginator = Paginator(artists, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except:
        # If table doesn't exist, show empty page
        page_obj = []
    
    return render(request, 'chinook_app/artists.html', {'artists': page_obj})


def all_albums(request):
    """Display paginated list of all albums."""
    try:
        albums = Album.objects.select_related('ArtistId').all().order_by('Title')
        paginator = Paginator(albums, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    except:
        # If table doesn't exist, show empty page
        page_obj = []
    
    return render(request, 'chinook_app/albums.html', {'albums': page_obj})


# ===== SEARCH AND FILTER VIEWS =====
def search_artist(request):
    """Search artists by name."""
    artists = None
    search_term = ''

    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        if search_term:
            try:
                artists = Artist.objects.filter(
                    Q(Name__icontains=search_term)
                ).order_by('Name')
            except:
                artists = []

    return render(request, 'chinook_app/search_artist.html', {
        'artists': artists,
        'search_term': search_term
    })


def search_album(request):
    """Search albums by title."""
    albums = None
    search_term = ''

    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        if search_term:
            try:
                albums = Album.objects.filter(
                    Q(Title__icontains=search_term)
                ).select_related('ArtistId').order_by('Title')
            except:
                albums = []

    return render(request, 'chinook_app/search_album.html', {
        'albums': albums,
        'search_term': search_term
    })


def search_track(request):
    """Search tracks by name."""
    tracks = None
    search_term = ''

    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        if search_term:
            try:
                tracks = Track.objects.filter(
                    Q(Name__icontains=search_term)
                ).select_related('AlbumId', 'AlbumId__ArtistId').order_by('Name')
            except:
                tracks = []

    return render(request, 'chinook_app/search_track.html', {
        'tracks': tracks,
        'search_term': search_term
    })


def artist_albums(request):
    """Display albums by selected artist."""
    albums = None
    artist = None

    if request.method == 'POST':
        artist_id = request.POST.get('artist_id')
        if artist_id:
            try:
                artist = get_object_or_404(Artist, ArtistId=artist_id)
                albums = Album.objects.filter(ArtistId=artist_id).order_by('Title')
            except:
                artist = None
                albums = []

    artists = Artist.objects.all().order_by('Name') if hasattr(Artist.objects, 'all') else []
    return render(request, 'chinook_app/artist_albums.html', {
        'artists': artists,
        'albums': albums,
        'artist': artist
    })


def album_tracks(request):
    """Display tracks by selected album."""
    tracks = None
    album = None

    if request.method == 'POST':
        album_id = request.POST.get('album_id')
        if album_id:
            try:
                album = get_object_or_404(Album, AlbumId=album_id)
                tracks = Track.objects.filter(AlbumId=album_id).order_by('TrackId')
            except:
                album = None
                tracks = []

    albums = Album.objects.select_related('ArtistId').all().order_by('Title') if hasattr(Album.objects, 'all') else []
    return render(request, 'chinook_app/album_tracks.html', {
        'albums': albums,
        'tracks': tracks,
        'album': album
    })


# ===== CREATE OPERATIONS =====
@login_required
def add_artist(request):
    """Add new artist to the database."""
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist_name = form.cleaned_data['Name']

            try:
                with connection.cursor() as cursor:
                    # Let PostgreSQL auto-generate the ArtistId using SERIAL
                    cursor.execute(
                        'INSERT INTO "Artist" ("Name") VALUES (%s) '
                        'RETURNING "ArtistId"',
                        [artist_name]
                    )
                    artist_id = cursor.fetchone()[0]

                msg = 'Artist "{}" added with ID: {}!'.format(
                    artist_name, artist_id
                )
                messages.success(request, msg)
                return redirect('all_artists')

            except Exception as e:
                messages.error(request, f'Error adding artist: {str(e)}')

    else:
        form = ArtistForm()

    return render(request, 'chinook_app/add_artist.html', {'form': form})


@login_required
def add_album(request):
    """Add new album to the database."""
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album_title = form.cleaned_data['Title']
            artist_id = form.cleaned_data['ArtistId'].ArtistId

            try:
                with connection.cursor() as cursor:
                    # Let PostgreSQL auto-generate the AlbumId using SERIAL
                    cursor.execute(
                        'INSERT INTO "Album" ("Title", "ArtistId") '
                        'VALUES (%s, %s) RETURNING "AlbumId"',
                        [album_title, artist_id]
                    )
                    album_id = cursor.fetchone()[0]

                messages.success(
                    request, f'Album "{album_title}" added successfully!'
                )
                return redirect('all_albums')

            except Exception as e:
                messages.error(request, f'Error adding album: {str(e)}')

    else:
        form = AlbumForm()

    artists = Artist.objects.all().order_by('Name') if hasattr(Artist.objects, 'all') else []
    return render(request, 'chinook_app/add_album.html', {
        'form': form,
        'artists': artists
    })


# ===== UPDATE OPERATIONS =====
@login_required
def update_artist(request):
    """Update existing artist information."""
    artists = Artist.objects.all().order_by('Name') if hasattr(Artist.objects, 'all') else []
    selected_artist = None

    if request.method == 'POST':
        if 'select_artist' in request.POST:
            artist_id = request.POST.get('artist_id')
            if artist_id:
                try:
                    selected_artist = get_object_or_404(Artist, ArtistId=artist_id)
                except:
                    selected_artist = None

        elif 'update_artist' in request.POST:
            artist_id = request.POST.get('artist_id')
            new_name = request.POST.get('new_name')
            if artist_id and new_name:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            'UPDATE "Artist" SET "Name" = %s '
                            'WHERE "ArtistId" = %s',
                            [new_name, artist_id]
                        )

                    messages.success(
                        request,
                        f'Artist updated successfully to "{new_name}"!'
                    )
                    return redirect('all_artists')

                except Exception as e:
                    messages.error(
                        request, f'Error updating artist: {str(e)}'
                    )

    return render(request, 'chinook_app/update_artist.html', {
        'artists': artists,
        'selected_artist': selected_artist
    })


@login_required
def update_album(request):
    """Update existing album information."""
    albums = Album.objects.select_related('ArtistId').all().order_by('Title') if hasattr(Album.objects, 'all') else []
    selected_album = None

    if request.method == 'POST':
        if 'select_album' in request.POST:
            album_id = request.POST.get('album_id')
            if album_id:
                try:
                    selected_album = get_object_or_404(Album, AlbumId=album_id)
                except:
                    selected_album = None

        elif 'update_album' in request.POST:
            album_id = request.POST.get('album_id')
            new_title = request.POST.get('new_title')
            if album_id and new_title:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            'UPDATE "Album" SET "Title" = %s '
                            'WHERE "AlbumId" = %s',
                            [new_title, album_id]
                        )

                    messages.success(
                        request,
                        f'Album updated successfully to "{new_title}"!'
                    )
                    return redirect('all_albums')

                except Exception as e:
                    messages.error(
                        request, f'Error updating album: {str(e)}'
                    )

    return render(request, 'chinook_app/update_album.html', {
        'albums': albums,
        'selected_album': selected_album
    })


# ===== DELETE OPERATIONS =====
@login_required
@staff_required
def delete_artist(request):
    """Delete artist from the database (with validation)."""
    artists = Artist.objects.all().order_by('Name') if hasattr(Artist.objects, 'all') else []
    selected_artist = None
    error = None

    if request.method == 'POST':
        if 'select_artist' in request.POST:
            artist_id = request.POST.get('artist_id')
            if artist_id:
                try:
                    selected_artist = get_object_or_404(Artist, ArtistId=artist_id)
                    # Check if artist has albums
                    if Album.objects.filter(ArtistId=artist_id).exists():
                        error = (
                            "Cannot delete artist with existing albums. "
                            "Please delete the albums first."
                        )
                except:
                    selected_artist = None

        elif 'delete_artist' in request.POST:
            artist_id = request.POST.get('artist_id')
            if artist_id:
                try:
                    artist = get_object_or_404(Artist, ArtistId=artist_id)
                    artist_name = artist.Name
                    # Double-check no albums exist
                    if not Album.objects.filter(ArtistId=artist_id).exists():
                        artist.delete()
                        success_msg = (
                            f'Artist "{artist_name}" deleted successfully!'
                        )
                        messages.success(request, success_msg)
                        return redirect('all_artists')
                    else:
                        error = "Cannot delete artist with existing albums."
                except:
                    error = "Artist not found or cannot be deleted."

    return render(request, 'chinook_app/delete_artist.html', {
        'artists': artists,
        'selected_artist': selected_artist,
        'error': error
    })


@login_required
@staff_required
def delete_album(request):
    """Delete album from the database (with validation)."""
    albums = Album.objects.select_related('ArtistId').all().order_by('Title') if hasattr(Album.objects, 'all') else []
    selected_album = None
    error = None

    if request.method == 'POST':
        if 'select_album' in request.POST:
            album_id = request.POST.get('album_id')
            if album_id:
                try:
                    selected_album = get_object_or_404(Album, AlbumId=album_id)
                    # Check if album has tracks
                    if Track.objects.filter(AlbumId=album_id).exists():
                        error = (
                            "Cannot delete album with existing tracks. "
                            "Please delete the tracks first."
                        )
                except:
                    selected_album = None

        elif 'delete_album' in request.POST:
            album_id = request.POST.get('album_id')
            if album_id:
                try:
                    album = get_object_or_404(Album, AlbumId=album_id)
                    album_title = album.Title
                    # Double-check no tracks exist
                    if not Track.objects.filter(AlbumId=album_id).exists():
                        album.delete()
                        success_msg = (
                            f'Album "{album_title}" deleted successfully!'
                        )
                        messages.success(request, success_msg)
                        return redirect('all_albums')
                    else:
                        error = "Cannot delete album with existing tracks."
                except:
                    error = "Album not found or cannot be deleted."

    return render(request, 'chinook_app/delete_album.html', {
        'albums': albums,
        'selected_album': selected_album,
        'error': error
    })


# ===== REVIEW SYSTEM VIEWS =====
@login_required
def add_review(request, track_id):
    """Add a review for a specific track."""
    try:
        track = get_object_or_404(Track, TrackId=track_id)
    except:
        messages.error(request, 'Track not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.track = track
            review.save()
            messages.success(
                request, 'Your review has been added successfully!'
            )
            return redirect('track_detail', track_id=track_id)
    else:
        form = ReviewForm()

    return render(request, 'chinook_app/add_review.html', {
        'form': form,
        'track': track
    })


@login_required
def update_review(request, review_id):
    """Update an existing review."""
    try:
        review = get_object_or_404(Review, id=review_id, user=request.user)
    except:
        messages.error(request, 'Review not found.')
        return redirect('home')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your review has been updated successfully!'
            )
            return redirect('track_detail', track_id=review.track.TrackId)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'chinook_app/update_review.html', {
        'form': form,
        'review': review
    })


@login_required
def delete_review(request, review_id):
    """Delete an existing review."""
    try:
        review = get_object_or_404(Review, id=review_id, user=request.user)
    except:
        messages.error(request, 'Review not found.')
        return redirect('home')

    if request.method == 'POST':
        track_id = review.track.TrackId
        review.delete()
        messages.success(
            request, 'Your review has been deleted successfully!'
        )
        return redirect('track_detail', track_id=track_id)

    return render(request, 'chinook_app/delete_review.html', {
        'review': review
    })


def track_detail(request, track_id):
    """Display track details and associated reviews."""
    try:
        track = get_object_or_404(Track, TrackId=track_id)
        reviews = Review.objects.filter(track=track).select_related('user')
        user_review = None

        if request.user.is_authenticated:
            user_review = Review.objects.filter(
                track=track, user=request.user
            ).first()

        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    except:
        # If track doesn't exist or there's an error
        track = None
        reviews = []
        user_review = None
        average_rating = None
        messages.error(request, 'Track not found or cannot be accessed.')

    return render(request, 'chinook_app/track_detail.html', {
        'track': track,
        'reviews': reviews,
        'user_review': user_review,
        'average_rating': average_rating
    })