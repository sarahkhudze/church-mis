from django.contrib import admin
from .models import ActivityLog


class ActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for ActivityLog model."""
    
    list_display = ('user', 'action', 'entity_type', 'description', 'timestamp')
    list_filter = ('action', 'entity_type', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('user', 'action', 'entity_type', 'entity_id', 
                       'description', 'ip_address', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('user', 'action', 'entity_type', 'entity_id', 'description')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual addition of activity logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of activity logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make activity logs read-only."""
        return False


admin.site.register(ActivityLog, ActivityLogAdmin)
