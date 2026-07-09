from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.utils import timezone
from django.conf import settings
from datetime import date


class MemberQuerySet(models.QuerySet):
    def active(self):
        return self.filter(member_status='active')

    def inactive(self):
        return self.filter(member_status__in=['left', 'deceased'])


class MemberManager(models.Manager.from_queryset(MemberQuerySet)):
    pass


class Member(models.Model):
    """Model for managing church members."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    ACTIVE = 'active'
    LEFT = 'left'
    DECEASED = 'deceased'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (LEFT, 'Left'),
        (DECEASED, 'Deceased'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    residential_address = models.TextField()
    occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # Church Information - Reference to CellGroup from cell_groups app
    cell_group = models.ForeignKey(
        'cell_groups.CellGroup',  # Changed to reference cell_groups app
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text='Cell group this member belongs to'
    )
    date_joined_church = models.DateField(default=date.today)
    
    # Baptism Information
    is_baptized = models.BooleanField(default=False)
    baptism_certificate_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text='Required if member is baptized'
    )
    baptism_date = models.DateField(blank=True, null=True)
    
    # Marriage Information
    is_married = models.BooleanField(default=False)
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default='single',
        help_text='Marital status of the member'
    )
    marriage_certificate_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        help_text='Required if member is married'
    )
    marriage_date = models.DateField(blank=True, null=True)
    spouse_name = models.CharField(max_length=200, blank=True, null=True)
    
    # System Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='members_created',
        help_text='User who created this member record'
    )
    is_active = models.BooleanField(default=True)
    member_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        help_text='Current membership status'
    )
    notes = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_note = models.TextField(blank=True, null=True)
    last_attendance_date = models.DateField(blank=True, null=True)
    last_follow_up_date = models.DateField(blank=True, null=True)

    objects = MemberManager()
    
    class Meta:
        db_table = 'members_member'
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['cell_group']),
            models.Index(fields=['is_baptized']),
            models.Index(fields=['is_married']),
            models.Index(fields=['gender']),
            models.Index(fields=['date_of_birth']),
            models.Index(fields=['member_status']),
        ]
        unique_together = [('phone_number', 'email')]
    
    def save(self, *args, **kwargs):
        """Override save to keep status and marital flags consistent."""
        if self.is_married:
            self.marital_status = 'married'
        else:
            self.marital_status = 'single'

        if not self.member_status:
            self.member_status = self.ACTIVE if self.is_active else self.LEFT

        self.is_active = self.member_status == self.ACTIVE
        self.follow_up_required = self.update_follow_up_status()
        super().save(*args, **kwargs)
    
    def __str__(self):
        cell_group_name = self.cell_group.name if self.cell_group else 'No Cell Group'
        return f"{self.get_full_name()} - {cell_group_name}"
    
    def get_full_name(self):
        """Return member's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active_member(self):
        return self.member_status == self.ACTIVE

    @property
    def age(self):
        """Calculate member's age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def update_follow_up_status(self, reference_date=None):
        """Flag members who have missed home church attendance for 5+ months."""
        if self.member_status != self.ACTIVE:
            return False
        if not self.last_attendance_date:
            return False
        if reference_date is None:
            reference_date = date.today()
        months_gap = (reference_date.year - self.last_attendance_date.year) * 12 + (
            reference_date.month - self.last_attendance_date.month
        )
        return months_gap >= 5

    @property
    def birthday_this_month(self):
        """Check if member's birthday is this month."""
        today = date.today()
        return self.date_of_birth.month == today.month
    
    def is_birthday_today(self):
        """Check if today is member's birthday."""
        today = date.today()
        return (self.date_of_birth.month == today.month and 
                self.date_of_birth.day == today.day)
    
    def clean(self):
        """Validate member data."""
        from django.core.exceptions import ValidationError
        
        if self.is_baptized and not self.baptism_certificate_number:
            raise ValidationError({
                'baptism_certificate_number': "Baptism Certificate Number is required for baptized members."
            })
        
        if self.is_married and not self.marriage_certificate_number:
            raise ValidationError({
                'marriage_certificate_number': "Marriage Certificate Number is required for married members."
            })


class AttendanceRecord(models.Model):
    """Attendance captured for a cell-group meeting."""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_records')
    cell_group = models.ForeignKey('cell_groups.CellGroup', on_delete=models.CASCADE, related_name='attendance_records')
    meeting_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'members_attendance_record'
        ordering = ['-meeting_date', '-created_at']
        unique_together = [('member', 'cell_group', 'meeting_date')]

    def __str__(self):
        return f"{self.member.get_full_name()} - {self.meeting_date} - {self.status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'present' and self.meeting_date:
            self.member.last_attendance_date = self.meeting_date
            self.member.follow_up_required = self.member.update_follow_up_status(reference_date=self.meeting_date)
            self.member.save(update_fields=['last_attendance_date', 'follow_up_required'])