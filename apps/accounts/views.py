from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, CreateView, UpdateView, DetailView, ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone

from .models import CustomUser
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm,
    UserProfileForm, PasswordChangeForm
)
from .utils import log_activity, admin_required, AdminRequiredMixin
from apps.cell_groups.models import CellGroup


class RegisterView(CreateView):
    """User registration view."""
    
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Log the registration."""
        response = super().form_valid(form)
        
        # Set status to pending for leaders, approved for others
        if form.cleaned_data.get('role') == 'leader':
            self.object.status = 'pending'
            self.object.save()
            messages.success(
                self.request,
                'Account created successfully! Your application is pending approval. You will be notified once approved.'
            )
        else:
            self.object.status = 'approved'
            self.object.save()
            messages.success(
                self.request,
                'Account created successfully! Please log in.'
            )
        
        log_activity(
            user=self.object,
            action='create',
            entity_type='user',
            description=f'User registered with role: {self.object.get_role_display()}. Status: {self.object.get_status_display()}',
            entity_id=self.object.id,
            request=self.request
        )
        
        return response


class LoginView(View):
    """User login view with status checking."""
    
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    
    def get(self, request):
        """Display login form."""
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Handle login."""
        form = self.form_class(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if user can login based on status
                if user.is_pending():
                    messages.warning(
                        request, 
                        'Your account is pending approval. Please wait for admin approval.'
                    )
                    return render(request, self.template_name, {'form': form})
                
                if user.status == 'rejected':
                    messages.error(
                        request,
                        f'Your application was rejected. Reason: {user.rejection_reason or "Not specified"}'
                    )
                    return render(request, self.template_name, {'form': form})
                
                if not user.is_active_user:
                    messages.error(
                        request,
                        'Your account has been deactivated. Please contact administrator.'
                    )
                    return render(request, self.template_name, {'form': form})
                
                login(request, user)
                log_activity(
                    user=user,
                    action='login',
                    entity_type='user',
                    description=f'User logged in. Status: {user.get_status_display()}',
                    request=request
                )
                
                # Custom welcome message based on role and status
                if user.is_admin():
                    messages.success(request, f'Welcome back, Administrator {user.get_full_name()}!')
                elif user.is_cell_leader() and user.is_approved():
                    messages.success(request, f'Welcome back, Cell Leader {user.get_full_name()}!')
                else:
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                
                return redirect('dashboard:dashboard')
        
        return render(request, self.template_name, {'form': form})


@login_required(login_url='accounts:login')
def logout_view(request):
    """Handle logout."""
    user = request.user
    log_activity(
        user=user,
        action='logout',
        entity_type='user',
        description='User logged out',
        request=request
    )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required(login_url='accounts:login')
def profile_view(request):
    """Display user profile."""
    context = {'user': request.user}
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts:login')
def profile_edit_view(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(
                user=request.user,
                action='edit',
                entity_type='user',
                description='User updated profile',
                entity_id=request.user.id,
                request=request
            )
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'accounts/profile_edit.html', context)


@login_required(login_url='accounts:login')
def change_password_view(request):
    """Change user password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='user',
                    description='User changed password',
                    entity_id=request.user.id,
                    request=request
                )
                
                # Re-authenticate user
                user = authenticate(
                    username=request.user.username,
                    password=new_password
                )
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Password changed successfully!')
                    return redirect('accounts:profile')
            else:
                form.add_error('old_password', 'Old password is incorrect.')
    else:
        form = PasswordChangeForm()
    
    context = {'form': form}
    return render(request, 'accounts/change_password.html', context)


@admin_required
def user_management_view(request):
    """Manage all users (Admin only)."""
    users = CustomUser.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        log_activity(
            user=request.user,
            action='search',
            entity_type='user',
            description=f'Searched users with query: {search_query}',
            request=request
        )
    
    # Filtering by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Filtering by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        users = users.filter(status=status_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'role_choices': CustomUser.ROLE_CHOICES,
        'status_choices': CustomUser.STATUS_CHOICES,
    }
    
    return render(request, 'accounts/user_management.html', context)


class UserDetailView(AdminRequiredMixin, DetailView):
    """View user details (Admin only)."""
    
    model = CustomUser
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'


class UserEditView(AdminRequiredMixin, UpdateView):
    """Edit user (Admin only)."""
    
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/user_edit.html'
    success_url = reverse_lazy('accounts:user_management')
    
    def form_valid(self, form):
        """Log the update."""
        response = super().form_valid(form)
        log_activity(
            user=self.request.user,
            action='edit',
            entity_type='user',
            description=f'Edited user: {self.object.get_full_name()}',
            entity_id=self.object.id,
            request=self.request
        )
        messages.success(self.request, 'User updated successfully!')
        return response


@admin_required
def pending_approvals_view(request):
    """View pending user approvals (Admin only)."""
    pending_users = CustomUser.objects.filter(
        role='leader', 
        status='pending'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        pending_users = pending_users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    paginator = Paginator(pending_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_users': page_obj,
        'search_query': search_query,
        'cell_groups': CellGroup.objects.filter(is_active=True),
    }
    
    return render(request, 'accounts/pending_approvals.html', context)


@admin_required
def approve_user_view(request, pk):
    """Approve a user application (Admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        assigned_cell_group_id = request.POST.get('assigned_cell_group')
        
        if assigned_cell_group_id:
            try:
                cell_group = CellGroup.objects.get(id=assigned_cell_group_id)
                user.assigned_cell_group = cell_group
                user.status = 'approved'
                user.approved_at = timezone.now()
                user.approved_by = request.user
                user.save()
                
                log_activity(
                    user=request.user,
                    action='approve',
                    entity_type='user',
                    description=f'Approved user: {user.get_full_name()} and assigned to cell group {cell_group.name}',
                    entity_id=user.id,
                    request=request
                )
                
                messages.success(
                    request, 
                    f'User {user.get_full_name()} has been approved and assigned to {cell_group.name}.'
                )
            except CellGroup.DoesNotExist:
                messages.error(request, 'Selected cell group does not exist.')
        else:
            messages.error(request, 'Please select a cell group for this leader.')
        
        return redirect('accounts:pending_approvals')
    
    context = {
        'user': user,
        'cell_groups': CellGroup.objects.filter(is_active=True),
    }
    return render(request, 'accounts/approve_user.html', context)


@admin_required
def reject_user_view(request, pk):
    """Reject a user application (Admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        user.status = 'rejected'
        user.rejection_reason = rejection_reason
        user.save()
        
        log_activity(
            user=request.user,
            action='reject',
            entity_type='user',
            description=f'Rejected user: {user.get_full_name()}. Reason: {rejection_reason}',
            entity_id=user.id,
            request=request
        )
        
        messages.success(request, f'User {user.get_full_name()} has been rejected.')
        return redirect('accounts:pending_approvals')
    
    context = {'user': user}
    return render(request, 'accounts/reject_user.html', context)


@admin_required
def user_deactivate_view(request, pk):
    """Deactivate user (Admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user.is_active_user = False
        user.save()
        
        log_activity(
            user=request.user,
            action='deactivate',
            entity_type='user',
            description=f'Deactivated user: {user.get_full_name()}',
            entity_id=user.id,
            request=request
        )
        
        messages.success(request, f'User {user.get_full_name()} has been deactivated.')
        return redirect('accounts:user_management')
    
    context = {'user': user}
    return render(request, 'accounts/user_deactivate.html', context)


@admin_required
def user_activate_view(request, pk):
    """Activate user (Admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user.is_active_user = True
        user.save()
        
        log_activity(
            user=request.user,
            action='activate',
            entity_type='user',
            description=f'Activated user: {user.get_full_name()}',
            entity_id=user.id,
            request=request
        )
        
        messages.success(request, f'User {user.get_full_name()} has been activated.')
        return redirect('accounts:user_management')
    
    context = {'user': user}
    return render(request, 'accounts/user_activate.html', context)

@admin_required
def admin_create_user_view(request):
    """Admin creates a new user (including leaders)."""
    from .forms import AdminUserCreationForm
    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Set status based on role
            if user.role == 'leader':
                user.status = 'approved'  # Admin-created leaders are auto-approved
                user.save()
            
            log_activity(
                user=request.user,
                action='create',
                entity_type='user',
                description=f'Admin created user: {user.get_full_name()} with role: {user.get_role_display()}',
                entity_id=user.id,
                request=request
            )
            
            messages.success(request, f'User {user.get_full_name()} created successfully!')
            return redirect('accounts:user_management')
    else:
        form = AdminUserCreationForm()
    
    context = {'form': form}
    return render(request, 'accounts/admin_create_user.html', context)