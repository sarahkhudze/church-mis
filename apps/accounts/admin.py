from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    
    model = CustomUser
    list_display = ('username', 'email', 'get_full_name', 'role', 'is_active_user', 'created_at')
    list_filter = ('role', 'is_active_user', 'created_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Church Info', {
            'fields': ('role', 'phone_number', 'assigned_cell_group', 'is_active_user')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Church Info', {
            'fields': ('role', 'phone_number', 'assigned_cell_group', 'is_active_user')
        }),
    )
    ordering = ('-created_at',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_full_name(self, obj):
        """Display user's full name."""
        return obj.get_full_name()
    
    get_full_name.short_description = 'Full Name'


admin.site.register(CustomUser, CustomUserAdmin)
