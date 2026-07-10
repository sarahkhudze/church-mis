from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta

from .models import Zone
from apps.cell_groups.models import CellGroup
from apps.members.models import Member
from apps.activity_logs.models import ActivityLog


def is_church_admin(user):
    return user.is_authenticated and user.is_admin()


@login_required
@user_passes_test(is_church_admin)
def zone_list(request):
    """List all zones."""
    zones = Zone.objects.filter(is_active=True).annotate(
        annotated_cell_group_count=Count('cell_groups', filter=Q(cell_groups__is_active=True)),
        annotated_member_count=Count('cell_groups__members', filter=Q(
            cell_groups__members__member_status=Member.ACTIVE,
            cell_groups__is_active=True
        ))
    ).order_by('name')
    
    context = {
        'zones': zones,
        'total_zones': zones.count(),
    }
    return render(request, 'zones/zone_list.html', context)


@login_required
@user_passes_test(is_church_admin)
def zone_create(request):
    """Create a new zone."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        zone_leader_id = request.POST.get('zone_leader')
        
        if Zone.objects.filter(name=name).exists():
            messages.error(request, 'A zone with this name already exists.')
            return redirect('zones:zone_create')
        
        zone = Zone.objects.create(
            name=name,
            description=description,
            zone_leader_id=zone_leader_id if zone_leader_id else None
        )
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='create',
            description=f'Created zone: {zone.name}'
        )
        
        messages.success(request, f'Zone "{zone.name}" created successfully!')
        return redirect('zones:zone_list')
    
    # Get potential zone leaders (admins and zone leaders without a zone)
    from apps.accounts.models import CustomUser
    zone_leaders = CustomUser.objects.filter(
        Q(role='admin') | Q(role='zone_leader'),
        is_active_user=True
    ).exclude(
        led_zones__is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'zone_leaders': zone_leaders,
    }
    return render(request, 'zones/zone_form.html', context)


@login_required
@user_passes_test(is_church_admin)
def zone_edit(request, pk):
    """Edit an existing zone."""
    zone = get_object_or_404(Zone, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        zone_leader_id = request.POST.get('zone_leader')
        is_active = request.POST.get('is_active') == 'on'
        
        # Check name uniqueness
        if Zone.objects.filter(name=name).exclude(pk=pk).exists():
            messages.error(request, 'A zone with this name already exists.')
            return redirect('zones:zone_edit', pk=pk)
        
        zone.name = name
        zone.description = description
        zone.zone_leader_id = zone_leader_id if zone_leader_id else None
        zone.is_active = is_active
        zone.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='update',
            description=f'Updated zone: {zone.name}'
        )
        
        messages.success(request, f'Zone "{zone.name}" updated successfully!')
        return redirect('zones:zone_list')
    
    # Get potential zone leaders
    from apps.accounts.models import CustomUser
    zone_leaders = CustomUser.objects.filter(
        Q(role='admin') | Q(role='zone_leader'),
        is_active_user=True
    ).exclude(
        Q(led_zones__is_active=True) & ~Q(led_zones=pk)
    ).order_by('first_name', 'last_name')
    
    context = {
        'zone': zone,
        'zone_leaders': zone_leaders,
    }
    return render(request, 'zones/zone_form.html', context)


@login_required
@user_passes_test(is_church_admin)
def zone_detail(request, pk):
    """View zone details."""
    zone = get_object_or_404(Zone, pk=pk)
    
    # Get cell groups in this zone
    cell_groups = zone.cell_groups.filter(is_active=True).annotate(
        member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
    ).order_by('name')
    
    # Get member statistics
    members = Member.objects.filter(
        cell_group__zone=zone,
        cell_group__is_active=True
    )
    
    # Recent members
    recent_members = members.filter(
        member_status=Member.ACTIVE
    ).order_by('-created_at')[:10]
    
    # Member status breakdown
    member_status_breakdown = {
        'active': members.filter(member_status=Member.ACTIVE).count(),
        'left': members.filter(member_status=Member.LEFT).count(),
        'deceased': members.filter(member_status=Member.DECEASED).count(),
        #'inactive': members.filter(member_status=Member.INACTIVE).count(),
    }
    
    context = {
        'zone': zone,
        'cell_groups': cell_groups,
        'total_members': members.count(),
        'recent_members': recent_members,
        'member_status_breakdown': member_status_breakdown,
        'attendance_summary': zone.attendance_summary,
    }
    return render(request, 'zones/zone_detail.html', context)


@login_required
@user_passes_test(is_church_admin)
def zone_delete(request, pk):
    """Delete (soft delete) a zone."""
    zone = get_object_or_404(Zone, pk=pk)
    
    if request.method == 'POST':
        # Check if zone has active cell groups
        if zone.cell_groups.filter(is_active=True).exists():
            messages.error(
                request, 
                f'Cannot delete zone "{zone.name}" because it has active cell groups. '
                'Please reassign or deactivate them first.'
            )
            return redirect('zones:zone_list')
        
        # Check if any user is assigned as zone leader
        if zone.zone_leader:
            zone.zone_leader = None
            zone.save()
        
        zone.is_active = False
        zone.save()
        
        # Log activity
        ActivityLog.objects.create(
            user=request.user,
            action='delete',
            description=f'Deleted zone: {zone.name}'
        )
        
        messages.success(request, f'Zone "{zone.name}" deleted successfully!')
        return redirect('zones:zone_list')
    
    context = {'zone': zone}
    return render(request, 'zones/zone_confirm_delete.html', context)


@login_required
def zone_overview_api(request):
    """API endpoint for zone overview statistics."""
    user = request.user
    
    if user.is_admin():
        zones = Zone.objects.filter(is_active=True)
        total_zones = zones.count()
        total_cell_groups = CellGroup.objects.filter(
            zone__is_active=True,
            is_active=True
        ).count()
        total_members = Member.objects.filter(
            cell_group__zone__is_active=True,
            cell_group__is_active=True,
            member_status=Member.ACTIVE
        ).count()
        
        zone_stats = []
        for zone in zones:
            zone_stats.append({
                'id': zone.id,
                'name': zone.name,
                'cell_group_count': zone.cell_groups.filter(is_active=True).count(),  # Using property
                'member_count': Member.objects.filter(
                    cell_group__zone=zone,
                    cell_group__is_active=True,
                    member_status=Member.ACTIVE
                ).count(),
            })
        
        return JsonResponse({
            'total_zones': total_zones,
            'total_cell_groups': total_cell_groups,
            'total_members': total_members,
            'zones': zone_stats,
        })
    
    return JsonResponse({'error': 'Unauthorized'}, status=403)