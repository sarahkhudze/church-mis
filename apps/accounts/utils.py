from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from apps.activity_logs.models import ActivityLog


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, action, entity_type, description, 
                 entity_id=None, request=None):
    """Create an activity log entry."""
    ip_address = get_client_ip(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT')[:500] if request else None
    
    ActivityLog.log_action(
        user=user,
        action=action,
        entity_type=entity_type,
        description=description,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def admin_required(view_func):
    """Decorator to ensure user is an admin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def cell_leader_required(view_func):
    """Decorator to ensure user is a cell leader."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not request.user.is_cell_leader():
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def leader_or_admin_required(view_func):
    """Decorator to ensure user is a cell leader or admin."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not (request.user.is_admin() or request.user.is_cell_leader()):
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


class AdminRequiredMixin:
    """Mixin to ensure user is an admin."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not request.user.is_admin():
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class CellLeaderRequiredMixin:
    """Mixin to ensure user is a cell leader."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not request.user.is_cell_leader():
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class LeaderOrAdminRequiredMixin:
    """Mixin to ensure user is a cell leader or admin."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        if not (request.user.is_admin() or request.user.is_cell_leader()):
            messages.error(request, 'You do not have permission to access this page.')
            log_activity(
                user=request.user,
                action='access_denied',
                entity_type='system',
                description='Unauthorized access attempt',
                request=request
            )
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


def can_manage_member(user, member):
    """Check if user can manage a specific member."""
    if user.is_admin():
        return True
    
    if user.is_cell_leader():
        return member.cell_group == user.assigned_cell_group
    
    return False


def get_user_members(user):
    """Get queryset of members that user can access."""
    from apps.members.models import Member
    
    if user.is_admin():
        return Member.objects.all()
    elif user.is_cell_leader() and user.assigned_cell_group:
        return user.assigned_cell_group.members.all()
    
    return Member.objects.none()


def get_user_cell_groups(user):
    """Get queryset of cell groups that user can access."""
    from apps.members.models import CellGroup
    
    if user.is_admin():
        return CellGroup.objects.all()
    elif user.is_cell_leader() and user.assigned_cell_group:
        return CellGroup.objects.filter(id=user.assigned_cell_group.id)
    
    return CellGroup.objects.none()
