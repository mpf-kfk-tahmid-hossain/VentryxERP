from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from core.models import TimeStampedModel, Address


class UserProfile(TimeStampedModel):
    """
    Extended user profile with additional ERP-specific fields
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    is_active = models.BooleanField(default=True)
    
    # Address relationship
    addresses = models.ManyToManyField(Address, blank=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email


class Role(TimeStampedModel):
    """
    Custom role model for RBAC (Role-Based Access Control)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField('Permission', blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Permission(TimeStampedModel):
    """
    Custom permission model for fine-grained access control
    """
    PERMISSION_TYPES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    app_label = models.CharField(max_length=100)  # e.g., 'finance', 'inventory'
    model_name = models.CharField(max_length=100)  # e.g., 'invoice', 'product'
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['app_label', 'model_name', 'permission_type']
        unique_together = ['app_label', 'model_name', 'permission_type']
    
    def __str__(self):
        return f"{self.app_label}.{self.model_name}.{self.permission_type}"
    
    @property
    def full_codename(self):
        return f"{self.app_label}.{self.codename}"


class UserRole(TimeStampedModel):
    """
    Many-to-many relationship between users and roles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='role_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'role']
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class UserSession(TimeStampedModel):
    """
    Track user sessions for security and audit purposes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class UserActivity(TimeStampedModel):
    """
    Track user activities for audit trail
    """
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.created_at}"


class PasswordHistory(TimeStampedModel):
    """
    Track password history for security compliance
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=255)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='password_changes')
    
    class Meta:
        verbose_name_plural = "Password History"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


# Signal handlers for automatic profile creation
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
