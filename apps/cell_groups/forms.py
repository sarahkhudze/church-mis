from django import forms
from .models import CellGroup
from apps.zones.models import Zone
from django.contrib.auth import get_user_model

User = get_user_model()


class CellGroupForm(forms.ModelForm):
    class Meta:
        model = CellGroup
        fields = [
            'name', 'description', 'zone', 'leader', 
            'meeting_day', 'meeting_time', 'meeting_frequency', 'meeting_days',
            'location', 'approval_status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'meeting_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Friday - Intercession, Sunday - Bible Study'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_day': forms.Select(attrs={'class': 'form-select'}),
            'meeting_frequency': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'approval_status': forms.Select(attrs={'class': 'form-select'}),
            'leader': forms.Select(attrs={'class': 'form-select'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set zone automatically if user is a zone leader
        if user and hasattr(user, 'zone') and user.zone:
            # Auto-set the zone to the user's assigned zone
            self.fields['zone'].initial = user.zone
            self.fields['zone'].widget.attrs['readonly'] = True
            self.fields['zone'].required = False
        else:
            # Only show active zones for non-zone-leaders
            self.fields['zone'].queryset = Zone.objects.filter(is_active=True)
            self.fields['zone'].required = False
            self.fields['zone'].empty_label = 'Select a zone...'
        
        # Make leader optional
        self.fields['leader'].required = False
        self.fields['leader'].empty_label = 'Select a leader...'
        
        # Restrict leader choices based on user role
        if user and not user.is_admin():
            # Non-admins can only see themselves as potential leaders
            self.fields['leader'].queryset = User.objects.filter(id=user.id)
        
        # Add help text
        self.fields['zone'].help_text = 'Assign this cell group to a zone (auto-assigned for zone leaders)'
        self.fields['meeting_frequency'].help_text = 'How many times per week the group meets'
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for duplicates, excluding current instance
            existing = CellGroup.objects.filter(
                name__iexact=name,
                is_active=True
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A cell group with this name already exists.')
        return name
    
    def clean(self):
        cleaned_data = super().clean()
        meeting_day = cleaned_data.get('meeting_day')
        meeting_time = cleaned_data.get('meeting_time')
        meeting_frequency = cleaned_data.get('meeting_frequency')
        meeting_days = cleaned_data.get('meeting_days')
        
        if meeting_day and not meeting_time:
            self.add_error('meeting_time', 'Please specify a meeting time.')
        
        # If meeting more than once per week, require meeting_days
        if meeting_frequency and meeting_frequency > 1 and not meeting_days:
            self.add_error('meeting_days', 'Please specify meeting days since you meet more than once per week.')
        
        return cleaned_data

# from django import forms
# from .models import CellGroup
# from apps.zones.models import Zone
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class CellGroupForm(forms.ModelForm):
#     class Meta:
#         model = CellGroup
#         fields = [
#             'name', 'description', 'zone', 'leader', 
#             'meeting_day', 'meeting_time', 'meeting_frequency', 'meeting_days',
#             'location', 'approval_status'
#         ]
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'meeting_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
#             'meeting_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Friday - Intercession, Sunday - Bible Study'}),
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'location': forms.TextInput(attrs={'class': 'form-control'}),
#             'meeting_day': forms.Select(attrs={'class': 'form-select'}),
#             'meeting_frequency': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
#             'approval_status': forms.Select(attrs={'class': 'form-select'}),
#             'leader': forms.Select(attrs={'class': 'form-select'}),
#             'zone': forms.Select(attrs={'class': 'form-select'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
        
#         # Only show active zones
#         self.fields['zone'].queryset = Zone.objects.filter(is_active=True)
#         self.fields['zone'].required = False
#         self.fields['zone'].empty_label = 'Select a zone...'
        
#         # Make leader optional
#         self.fields['leader'].required = False
#         self.fields['leader'].empty_label = 'Select a leader...'
        
#         # Restrict leader choices based on user role
#         if user and not user.is_admin():
#             # Non-admins can only see themselves as potential leaders
#             self.fields['leader'].queryset = User.objects.filter(id=user.id)
        
#         # Add help text
#         self.fields['zone'].help_text = 'Assign this cell group to a zone (optional but recommended)'
#         self.fields['meeting_frequency'].help_text = 'How many times per week the group meets'
        
#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if name:
#             # Check for duplicates, excluding current instance
#             existing = CellGroup.objects.filter(
#                 name__iexact=name,
#                 is_active=True
#             )
#             if self.instance and self.instance.pk:
#                 existing = existing.exclude(pk=self.instance.pk)
#             if existing.exists():
#                 raise forms.ValidationError('A cell group with this name already exists.')
#         return name
    
#     def clean(self):
#         cleaned_data = super().clean()
#         meeting_day = cleaned_data.get('meeting_day')
#         meeting_time = cleaned_data.get('meeting_time')
        
#         if meeting_day and not meeting_time:
#             self.add_error('meeting_time', 'Please specify a meeting time.')
        
#         return cleaned_data

