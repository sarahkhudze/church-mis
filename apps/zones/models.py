from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    zone_leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_zones',
        limit_choices_to={'role__in': ['admin', 'zone_leader']}
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Zone'
        verbose_name_plural = 'Zones'

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Get total active members in this zone."""
        from apps.members.models import Member
        return Member.objects.filter(
            cell_group__zone=self,
            cell_group__is_active=True,
            member_status=Member.ACTIVE
        ).count()

    @property
    def cell_group_count(self):
        """Get total active cell groups in this zone."""
        return self.cell_groups.filter(is_active=True).count()

    @property
    def attendance_summary(self):
        """Get attendance summary for the zone."""
        from apps.members.models import Member
        members = Member.objects.filter(
            cell_group__zone=self,
            cell_group__is_active=True
        )
        return {
            'active_members': members.filter(member_status=Member.ACTIVE).count(),
            'inactive_members': members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count(),
            'follow_up_required': members.filter(follow_up_required=True).count(),
        }