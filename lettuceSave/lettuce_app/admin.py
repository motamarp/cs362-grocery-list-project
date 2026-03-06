from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


# Register your models here.
class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """User admin with profile inline"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_select_related = ('profile',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = ('user', 'dietary_preferences', 'created_at')
    list_filter = ('dietary_preferences', 'created_at')
    search_fields = ('user_username', 'last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'height', 'activity_level')
        }),
        ('Preferences', {
            'fields': ('dietary_preferences', 'favorite_stores')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )