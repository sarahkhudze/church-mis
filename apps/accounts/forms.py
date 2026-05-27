from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser
from apps.cell_groups.models import CellGroup


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    
    # Remove admin from the role choices that regular users can select
    USER_ROLE_CHOICES = [
        ('leader', 'Cell Group Leader'),
        ('viewer', 'Viewer (Read-only)'),
    ]
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Required. Enter a valid email address.'
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Required.'
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Required.'
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Optional. Enter your phone number.'
    )
    role = forms.ChoiceField(
        choices=USER_ROLE_CHOICES,  # Use limited choices for public registration
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Select your role in the system.'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 
                  'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add specific placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
        
        # Add help text
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
    
    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_username(self):
        """Check if username already exists."""
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    # REMOVED the clean method that was checking for application_reason
    # No additional validation needed


class CustomUserChangeForm(UserChangeForm):
    """Form for updating user information."""
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Optional. Enter your phone number.'
    )
    assigned_cell_group = forms.ModelChoiceField(
        queryset=CellGroup.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Cell group assigned to this leader.'
    )
    status = forms.ChoiceField(
        choices=CustomUser.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Account approval status'
    )
    rejection_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text='Reason for rejection if applicable'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number',
                  'role', 'status', 'assigned_cell_group', 'rejection_reason', 'is_active_user')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            if field != 'password':
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with status checking."""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def confirm_login_allowed(self, user):
        """Check if user is allowed to login based on status."""
        if not user.is_active_user:
            raise forms.ValidationError(
                'This account is inactive.',
                code='inactive',
            )
        if user.is_pending():
            raise forms.ValidationError(
                'Your account is pending approval. Please wait for admin approval.',
                code='pending',
            )
        if user.status == 'rejected':
            raise forms.ValidationError(
                f'Your application was rejected. Reason: {user.rejection_reason or "Not specified"}',
                code='rejected',
            )
        super().confirm_login_allowed(user)


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PasswordChangeForm(forms.Form):
    """Form for changing password."""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text='At least 8 characters.'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False
    )
    
    def clean_new_password1(self):
        """Validate new password."""
        password = self.cleaned_data.get('new_password1')
        try:
            validate_password(password)
        except forms.ValidationError as e:
            raise forms.ValidationError(e.message)
        return password
    
    def clean(self):
        """Check if passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data