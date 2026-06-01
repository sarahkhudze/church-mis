from django.db import models
from django.core.validators import URLValidator, EmailValidator
from django.utils import timezone
from datetime import date


class Member(models.Model):
    """Model for managing church members."""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
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
    notes = models.TextField(blank=True, null=True)
    
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
        ]
        unique_together = [('phone_number', 'email')]
    
    def save(self, *args, **kwargs):
        """Override save to set marital_status based on is_married."""
        if self.is_married:
            self.marital_status = 'married'
        else:
            self.marital_status = 'single'
        super().save(*args, **kwargs)
    
    def __str__(self):
        cell_group_name = self.cell_group.name if self.cell_group else 'No Cell Group'
        return f"{self.get_full_name()} - {cell_group_name}"
    
    def get_full_name(self):
        """Return member's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate member's age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
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