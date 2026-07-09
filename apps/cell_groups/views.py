from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from .models import CellGroup
from .forms import CellGroupForm
from apps.members.models import Member
from apps.zones.models import Zone
from apps.activity_logs.models import ActivityLog


def is_church_admin(user):
    return user.is_authenticated and user.is_admin()


def is_zone_leader_or_admin(user):
    return user.is_authenticated and (user.is_admin() or user.is_zone_leader())


@login_required
def cell_group_list_view(request):
    """List all cell groups with filtering."""
    user = request.user
    cell_groups = CellGroup.objects.filter(is_active=True)
    
    # Filter based on user role
    if user.is_cell_leader() and user.assigned_cell_group:
        # Cell leaders can only see their own group
        cell_groups = cell_groups.filter(id=user.assigned_cell_group.id)
    elif user.is_zone_leader() and user.zone_name:
        # Zone leaders can see groups in their zone
        try:
            zone = Zone.objects.get(name=user.zone_name, is_active=True)
            cell_groups = cell_groups.filter(zone=zone)
        except Zone.DoesNotExist:
            cell_groups = cell_groups.none()
    # Admins can see all groups
    
    # Apply filters
    zone_filter = request.GET.get('zone')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if zone_filter:
        cell_groups = cell_groups.filter(zone__id=zone_filter)
    
    if status_filter:
        cell_groups = cell_groups.filter(approval_status=status_filter)
    
    if search_query:
        cell_groups = cell_groups.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(leader__first_name__icontains=search_query) |
            Q(leader__last_name__icontains=search_query)
        )
    
    # Annotate with member count
    cell_groups = cell_groups.annotate(
        member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
    ).order_by('name')
    
    # Pagination
    paginator = Paginator(cell_groups, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get zones for filter dropdown
    zones = Zone.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'zones': zones,
        'zone_filter': zone_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'is_admin': user.is_admin(),
        'is_zone_leader': user.is_zone_leader(),
        'is_cell_leader': user.is_cell_leader(),
        'total_cell_groups': cell_groups.count(),
    }
    return render(request, 'cell_groups/cell_group_list.html', context)


@login_required
def cell_group_detail_view(request, pk):
    """View cell group details."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    # Check permissions
    if user.is_cell_leader() and user.assigned_cell_group:
        if user.assigned_cell_group.id != cell_group.id:
            messages.error(request, 'You can only view your own cell group.')
            return redirect('cell_groups:cell_group_list')
    elif user.is_zone_leader() and user.zone_name:
        if cell_group.zone and cell_group.zone.name != user.zone_name:
            messages.error(request, 'You can only view cell groups in your zone.')
            return redirect('cell_groups:cell_group_list')
    elif not (user.is_admin() or user.is_superuser):
        if not user.is_zone_leader() and not user.is_cell_leader():
            messages.error(request, 'You do not have permission to view this cell group.')
            return redirect('cell_groups:cell_group_list')
    
    # Get members
    members = cell_group.members.filter(
        member_status=Member.ACTIVE
    ).order_by('-created_at')
    
    # Member statistics
    member_stats = {
        'total': members.count(),
        'male': members.filter(gender='M').count(),
        'female': members.filter(gender='F').count(),
        'baptized': members.filter(is_baptized=True).count(),
        'married': members.filter(is_married=True).count(),
        'follow_up': members.filter(follow_up_required=True).count(),
    }
    
    # Recent activity
    recent_activities = ActivityLog.objects.filter(
        Q(description__icontains=cell_group.name) |
        Q(description__icontains=f'cell group "{cell_group.name}"')
    ).order_by('-timestamp')[:10]
    
    # Get attendance records
    from apps.members.models import AttendanceRecord
    attendance_records = AttendanceRecord.objects.filter(
        cell_group=cell_group
    ).order_by('-meeting_date')[:10]
    
    context = {
        'cell_group': cell_group,
        'members': members[:20],
        'member_stats': member_stats,
        'recent_activities': recent_activities,
        'attendance_records': attendance_records,
        'total_members': members.count(),
        'is_admin': user.is_admin(),
        'is_zone_leader': user.is_zone_leader(),
        'is_cell_leader': user.is_cell_leader(),
    }
    return render(request, 'cell_groups/cell_group_detail.html', context)


@login_required
def cell_group_create_view(request):
    """Create a new cell group."""
    user = request.user
    
    # Check permissions - only admins and zone leaders can create
    if not (user.is_admin() or user.is_zone_leader()):
        messages.error(request, 'You do not have permission to create cell groups.')
        return redirect('cell_groups:cell_group_list')
    
    if request.method == 'POST':
        form = CellGroupForm(request.POST, user=user)
        if form.is_valid():
            cell_group = form.save(commit=False)
            
            # If zone leader, auto-assign to their zone
            if user.is_zone_leader() and user.zone_name:
                try:
                    zone = Zone.objects.get(name=user.zone_name, is_active=True)
                    cell_group.zone = zone
                except Zone.DoesNotExist:
                    messages.warning(request, 'Your zone could not be found. Please contact an administrator.')
            
            # If admin, use selected zone
            if user.is_admin() and form.cleaned_data.get('zone'):
                cell_group.zone = form.cleaned_data.get('zone')
            
            cell_group.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                action='create',
                description=f'Created cell group: {cell_group.name}'
            )
            
            messages.success(request, f'Cell group "{cell_group.name}" created successfully!')
            return redirect('cell_groups:cell_group_detail', pk=cell_group.id)
    else:
        form = CellGroupForm(user=user)
        # Pre-select zone if zone leader
        if user.is_zone_leader() and user.zone_name:
            try:
                zone = Zone.objects.get(name=user.zone_name, is_active=True)
                form.fields['zone'].initial = zone.id
            except Zone.DoesNotExist:
                pass
    
    # Get available zones for dropdown
    zones = Zone.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'zones': zones,
        'is_edit': False,
        'is_admin': user.is_admin(),
        'is_zone_leader': user.is_zone_leader(),
    }
    return render(request, 'cell_groups/cell_group_form.html', context)


@login_required
def cell_group_edit_view(request, pk):
    """Edit an existing cell group."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    # Check permissions
    if user.is_cell_leader() and user.assigned_cell_group:
        if user.assigned_cell_group.id != cell_group.id:
            messages.error(request, 'You can only edit your own cell group.')
            return redirect('cell_groups:cell_group_list')
    elif user.is_zone_leader() and user.zone_name:
        if cell_group.zone and cell_group.zone.name != user.zone_name:
            messages.error(request, 'You can only edit cell groups in your zone.')
            return redirect('cell_groups:cell_group_list')
    elif not user.is_admin() and not user.is_superuser:
        messages.error(request, 'You do not have permission to edit this cell group.')
        return redirect('cell_groups:cell_group_list')
    
    if request.method == 'POST':
        form = CellGroupForm(request.POST, instance=cell_group, user=user)
        if form.is_valid():
            cell_group = form.save()
            
            # Log activity
            ActivityLog.objects.create(
                user=user,
                action='update',
                description=f'Updated cell group: {cell_group.name}'
            )
            
            messages.success(request, f'Cell group "{cell_group.name}" updated successfully!')
            return redirect('cell_groups:cell_group_detail', pk=cell_group.id)
    else:
        form = CellGroupForm(instance=cell_group, user=user)
    
    # Get available zones for dropdown
    zones = Zone.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'cell_group': cell_group,
        'zones': zones,
        'is_edit': True,
        'is_admin': user.is_admin(),
        'is_zone_leader': user.is_zone_leader(),
        'is_cell_leader': user.is_cell_leader(),
    }
    return render(request, 'cell_groups/cell_group_form.html', context)


@login_required
def cell_group_delete_view(request, pk):
    """Delete (soft delete) a cell group."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    # Only admins can delete
    if not user.is_admin():
        messages.error(request, 'You do not have permission to delete cell groups.')
        return redirect('cell_groups:cell_group_list')
    
    # Check if cell group has members
    if cell_group.members.filter(member_status=Member.ACTIVE).exists():
        messages.error(
            request,
            f'Cannot delete cell group "{cell_group.name}" because it has active members. '
            'Please reassign members first.'
        )
        return redirect('cell_groups:cell_group_detail', pk=cell_group.id)
    
    if request.method == 'POST':
        # Soft delete
        cell_group.is_active = False
        cell_group.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action='delete',
            description=f'Deleted cell group: {cell_group.name}'
        )
        
        messages.success(request, f'Cell group "{cell_group.name}" deleted successfully!')
        return redirect('cell_groups:cell_group_list')
    
    context = {
        'cell_group': cell_group,
        'is_admin': user.is_admin(),
    }
    return render(request, 'cell_groups/cell_group_confirm_delete.html', context)


@login_required
def cell_group_members_view(request, pk):
    """View and manage members of a cell group."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    # Check permissions
    if user.is_cell_leader() and user.assigned_cell_group:
        if user.assigned_cell_group.id != cell_group.id:
            messages.error(request, 'You can only view members of your own cell group.')
            return redirect('cell_groups:cell_group_list')
    elif user.is_zone_leader() and user.zone_name:
        if cell_group.zone and cell_group.zone.name != user.zone_name:
            messages.error(request, 'You can only view members of cell groups in your zone.')
            return redirect('cell_groups:cell_group_list')
    elif not user.is_admin() and not user.is_superuser:
        messages.error(request, 'You do not have permission to view members.')
        return redirect('cell_groups:cell_group_list')
    
    # Get members with filters
    members = cell_group.members.all()
    
    status_filter = request.GET.get('status')
    if status_filter:
        members = members.filter(member_status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    members = members.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cell_group': cell_group,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_members': members.count(),
        'is_admin': user.is_admin(),
        'is_zone_leader': user.is_zone_leader(),
        'is_cell_leader': user.is_cell_leader(),
    }
    return render(request, 'cell_groups/cell_group_members.html', context)


@login_required
def cell_group_approve_view(request, pk):
    """Approve a cell group (admin only)."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    if not user.is_admin():
        messages.error(request, 'Only administrators can approve cell groups.')
        return redirect('cell_groups:cell_group_list')
    
    if request.method == 'POST':
        cell_group.approval_status = 'approved'
        cell_group.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action='approve',
            description=f'Approved cell group: {cell_group.name}'
        )
        
        messages.success(request, f'Cell group "{cell_group.name}" approved successfully!')
    
    return redirect('cell_groups:cell_group_detail', pk=cell_group.id)


@login_required
def cell_group_reject_view(request, pk):
    """Reject a cell group (admin only)."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    if not user.is_admin():
        messages.error(request, 'Only administrators can reject cell groups.')
        return redirect('cell_groups:cell_group_list')
    
    if request.method == 'POST':
        cell_group.approval_status = 'rejected'
        cell_group.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=user,
            action='reject',
            description=f'Rejected cell group: {cell_group.name}'
        )
        
        messages.success(request, f'Cell group "{cell_group.name}" rejected.')
    
    return redirect('cell_groups:cell_group_detail', pk=cell_group.id)


@login_required
def cell_group_stats_api(request, pk):
    """API endpoint for cell group statistics."""
    cell_group = get_object_or_404(CellGroup, pk=pk)
    user = request.user
    
    # Check permissions
    if user.is_cell_leader() and user.assigned_cell_group:
        if user.assigned_cell_group.id != cell_group.id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    elif user.is_zone_leader() and user.zone_name:
        if cell_group.zone and cell_group.zone.name != user.zone_name:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
    elif not user.is_admin() and not user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    members = cell_group.members.filter(member_status=Member.ACTIVE)
    
    stats = {
        'id': cell_group.id,
        'name': cell_group.name,
        'total_members': members.count(),
        'male': members.filter(gender='M').count(),
        'female': members.filter(gender='F').count(),
        'baptized': members.filter(is_baptized=True).count(),
        'married': members.filter(is_married=True).count(),
        'follow_up_required': members.filter(follow_up_required=True).count(),
        'zone': cell_group.zone.name if cell_group.zone else None,
        'zone_id': cell_group.zone.id if cell_group.zone else None,
        'leader': cell_group.leader.get_full_name() if cell_group.leader else None,
        'leader_id': cell_group.leader.id if cell_group.leader else None,
        'meeting_schedule': cell_group.meeting_schedule,
        'meeting_day': cell_group.meeting_day,
        'meeting_time': str(cell_group.meeting_time) if cell_group.meeting_time else None,
        'location': cell_group.location,
        'approval_status': cell_group.approval_status,
        'is_active': cell_group.is_active,
        'created_at': cell_group.created_at.isoformat() if cell_group.created_at else None,
        'updated_at': cell_group.updated_at.isoformat() if cell_group.updated_at else None,
    }
    
    return JsonResponse(stats)


@login_required
def get_cell_groups_by_zone_api(request):
    """API endpoint to get cell groups by zone."""
    zone_id = request.GET.get('zone_id')
    
    if not zone_id:
        return JsonResponse({'error': 'Zone ID required'}, status=400)
    
    try:
        zone = Zone.objects.get(id=zone_id, is_active=True)
        cell_groups = zone.cell_groups.filter(is_active=True).values('id', 'name')
        return JsonResponse({'cell_groups': list(cell_groups)})
    except Zone.DoesNotExist:
        return JsonResponse({'error': 'Zone not found'}, status=404)


@login_required
def cell_group_leader_dashboard(request):
    """Dashboard view for cell group leaders."""
    user = request.user
    
    if not user.is_cell_leader() or not user.assigned_cell_group:
        messages.error(request, 'You are not assigned to any cell group.')
        return redirect('dashboard:dashboard')
    
    cell_group = user.assigned_cell_group
    members = cell_group.members.filter(member_status=Member.ACTIVE)
    
    context = {
        'cell_group': cell_group,
        'total_members': members.count(),
        'male_count': members.filter(gender='M').count(),
        'female_count': members.filter(gender='F').count(),
        'baptized_count': members.filter(is_baptized=True).count(),
        'follow_up_required': members.filter(follow_up_required=True).count(),
        'recent_members': members.order_by('-created_at')[:10],
        'zone': cell_group.zone,
    }
    return render(request, 'cell_groups/leader_dashboard.html', context)