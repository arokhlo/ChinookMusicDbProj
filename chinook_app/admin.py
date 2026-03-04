from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.core.exceptions import PermissionDenied
from .models import UserProfile, Artist, Album, Track, Review, SecurityQuestion


# Unregister the default User admin if it's registered
admin.site.unregister(User)
admin.site.unregister(Group)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ['avatar', 'bio', 'location', 'birth_date']
    extra = 0


class SecurityQuestionInline(admin.StackedInline):
    model = SecurityQuestion
    can_delete = False
    verbose_name_plural = 'Security Questions'
    fields = [
        'question_1', 'answer_1',
        'question_2', 'answer_2',
        'question_3', 'answer_3',
        'question_4', 'answer_4',
        'question_5', 'answer_5',
    ]
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, SecurityQuestionInline]
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_superuser', 'is_active',
        'date_joined', 'group_display', 'user_actions'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active',
        'groups', 'date_joined'
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    actions = [
        'assign_admin_group', 'assign_superuser_group',
        'assign_staff_group', 'assign_regular_group'
    ]

    def is_protected_user(self, obj):
        """Check if the user is protected (username is 'admin')."""
        return obj.username.lower() == 'admin'

    def has_module_permission(self, request):
        """Check if user has permission to access this admin module."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # Allow the protected admin user to access admin
        if request.user.username.lower() == 'admin':
            return True

        # Only allow Admin group and actual Django superusers
        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def has_view_permission(self, request, obj=None):
        """Check if user has permission to view users."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # If the requesting user is the protected admin user
        if request.user.username.lower() == 'admin':
            return True

        # If viewing a specific user object, check if it's protected
        if obj and self.is_protected_user(obj):
            # No one can view the protected admin user (except admin itself)
            if request.user.username.lower() != 'admin':
                return False

        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def has_change_permission(self, request, obj=None):
        """Check if user has permission to change users."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # If the requesting user is the protected admin user
        if request.user.username.lower() == 'admin':
            # Allow admin to change other users but not itself
            if obj and self.is_protected_user(obj):
                return False
            return True

        # If changing a specific user object, check if it's protected
        if obj and self.is_protected_user(obj):
            # No one can modify the protected admin user
            return False

        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def has_delete_permission(self, request, obj=None):
        """Check if user has permission to delete users."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # If the requesting user is the protected admin user
        if request.user.username.lower() == 'admin':
            # Allow admin to delete other users but not itself
            if obj and self.is_protected_user(obj):
                return False
            return True

        # If deleting a specific user object, check if it's protected
        if obj and self.is_protected_user(obj):
            # No one can delete the protected admin user
            return False

        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def has_add_permission(self, request):
        """Check if user has permission to add users."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # Allow the protected admin user to add users
        if request.user.username.lower() == 'admin':
            return True

        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def get_queryset(self, request):
        """
        Store the current user for use in other methods.

        Filter out protected users except when the protected admin is viewing.
        """
        self._current_user = request.user
        
        # If the protected admin user is viewing, show all users
        if request.user.username.lower() == 'admin':
            return super().get_queryset(request)
        
        # Otherwise, exclude protected admin user from queryset
        return super().get_queryset(request).exclude(username__iexact='admin')

    def group_display(self, obj):
        """Display user groups in admin list."""
        groups = obj.groups.all()
        if groups:
            return ", ".join([group.name for group in groups])
        return "No Group"
    group_display.short_description = 'Groups'

    def user_actions(self, obj):
        """Display user actions in admin list display."""
        # Check if we have the current user and prevent self-modification
        if hasattr(self, '_current_user') and obj == self._current_user:
            return "Current User - No actions available"

        # Don't show actions for protected admin user (unless admin is viewing)
        if self.is_protected_user(obj):
            if not (hasattr(self, '_current_user') and self._current_user.username.lower() == 'admin'):
                return "Protected User - No actions available"

        links = []
        admin_url = reverse("admin:assign_group", args=[obj.id, "admin"])
        superuser_url = reverse(
            "admin:assign_group", args=[obj.id, "superuser"]
        )
        staff_url = reverse("admin:assign_group", args=[obj.id, "staff"])
        regular_url = reverse("admin:assign_group", args=[obj.id, "regular"])

        # Check if user is already in the group
        if not obj.is_superuser:
            links.append(f'<a href="{admin_url}">Make Admin</a>')
        if not obj.groups.filter(name='Superuser').exists():
            links.append(f'<a href="{superuser_url}">Make Superuser</a>')
        if not obj.groups.filter(name='Staff').exists():
            links.append(f'<a href="{staff_url}">Make Staff</a>')
        if not obj.groups.filter(name='Regular').exists():
            links.append(f'<a href="{regular_url}">Make Regular</a>')

        return format_html(' | '.join(links)) if links else "No actions"
    user_actions.short_description = 'Actions'

    def get_urls(self):
        """Add custom URLs for group assignment."""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/assign-group/<str:group_type>/',
                self.admin_site.admin_view(self.assign_group_view),
                name='assign_group'
            ),
        ]
        return custom_urls + urls

    def assign_group_view(self, request, user_id, group_type):
        """Handle group assignment via custom URL."""
        # Check permission first
        # Allow protected admin user
        if not (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
            or request.user.username.lower() == 'admin'
        ):
            raise PermissionDenied

        try:
            user = User.objects.get(id=user_id)

            # Prevent modifying protected admin user (except by admin itself)
            if user.username.lower() == 'admin' and request.user.username.lower() != 'admin':
                msg = 'Cannot modify the protected admin user.'
                messages.error(request, msg)
                url = reverse('admin:auth_user_changelist')
                return HttpResponseRedirect(url)

            target_user = request.user

            # Security checks
            if user == target_user:
                msg = 'You cannot modify your own group assignments.'
                messages.error(request, msg)
                url = reverse('admin:auth_user_changelist')
                return HttpResponseRedirect(url)

            # Check if user has permission (superuser or admin group or protected admin)
            if not (target_user.is_superuser or target_user.username.lower() == 'admin'):
                msg = 'Only superusers can modify user groups.'
                messages.error(request, msg)
                url = reverse('admin:auth_user_changelist')
                return HttpResponseRedirect(url)

            # Clear existing groups and assign new one
            user.groups.clear()

            if group_type == 'admin':
                group, created = Group.objects.get_or_create(name='Admin')
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = True
                msg = (
                    f'User {user.username} assigned to '
                    'Admin group with full permissions.'
                )
                messages.success(request, msg)

            elif group_type == 'superuser':
                group, created = Group.objects.get_or_create(name='Superuser')
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = True
                msg = f'User {user.username} assigned to Superuser group.'
                messages.success(request, msg)

            elif group_type == 'staff':
                group, created = Group.objects.get_or_create(name='Staff')
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = False
                msg = f'User {user.username} assigned to Staff group.'
                messages.success(request, msg)

            elif group_type == 'regular':
                group, created = Group.objects.get_or_create(name='Regular')
                user.groups.add(group)
                user.is_staff = False
                user.is_superuser = False
                msg = f'User {user.username} assigned to Regular group.'
                messages.success(request, msg)

            user.save()

        except User.DoesNotExist:
            messages.error(request, 'User not found.')

        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))

    def assign_admin_group(self, request, queryset):
        """Assign selected users to Admin group."""
        # Check permission
        if not (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
            or request.user.username.lower() == 'admin'
        ):
            raise PermissionDenied

        # Filter out protected admin user unless admin is doing it
        if request.user.username.lower() != 'admin':
            queryset = queryset.exclude(username__iexact='admin')

        group, created = Group.objects.get_or_create(name='Admin')
        for user in queryset:
            if user != request.user:  # Prevent self-modification
                user.groups.clear()
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        count = queryset.count()
        msg = f'Successfully assigned {count} users to Admin group.'
        self.message_user(request, msg)
    assign_admin_group.short_description = "Assign to Admin group"

    def assign_superuser_group(self, request, queryset):
        """Assign selected users to Superuser group."""
        # Check permission
        if not (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
            or request.user.username.lower() == 'admin'
        ):
            raise PermissionDenied

        # Filter out protected admin user unless admin is doing it
        if request.user.username.lower() != 'admin':
            queryset = queryset.exclude(username__iexact='admin')

        group, created = Group.objects.get_or_create(name='Superuser')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        count = queryset.count()
        msg = f'Successfully assigned {count} users to Superuser group.'
        self.message_user(request, msg)
    assign_superuser_group.short_description = "Assign to Superuser group"

    def assign_staff_group(self, request, queryset):
        """Assign selected users to Staff group."""
        # Check permission
        if not (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
            or request.user.username.lower() == 'admin'
        ):
            raise PermissionDenied

        # Filter out protected admin user unless admin is doing it
        if request.user.username.lower() != 'admin':
            queryset = queryset.exclude(username__iexact='admin')

        group, created = Group.objects.get_or_create(name='Staff')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(group)
                user.is_staff = True
                user.is_superuser = False
                user.save()
        count = queryset.count()
        msg = f'Successfully assigned {count} users to Staff group.'
        self.message_user(request, msg)
    assign_staff_group.short_description = "Assign to Staff group"

    def assign_regular_group(self, request, queryset):
        """Assign selected users to Regular group."""
        # Check permission
        if not (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
            or request.user.username.lower() == 'admin'
        ):
            raise PermissionDenied

        # Filter out protected admin user unless admin is doing it
        if request.user.username.lower() != 'admin':
            queryset = queryset.exclude(username__iexact='admin')

        group, created = Group.objects.get_or_create(name='Regular')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(group)
                user.is_staff = False
                user.is_superuser = False
                user.save()
        count = queryset.count()
        msg = f'Successfully assigned {count} users to Regular group.'
        self.message_user(request, msg)
    assign_regular_group.short_description = "Assign to Regular group"


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count']
    filter_horizontal = ['permissions']

    def has_module_permission(self, request):
        """Check if user has permission to access groups admin."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # Allow the protected admin user
        if request.user.username.lower() == 'admin':
            return True

        # Only allow Admin group and actual Django superusers
        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Number of Users'


# Register the custom admins
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)


class BaseAdmin(admin.ModelAdmin):
    """Base admin class with permission checks for all models."""

    def has_module_permission(self, request):
        """Check if user has permission to access this admin module."""
        if not request.user.is_authenticated:
            return False

        # Superuser group members cannot access admin
        if request.user.groups.filter(name='Superuser').exists():
            return False

        # Allow the protected admin user
        if request.user.username.lower() == 'admin':
            return True

        # Only allow Admin group and actual Django superusers
        return (
            request.user.groups.filter(name='Admin').exists()
            or request.user.is_superuser
        )

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return self.has_module_permission(request)


@admin.register(UserProfile)
class UserProfileAdmin(BaseAdmin):
    list_display = ['user', 'location', 'birth_date']
    list_filter = ['location']
    search_fields = [
        'user__username', 'user__first_name',
        'user__last_name', 'location', 'bio'
    ]
    readonly_fields = ['user']

    def get_queryset(self, request):
        """Exclude profiles of protected users except when admin is viewing."""
        queryset = super().get_queryset(request)
        # If the protected admin user is viewing, show all profiles
        if request.user.username.lower() == 'admin':
            return queryset
        # Otherwise, exclude protected admin user's profile
        return queryset.exclude(user__username__iexact='admin')

    def has_view_permission(self, request, obj=None):
        """Check if user can view this profile."""
        if not super().has_view_permission(request, obj):
            return False

        # Allow admin to view all profiles including protected one
        if request.user.username.lower() == 'admin':
            return True

        # Don't allow viewing profile of protected admin user
        if obj and obj.user.username.lower() == 'admin':
            return False

        return True

    def has_change_permission(self, request, obj=None):
        """Check if user can change this profile."""
        if not super().has_change_permission(request, obj):
            return False

        # Allow admin to change other profiles but not protected one
        if request.user.username.lower() == 'admin':
            if obj and obj.user.username.lower() == 'admin':
                return False
            return True

        # Don't allow changing profile of protected admin user
        if obj and obj.user.username.lower() == 'admin':
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        """Check if user can delete this profile."""
        if not super().has_delete_permission(request, obj):
            return False

        # Don't allow deleting any profile (including protected one)
        return False

    fieldsets = (
        (None, {
            'fields': ('user', 'avatar')
        }),
        ('Personal Information', {
            'fields': ('bio', 'location', 'birth_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(BaseAdmin):
    list_display = ['user', 'question_1', 'question_2']
    list_filter = ['question_1', 'question_2', 'question_3']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user']

    def get_queryset(self, request):
        """Exclude security questions of protected users except when admin is viewing."""
        queryset = super().get_queryset(request)
        # If the protected admin user is viewing, show all
        if request.user.username.lower() == 'admin':
            return queryset
        # Otherwise, exclude protected admin user's security questions
        return queryset.exclude(user__username__iexact='admin')

    def has_view_permission(self, request, obj=None):
        """Check if user can view security questions."""
        if not super().has_view_permission(request, obj):
            return False

        # Allow admin to view all security questions including protected one
        if request.user.username.lower() == 'admin':
            return True

        # Don't allow viewing security questions of protected admin user
        if obj and obj.user.username.lower() == 'admin':
            return False

        return True

    def has_change_permission(self, request, obj=None):
        """Check if user can change security questions."""
        if not super().has_change_permission(request, obj):
            return False

        # Allow admin to change other security questions but not protected one
        if request.user.username.lower() == 'admin':
            if obj and obj.user.username.lower() == 'admin':
                return False
            return True

        # Don't allow changing security questions of protected admin user
        if obj and obj.user.username.lower() == 'admin':
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        """Check if user can delete security questions."""
        if not super().has_delete_permission(request, obj):
            return False

        # Don't allow deleting any security questions
        return False

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Security Questions', {
            'fields': (
                ('question_1', 'answer_1'),
                ('question_2', 'answer_2'),
                ('question_3', 'answer_3'),
                ('question_4', 'answer_4'),
                ('question_5', 'answer_5'),
            )
        }),
    )


@admin.register(Artist)
class ArtistAdmin(BaseAdmin):
    list_display = ['ArtistId', 'Name']
    list_filter = ['Name']
    search_fields = ['Name']
    ordering = ['Name']


@admin.register(Album)
class AlbumAdmin(BaseAdmin):
    list_display = ['AlbumId', 'Title', 'ArtistId']
    list_filter = ['ArtistId']
    search_fields = ['Title', 'ArtistId__Name']
    raw_id_fields = ['ArtistId']
    ordering = ['Title']


@admin.register(Track)
class TrackAdmin(BaseAdmin):
    list_display = [
        'TrackId', 'Name', 'AlbumId', 'Composer',
        'Milliseconds', 'UnitPrice'
    ]
    list_filter = ['AlbumId', 'GenreId', 'MediaTypeId']
    search_fields = ['Name', 'Composer', 'AlbumId__Title']
    raw_id_fields = ['AlbumId']
    list_per_page = 50

    def duration_formatted(self, obj):
        return obj.duration_formatted()
    duration_formatted.short_description = 'Duration'


@admin.register(Review)
class ReviewAdmin(BaseAdmin):
    list_display = ['user', 'track', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'track__Name', 'comment']
    raw_id_fields = ['user', 'track']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('user', 'track', 'rating')
        }),
        ('Review Content', {
            'fields': ('comment',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )