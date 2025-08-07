from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Role, Permission, UserRole, 
    UserSession, UserActivity, PasswordHistory
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1
    verbose_name_plural = 'User Roles'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, UserRoleInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)
    ordering = ('name',)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'permission_type', 'app_label', 'model_name', 'is_active')
    list_filter = ('permission_type', 'app_label', 'model_name', 'is_active')
    search_fields = ('name', 'codename', 'app_label', 'model_name')
    ordering = ('app_label', 'model_name', 'permission_type')


class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active', 'assigned_by', 'assigned_date')
    list_filter = ('role', 'is_active', 'assigned_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'role__name')
    ordering = ('-assigned_date',)


class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'login_time', 'logout_time', 'is_active')
    list_filter = ('is_active', 'login_time', 'logout_time')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'ip_address')
    ordering = ('-login_time',)
    readonly_fields = ('session_key', 'login_time')


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'app_label', 'model_name', 'created_at')
    list_filter = ('activity_type', 'app_label', 'model_name', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'ip_address', 'user_agent')


class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'changed_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('password_hash', 'created_at')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Role, RoleAdmin)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(UserRole, UserRoleAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
admin.site.register(PasswordHistory, PasswordHistoryAdmin)
