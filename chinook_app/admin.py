from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
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
        'custom_question_text'
    ]
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, SecurityQuestionInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'group_display', 'user_actions']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    actions = ['assign_admin_group', 'assign_superuser_group', 'assign_staff_group', 'assign_regular_group']
    
    def group_display(self, obj):
        groups = obj.groups.all()
        if groups:
            return ", ".join([group.name for group in groups])
        return "No Group"
    group_display.short_description = 'Groups'
    
    def user_actions(self, obj):
        if obj == self.user:  # Prevent admin from modifying their own permissions
            return "Current User"
        
        links = []
        if not obj.is_superuser:
            links.append(f'<a href="{reverse("admin:assign_group", args=[obj.id, "admin"])}">Make Admin</a>')
        if not obj.groups.filter(name='Superuser').exists():
            links.append(f'<a href="{reverse("admin:assign_group", args=[obj.id, "superuser"])}">Make Superuser</a>')
        if not obj.groups.filter(name='Staff').exists():
            links.append(f'<a href="{reverse("admin:assign_group", args=[obj.id, "staff"])}">Make Staff</a>')
        if not obj.groups.filter(name='Regular').exists():
            links.append(f'<a href="{reverse("admin:assign_group", args=[obj.id, "regular"])}">Make Regular</a>')
        
        return format_html(' | '.join(links)) if links else "No actions"
    user_actions.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:user_id>/assign-group/<str:group_type>/', 
                 self.admin_site.admin_view(self.assign_group_view), 
                 name='assign_group'),
        ]
        return custom_urls + urls
    
    def assign_group_view(self, request, user_id, group_type):
        try:
            user = User.objects.get(id=user_id)
            target_user = request.user
            
            # Security checks
            if user == target_user:
                messages.error(request, 'You cannot modify your own group assignments.')
                return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
            
            if not target_user.is_superuser:
                messages.error(request, 'Only superusers can modify user groups.')
                return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
            
            # Clear existing groups and assign new one
            user.groups.clear()
            
            if group_type == 'admin':
                admin_group, created = Group.objects.get_or_create(name='Admin')
                user.groups.add(admin_group)
                user.is_staff = True
                user.is_superuser = True
                messages.success(request, f'User {user.username} has been assigned to Admin group with full permissions.')
            
            elif group_type == 'superuser':
                superuser_group, created = Group.objects.get_or_create(name='Superuser')
                user.groups.add(superuser_group)
                user.is_staff = True
                user.is_superuser = True
                messages.success(request, f'User {user.username} has been assigned to Superuser group.')
            
            elif group_type == 'staff':
                staff_group, created = Group.objects.get_or_create(name='Staff')
                user.groups.add(staff_group)
                user.is_staff = True
                user.is_superuser = False
                messages.success(request, f'User {user.username} has been assigned to Staff group.')
            
            elif group_type == 'regular':
                regular_group, created = Group.objects.get_or_create(name='Regular')
                user.groups.add(regular_group)
                user.is_staff = False
                user.is_superuser = False
                messages.success(request, f'User {user.username} has been assigned to Regular group.')
            
            user.save()
            
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
    
    def assign_admin_group(self, request, queryset):
        admin_group, created = Group.objects.get_or_create(name='Admin')
        for user in queryset:
            if user != request.user:  # Prevent self-modification
                user.groups.clear()
                user.groups.add(admin_group)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        self.message_user(request, f'Successfully assigned {queryset.count()} users to Admin group.')
    assign_admin_group.short_description = "Assign selected users to Admin group"
    
    def assign_superuser_group(self, request, queryset):
        superuser_group, created = Group.objects.get_or_create(name='Superuser')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(superuser_group)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        self.message_user(request, f'Successfully assigned {queryset.count()} users to Superuser group.')
    assign_superuser_group.short_description = "Assign selected users to Superuser group"
    
    def assign_staff_group(self, request, queryset):
        staff_group, created = Group.objects.get_or_create(name='Staff')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(staff_group)
                user.is_staff = True
                user.is_superuser = False
                user.save()
        self.message_user(request, f'Successfully assigned {queryset.count()} users to Staff group.')
    assign_staff_group.short_description = "Assign selected users to Staff group"
    
    def assign_regular_group(self, request, queryset):
        regular_group, created = Group.objects.get_or_create(name='Regular')
        for user in queryset:
            if user != request.user:
                user.groups.clear()
                user.groups.add(regular_group)
                user.is_staff = False
                user.is_superuser = False
                user.save()
        self.message_user(request, f'Successfully assigned {queryset.count()} users to Regular group.')
    assign_regular_group.short_description = "Assign selected users to Regular group"


class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count']
    filter_horizontal = ['permissions']
    
    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Number of Users'


# Register the custom admins
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'birth_date']
    list_filter = ['location']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'location', 'bio']
    readonly_fields = ['user']
    
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
class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_1', 'question_2']
    list_filter = ['question_1', 'question_2', 'question_3']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user']
    
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
                'custom_question_text'
            )
        }),
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['ArtistId', 'Name']
    list_filter = ['Name']
    search_fields = ['Name']
    ordering = ['Name']


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['AlbumId', 'Title', 'ArtistId']
    list_filter = ['ArtistId']
    search_fields = ['Title', 'ArtistId__Name']
    raw_id_fields = ['ArtistId']
    ordering = ['Title']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['TrackId', 'Name', 'AlbumId', 'Composer', 'Milliseconds', 'UnitPrice']
    list_filter = ['AlbumId', 'GenreId', 'MediaTypeId']
    search_fields = ['Name', 'Composer', 'AlbumId__Title']
    raw_id_fields = ['AlbumId']
    list_per_page = 50
    
    def duration_formatted(self, obj):
        return obj.duration_formatted()
    duration_formatted.short_description = 'Duration'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
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