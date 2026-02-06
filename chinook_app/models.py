import os
import uuid
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


class SecurityQuestion(models.Model):
    """
    Security questions for user authentication and password recovery.
    """
    QUESTION_CHOICES = [
        ('birth_year', '1. What is your birth year?'),
        ('father_birth_year', '2. What is your father\'s birth year?'),
        ('mother_name', '3. What is your mother\'s name?'),
        ('father_name', '4. What is your father\'s name?'),
        ('favourite_colour', '5. What is your favourite colour?'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    question_1 = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer_1 = models.CharField(max_length=255)
    question_2 = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer_2 = models.CharField(max_length=255)
    question_3 = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer_3 = models.CharField(max_length=255)
    question_4 = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer_4 = models.CharField(max_length=255)
    question_5 = models.CharField(max_length=50, choices=QUESTION_CHOICES)
    answer_5 = models.CharField(max_length=255)

    def __str__(self):
        return f"Security Questions for {self.user.username}"

    def get_available_questions(self):
        """Returns a list of available questions that haven't been used yet."""
        used_questions = [
            self.question_1,
            self.question_2,
            self.question_3,
            self.question_4,
            self.question_5,
        ]
        available_questions = [
            (choice[0], choice[1]) for choice in self.QUESTION_CHOICES
            if choice[0] not in used_questions
        ]
        return available_questions

    def get_question_display(self, question_field):
        """Returns the display text for a question field."""
        question_value = getattr(self, question_field)
        for choice in self.QUESTION_CHOICES:
            if choice[0] == question_value:
                return choice[1]
        return question_value


def validate_image_size(value):
    """Validate that image size is under 2MB."""
    limit = 2 * 1024 * 1024  # 2MB
    if value.size > limit:
        raise ValidationError('Image size must be less than 2MB.')


def user_avatar_path(instance, filename):
    """Generate unique file path for user avatar upload."""
    # Generate unique filename
    ext = filename.split('.')[-1]
    unique_filename = f"avatar_{instance.user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # File will be uploaded to MEDIA_ROOT/avatars/user_<id>/<filename>
    return f'avatars/user_{instance.user.id}/{unique_filename}'


class UserProfile(models.Model):
    """Extended user profile information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Upload a profile picture. Max size: 2MB"
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def save(self, *args, **kwargs):
        # Delete old avatar file when a new one is uploaded
        if self.pk:
            try:
                old = UserProfile.objects.get(pk=self.pk)
                if old.avatar and old.avatar != self.avatar:
                    if os.path.isfile(old.avatar.path):
                        os.remove(old.avatar.path)
            except UserProfile.DoesNotExist:
                pass
        
        # Ensure avatar directory exists
        if self.avatar:
            avatar_dir = os.path.dirname(self.avatar.path)
            os.makedirs(avatar_dir, exist_ok=True)
            
        super().save(*args, **kwargs)

    def avatar_url(self):
        """Return avatar URL or default."""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.png'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)
        # Send notification to admin about new user registration
        send_admin_registration_notification(instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


def send_admin_registration_notification(new_user):
    """Send email notification to admin when a new user registers."""
    try:
        admin_users = User.objects.filter(is_superuser=True)

        for admin_user in admin_users:
            subject = f'New User Registration - {new_user.username}'
            context = {
                'admin_username': admin_user.username,
                'new_user': new_user,
                'registration_date': new_user.date_joined.strftime(
                    '%Y-%m-%d %H:%M:%S'
                ),
                'admin_url': 'http://localhost:8000/admin/'
            }

            html_message = render_to_string(
                'admin/new_user_notification.html', context
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_user.email],
                html_message=html_message,
                fail_silently=True,
            )

    except Exception as e:
        # Log the error but don't break user registration
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending admin notification: {e}")


class Artist(models.Model):
    """Artist model representing music artists."""
    ArtistId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=120)

    class Meta:
        db_table = 'Artist'
        managed = True
        ordering = ['Name']

    def __str__(self):
        return self.Name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('artist_detail', args=[str(self.ArtistId)])

    def album_count(self):
        """Return number of albums by this artist."""
        return self.album_set.count()


class Album(models.Model):
    """Album model representing music albums."""
    AlbumId = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=160)
    ArtistId = models.ForeignKey(
        Artist, on_delete=models.CASCADE, db_column='ArtistId'
    )

    class Meta:
        db_table = 'Album'
        managed = False
        ordering = ['Title']

    def __str__(self):
        return self.Title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('album_detail', args=[str(self.AlbumId)])

    def track_count(self):
        """Return number of tracks in this album."""
        return self.track_set.count()

    def duration(self):
        """Return total duration of all tracks in milliseconds."""
        from django.db.models import Sum
        total = self.track_set.aggregate(Sum('Milliseconds'))['Milliseconds__sum']
        return total or 0


class Track(models.Model):
    """Track model representing individual music tracks."""
    TrackId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=200)
    AlbumId = models.ForeignKey(
        Album, on_delete=models.CASCADE, db_column='AlbumId',
        null=True, blank=True
    )
    MediaTypeId = models.IntegerField()
    GenreId = models.IntegerField(null=True, blank=True)
    Composer = models.CharField(max_length=220, null=True, blank=True)
    Milliseconds = models.IntegerField()
    Bytes = models.IntegerField(null=True, blank=True)
    UnitPrice = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Track'
        managed = False
        ordering = ['TrackId']

    def __str__(self):
        return self.Name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('track_detail', args=[str(self.TrackId)])

    def duration_formatted(self):
        """Format milliseconds to MM:SS format."""
        minutes = self.Milliseconds // 60000
        seconds = (self.Milliseconds % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    def artist(self):
        """Get artist from album."""
        if self.AlbumId and self.AlbumId.ArtistId:
            return self.AlbumId.ArtistId
        return None


class Review(models.Model):
    """Review model for user reviews of tracks."""
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'track']
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username
        track_name = self.track.Name
        return f"{username} - {track_name} - {self.rating} stars"

    def get_rating_display(self):
        """Get star representation of rating."""
        return '★' * self.rating