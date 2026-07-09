from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Zone
from apps.cell_groups.models import CellGroup
from apps.members.models import Member


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone_leader', 'cell_group_count_display', 'member_count_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'zone_leader__first_name', 'zone_leader__last_name']
    readonly_fields = ['created_at', 'updated_at', 'cell_group_count_display', 'member_count_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Leadership', {
            'fields': ('zone_leader',),
            'description': 'Assign a zone leader to manage this zone'
        }),
        ('Statistics', {
            'fields': ('cell_group_count_display', 'member_count_display'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_zones', 'deactivate_zones']
    
    def cell_group_count_display(self, obj):
        """Display cell group count with link."""
        count = obj.cell_groups.filter(is_active=True).count()
        url = reverse('admin:cell_groups_cellgroup_changelist') + f'?zone__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    cell_group_count_display.short_description = 'Cell Groups'
    
    def member_count_display(self, obj):
        """Display member count."""
        count = Member.objects.filter(
            cell_group__zone=obj,
            cell_group__is_active=True,
            member_status=Member.ACTIVE
        ).count()
        return count
    member_count_display.short_description = 'Active Members'
    
    def activate_zones(self, request, queryset):
        """Activate selected zones."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} zones activated successfully.')
    activate_zones.short_description = 'Activate selected zones'
    
    def deactivate_zones(self, request, queryset):
        """Deactivate selected zones."""
        # Check if zones have cell groups before deactivating
        for zone in queryset:
            if zone.cell_groups.filter(is_active=True).exists():
                self.message_user(
                    request, 
                    f'Cannot deactivate zone "{zone.name}" - it has active cell groups.',
                    level='ERROR'
                )
                return
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} zones deactivated successfully.')
    deactivate_zones.short_description = 'Deactivate selected zones'
    
    def save_model(self, request, obj, form, change):
        """Log zone creation/update."""
        if not change:
            # New zone created
            from apps.activity_logs.models import ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='create',
                description=f'Created zone: {obj.name}'
            )
        else:
            # Zone updated
            from apps.activity_logs.models import ActivityLog
            ActivityLog.objects.create(
                user=request.user,
                action='update',
                description=f'Updated zone: {obj.name}'
            )
        super().save_model(request, obj, form, change)