from django.contrib import admin
from .models import Member
from apps.cell_groups.models import CellGroup  # Import CellGroup from the correct app


class CellGroupAdmin(admin.ModelAdmin):
    """Admin interface for CellGroup model."""
    
    list_display = ('name', 'location', 'leader', 'member_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'location', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Group Information', {
            'fields': ('name', 'location', 'description', 'leader')
        }),
        ('Meeting Information', {
            'fields': ('meeting_day', 'meeting_time'),
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        """Display member count for the cell group."""
        return obj.member_count
    member_count.short_description = 'Member Count'


class MemberAdmin(admin.ModelAdmin):
    """Admin interface for Member model."""
    
    list_display = ('get_full_name', 'gender', 'cell_group', 'is_baptized', 'is_married', 'is_active', 'created_at')
    list_filter = ('gender', 'is_baptized', 'is_married', 'is_active', 'cell_group', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    ordering = ('last_name', 'first_name')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'occupation')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'residential_address')
        }),
        ('Church Information', {
            'fields': ('cell_group', 'date_joined_church')
        }),
        ('Baptism Information', {
            'fields': ('is_baptized', 'baptism_certificate_number', 'baptism_date')
        }),
        ('Marriage Information', {
            'fields': ('is_married', 'marriage_certificate_number', 'marriage_date', 'spouse_name')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'is_active', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        """Display member's full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Name'
    
    def save_model(self, request, obj, form, change):
        """Set created_by field when creating new member."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Register the models
admin.site.register(CellGroup, CellGroupAdmin)
admin.site.register(Member, MemberAdmin)