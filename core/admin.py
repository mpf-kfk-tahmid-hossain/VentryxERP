from django.contrib import admin
from .models import Address, Company, Document


class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'state_province', 'postal_code', 'country', 'address_type', 'is_primary', 'is_active')
    list_filter = ('address_type', 'country', 'is_primary', 'is_active', 'created_at')
    search_fields = ('street_address', 'city', 'state_province', 'postal_code')
    ordering = ('-is_primary', '-created_at')
    readonly_fields = ('created_at', 'updated_at')


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_name', 'tax_id', 'phone', 'email', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'legal_name', 'tax_id', 'email')
    ordering = ('name',)
    filter_horizontal = ('addresses',)
    readonly_fields = ('created_at', 'updated_at')


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'file', 'is_active', 'created_at')
    list_filter = ('document_type', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'file_extension', 'file_size')


admin.site.register(Address, AddressAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Document, DocumentAdmin)
