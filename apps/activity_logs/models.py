from django.db import models
from django.utils import timezone


class ActivityLog(models.Model):
    """Model for tracking user activities and system actions."""
    
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('search', 'Search'),
        ('import', 'Import'),
        ('other', 'Other'),
    ]
    
    ENTITY_TYPES = [
        ('member', 'Member'),
        ('cell_group', 'Cell Group'),
        ('user', 'User'),
        ('report', 'Report'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='activity_logs',
        help_text='User who performed the action'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Type of action performed'
    )
    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPES,
        help_text='Type of entity affected'
    )
    entity_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID of the affected entity'
    )
    description = models.TextField(
        help_text='Detailed description of the action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address from which action was performed'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text='Browser/client information'
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'activity_logs_activitylog'
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['entity_type']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} ({self.timestamp})"
    
    @classmethod
    def log_action(cls, user, action, entity_type, description, 
                   entity_id=None, ip_address=None, user_agent=None):
        """Create an activity log entry."""
        return cls.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
