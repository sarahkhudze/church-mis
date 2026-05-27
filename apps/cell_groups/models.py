from django.db import models
from django.utils import timezone
from django.conf import settings


class CellGroup(models.Model):
    MEETING_DAYS = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday')
    ]
    
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200)
    # Use settings.AUTH_USER_MODEL to reference the user model
    leader = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_cell_group'
    )
    description = models.TextField(blank=True)
    meeting_day = models.CharField(max_length=20, choices=MEETING_DAYS, default='Sunday')
    meeting_time = models.TimeField(null=True, blank=True, default='15:00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'cell_groups'
        verbose_name = 'Cell Group'
        verbose_name_plural = 'Cell Groups'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        """Get the number of members in this cell group."""
        from apps.members.models import Member  # Import here to avoid circular import
        return Member.objects.filter(cell_group=self, is_active=True).count()
    
    @property
    def baptized_count(self):
        """Get the number of baptized members in this cell group."""
        from apps.members.models import Member  # Import here to avoid circular import
        return Member.objects.filter(cell_group=self, is_active=True, is_baptized=True).count()
    
    @property
    def leader_name(self):
        """Get the leader's full name."""
        if self.leader:
            return self.leader.get_full_name()
        return "Not Assigned"


class CellGroupTransfer(models.Model):
    from apps.members.models import Member  # Import here to avoid circular import
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='transfers')
    from_cell_group = models.ForeignKey(
        CellGroup, 
        on_delete=models.CASCADE, 
        related_name='transfers_out'
    )
    to_cell_group = models.ForeignKey(
        CellGroup, 
        on_delete=models.CASCADE, 
        related_name='transfers_in'
    )
    transfer_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='approved_transfers'
    )
    notes = models.TextField(blank=True, help_text='Additional notes about the transfer')
    
    class Meta:
        db_table = 'cell_group_transfers'
        verbose_name = 'Cell Group Transfer'
        verbose_name_plural = 'Cell Group Transfers'
        ordering = ['-transfer_date']
    
    def __str__(self):
        member_name = self.member.full_name if hasattr(self.member, 'full_name') else str(self.member)
        return f"{member_name} moved from {self.from_cell_group.name} to {self.to_cell_group.name} on {self.transfer_date.date()}"