from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')

    class Meta:
        abstract = True


class Address(TimeStampedModel):
    """
    Reusable Address model for customers, vendors, employees, etc.
    """
    ADDRESS_TYPES = [
        ('billing', 'Billing Address'),
        ('shipping', 'Shipping Address'),
        ('office', 'Office Address'),
        ('home', 'Home Address'),
    ]
    
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='billing')
    street_address = models.CharField(max_length=255)
    street_address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state_province} {self.postal_code}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primary addresses of the same type
        if self.is_primary:
            Address.objects.filter(
                address_type=self.address_type,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Company(TimeStampedModel):
    """
    Company/Organization model for multi-tenant support
    """
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Address relationship
    addresses = models.ManyToManyField(Address, blank=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Document(TimeStampedModel):
    """
    Generic document model for storing files
    """
    DOCUMENT_TYPES = [
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('contract', 'Contract'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def file_extension(self):
        """Get the file extension"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None
    
    @property
    def file_size(self):
        """Get the file size in bytes"""
        if self.file:
            return self.file.size
        return 0
