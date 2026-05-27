from django import forms
from django.core.exceptions import ValidationError
from .models import Member
from apps.cell_groups.models import CellGroup  # Fixed import


class MemberForm(forms.ModelForm):
    """Form for creating and updating member information."""
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone_number', 'email', 'residential_address', 'occupation',
            'cell_group', 'date_joined_church', 'is_baptized', 
            'baptism_certificate_number', 'baptism_date', 'is_married',
            'marriage_certificate_number', 'marriage_date', 'spouse_name', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'residential_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Residential Address'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Occupation (Optional)'
            }),
            'cell_group': forms.Select(attrs={'class': 'form-control'}),
            'date_joined_church': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_baptized': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baptism_certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Baptism Certificate Number'
            }),
            'baptism_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'is_married': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'marriage_certificate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marriage Certificate Number'
            }),
            'marriage_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'spouse_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Spouse Name'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional Notes'
            }),
        }
    
    def clean(self):
        """Validate member data with conditional checks."""
        cleaned_data = super().clean()
        
        is_baptized = cleaned_data.get('is_baptized')
        baptism_cert = cleaned_data.get('baptism_certificate_number')
        
        if is_baptized and not baptism_cert:
            self.add_error('baptism_certificate_number',
                          'Baptism Certificate Number is required for baptized members.')
        
        is_married = cleaned_data.get('is_married')
        marriage_cert = cleaned_data.get('marriage_certificate_number')
        
        if is_married and not marriage_cert:
            self.add_error('marriage_certificate_number',
                          'Marriage Certificate Number is required for married members.')
        
        return cleaned_data


class MemberSearchForm(forms.Form):
    """Form for searching and filtering members."""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, or phone',
            'autocomplete': 'off'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Member.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_baptized = forms.ChoiceField(
        choices=[
            ('', 'All Members'),
            ('True', 'Baptized'),
            ('False', 'Not Baptized'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_married = forms.ChoiceField(
        choices=[
            ('', 'All Members'),
            ('True', 'Married'),
            ('False', 'Single'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cell_group = forms.ModelChoiceField(
        queryset=CellGroup.objects.filter(is_active=True),
        required=False,
        empty_label='All Cell Groups',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    age_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'From Age',
            'min': '0'
        })
    )
    age_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'To Age',
            'min': '0'
        })
    )
    ordering = forms.ChoiceField(
        choices=[
            ('-updated_at', 'Recently Updated'),
            ('last_name', 'Name (A-Z)'),
            ('-last_name', 'Name (Z-A)'),
            ('date_of_birth', 'Age (Youngest First)'),
            ('-date_of_birth', 'Age (Oldest First)'),
            ('date_joined_church', 'Oldest Members First'),
            ('-date_joined_church', 'Newest Members First'),
        ],
        required=False,
        initial='-updated_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class CellGroupForm(forms.ModelForm):
    """Form for creating and updating cell groups."""
    
    class Meta:
        model = CellGroup
        fields = ['name', 'location', 'description', 'leader', 'meeting_day', 'meeting_time']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cell Group Name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Location/Area'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Group Description'
            }),
            'leader': forms.Select(attrs={'class': 'form-control'}),
            'meeting_day': forms.Select(attrs={'class': 'form-control'}),
            'meeting_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show users with leader role
        from apps.accounts.models import CustomUser
        self.fields['leader'].queryset = CustomUser.objects.filter(
            role='leader',
            is_active_user=True
        )
        self.fields['leader'].required = False
        self.fields['leader'].empty_label = 'No Leader Assigned'


class BulkMemberActionForm(forms.Form):
    """Form for bulk member actions."""
    
    ACTION_CHOICES = [
        ('transfer_group', 'Transfer to Cell Group'),
        ('mark_baptized', 'Mark as Baptized'),
        ('mark_married', 'Mark as Married'),
        ('deactivate', 'Deactivate Members'),
        ('activate', 'Activate Members'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    target_cell_group = forms.ModelChoiceField(
        queryset=CellGroup.objects.filter(is_active=True),
        required=False,
        empty_label='Select Cell Group',
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Required if action is "Transfer to Cell Group"'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        target_cell_group = cleaned_data.get('target_cell_group')
        
        if action == 'transfer_group' and not target_cell_group:
            self.add_error('target_cell_group', 
                          'Target cell group is required for transfer action.')
        
        return cleaned_data


class MemberImportForm(forms.Form):
    """Form for importing members from CSV/Excel."""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        }),
        help_text='Upload CSV or Excel file'
    )
    cell_group = forms.ModelChoiceField(
        queryset=CellGroup.objects.filter(is_active=True),
        required=False,
        empty_label='Assign to Cell Group (Optional)',
        widget=forms.Select(attrs={'class': 'form-control'})
    )