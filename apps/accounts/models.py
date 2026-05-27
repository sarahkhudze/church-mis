from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.conf import settings


class CustomUser(AbstractUser):
    """Custom User model extending Django's AbstractUser."""
    
    ROLE_CHOICES = [
        ('admin', 'Church Administrator'),
        ('leader', 'Cell Group Leader'),
        ('viewer', 'Viewer (Read-only)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('inactive', 'Inactive'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer',
        help_text='User role in the system'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Account approval status'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='User contact number'
    )
    # Use string reference to avoid circular import
    assigned_cell_group = models.ForeignKey(
        'cell_groups.CellGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leaders',
        help_text='Cell group assigned to this leader'
    )
    is_active_user = models.BooleanField(
        default=True,
        help_text='Whether this user account is active'
    )
    
    # Approval fields
    application_reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for applying as a cell group leader'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the user was approved'
    )
    approved_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_users',
        help_text='Admin who approved this user'
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for rejection if applicable'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active_user']),
        ]
    
    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.get_role_display()}) - {self.get_status_display()}"
        return f"{self.username} ({self.get_role_display()}) - {self.get_status_display()}"
    
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == 'admin'
    
    def is_cell_leader(self):
        """Check if user is a cell group leader."""
        return self.role == 'leader'
    
    def is_approved(self):
        """Check if user account is approved."""
        return self.status == 'approved'
    
    def is_pending(self):
        """Check if user account is pending approval."""
        return self.status == 'pending'
    
    def can_manage_all_members(self):
        """Check if user can manage all members (admin only)."""
        return self.is_admin()
    
    def get_managed_members(self):
        """Get members this user can manage."""
        from apps.members.models import Member  # Import here to avoid circular import
        if self.is_admin():
            return Member.objects.filter(is_active=True)
        elif self.is_cell_leader() and self.is_approved() and self.assigned_cell_group:
            return self.assigned_cell_group.members.filter(is_active=True)
        return Member.objects.none()
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_role_display(self):
        """Get the display name for the user's role."""
        return dict(self.ROLE_CHOICES).get(self.role, self.role)
    
    def get_status_display(self):
        """Get the display name for the user's status."""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)