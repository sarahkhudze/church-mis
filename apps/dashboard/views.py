# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q, Count
# from datetime import date, timedelta
# from django.utils import timezone

# from apps.members.models import Member
# from apps.cell_groups.models import CellGroup
# from apps.accounts.models import CustomUser
# from apps.activity_logs.models import ActivityLog
# from apps.zones.models import Zone


# @login_required(login_url='login')
# def dashboard_view(request):
#     """Main dashboard view."""
#     user = request.user
#     context = {}
    
#     if user.is_admin():
#         # Admin Dashboard
#         context['is_admin'] = True
        
#         # Overall Statistics
#         context['total_members'] = Member.objects.active().count()
#         context['total_cell_groups'] = CellGroup.objects.filter(is_active=True).count()
#         context['total_leaders'] = CustomUser.objects.filter(role='leader', is_active_user=True).count()
        
#         # Member Statistics
#         baptized_members = Member.objects.active().filter(is_baptized=True).count()
#         married_members = Member.objects.active().filter(is_married=True).count()
#         context['baptized_members'] = baptized_members
#         context['married_members'] = married_members
        
#         # Gender Distribution
#         male_count = Member.objects.active().filter(gender='M').count()
#         female_count = Member.objects.active().filter(gender='F').count()
#         context['male_count'] = male_count
#         context['female_count'] = female_count
        
#         # Recent Members (last 7 days)
#         seven_days_ago = timezone.now() - timedelta(days=7)
#         recent_members = Member.objects.active().filter(
#             created_at__gte=seven_days_ago
#         ).order_by('-created_at')[:5]
#         context['recent_members'] = recent_members
        
#         # Birthdays This Month
#         today = date.today()
#         birthdays_this_month = Member.objects.active().filter(
#             date_of_birth__month=today.month
#         ).order_by('date_of_birth')[:10]
#         context['birthdays_this_month'] = birthdays_this_month
        
#         # Cell Groups with Member Count
#         cell_groups_stats = CellGroup.objects.filter(
#             is_active=True
#         ).annotate(
#             member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#         ).order_by('-member_count')[:5]
#         context['cell_groups_stats'] = cell_groups_stats
        
#         # Recent Activity
#         recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
#         context['recent_activities'] = recent_activities
        
#         # ===== ZONE MANAGEMENT DATA =====
#         # Get all active zones with counts using the relationship
#         zones = Zone.objects.filter(is_active=True).annotate(
#             annotated_cell_group_count=Count('cell_groups', filter=Q(cell_groups__is_active=True)),
#             annotated_member_count=Count('cell_groups__members', filter=Q(
#                 cell_groups__members__member_status=Member.ACTIVE,
#                 cell_groups__is_active=True
#             ))
#         ).order_by('name')
        
#         context['total_zones'] = zones.count()
#         context['zones_without_leaders'] = zones.filter(zone_leader__isnull=True).count()
#         context['zones'] = zones[:5]  # Show first 5 zones on dashboard
        
#         # Total cell groups in zones
#         context['total_cell_groups_in_zones'] = CellGroup.objects.filter(
#             zone__is_active=True,
#             is_active=True
#         ).count()
        
#         # Total members in zones
#         context['total_members_in_zones'] = Member.objects.filter(
#             cell_group__zone__is_active=True,
#             cell_group__is_active=True,
#             member_status=Member.ACTIVE
#         ).count()
#         # ===== END ZONE MANAGEMENT DATA =====
        
#     elif user.is_zone_leader() and user.zone_name:
#         context['is_zone_leader'] = True
        
#         # Get the zone using the new Zone model
#         try:
#             zone = Zone.objects.get(name=user.zone_name, is_active=True)
#             zone_cell_groups = CellGroup.objects.filter(is_active=True, zone=zone).annotate(
#                 member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#             ).order_by('name')
#             zone_members = Member.objects.filter(cell_group__in=zone_cell_groups).active()
            
#             context['zone_name'] = zone.name
#             context['zone_cell_groups'] = zone_cell_groups
#             context['zone_cell_group_count'] = zone_cell_groups.count()
#             context['zone_member_count'] = zone_members.count()
#             context['zone_active_members'] = zone_members.filter(member_status=Member.ACTIVE).count()
#             context['zone_inactive_members'] = zone_members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count()
#             context['zone_follow_up_required'] = zone_members.filter(follow_up_required=True).count()
#             context['zone_attendance_summary'] = {
#                 'active_members': zone_members.count(),
#                 'follow_up_required': context['zone_follow_up_required'],
#             }
#         except Zone.DoesNotExist:
#             # Fallback to old zone_name if Zone model doesn't have it
#             zone_cell_groups = CellGroup.objects.filter(is_active=True, zone_name=user.zone_name).annotate(
#                 member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#             ).order_by('name')
#             zone_members = Member.objects.filter(cell_group__in=zone_cell_groups).active()
            
#             context['zone_name'] = user.zone_name
#             context['zone_cell_groups'] = zone_cell_groups
#             context['zone_cell_group_count'] = zone_cell_groups.count()
#             context['zone_member_count'] = zone_members.count()
#             context['zone_active_members'] = zone_members.filter(member_status=Member.ACTIVE).count()
#             context['zone_inactive_members'] = zone_members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count()
#             context['zone_follow_up_required'] = zone_members.filter(follow_up_required=True).count()
#             context['zone_attendance_summary'] = {
#                 'active_members': zone_members.count(),
#                 'follow_up_required': context['zone_follow_up_required'],
#             }

#     elif user.is_cell_leader():
#         # Cell Leader Dashboard
#         context['is_cell_leader'] = True
#         cell_group = user.assigned_cell_group
        
#         if cell_group:
#             # Cell Group Statistics
#             members = cell_group.members.active()
#             context['cell_group'] = cell_group
#             context['total_members'] = members.count()
            
#             # Member Statistics
#             context['baptized_members'] = members.filter(is_baptized=True).count()
#             context['married_members'] = members.filter(is_married=True).count()
            
#             # Gender Distribution
#             context['male_count'] = members.filter(gender='M').count()
#             context['female_count'] = members.filter(gender='F').count()
            
#             # Recently Added Members
#             recent_members = members.order_by('-created_at')[:5]
#             context['recent_members'] = recent_members
            
#             # Birthdays This Month
#             today = date.today()
#             birthdays = members.filter(date_of_birth__month=today.month).order_by('date_of_birth')[:10]
#             context['birthdays_this_month'] = birthdays

#             # Follow-up alerts for the assigned cell group
#             context['follow_up_required'] = members.filter(follow_up_required=True).count()
#             context['cell_group_schedule'] = cell_group.meeting_schedule
    
#     return render(request, 'dashboard/dashboard.html', context)


# @login_required(login_url='login')
# def statistics_view(request):
#     """Detailed statistics view."""
#     user = request.user
#     context = {}
    
#     if user.is_admin():
#         # Overall statistics
#         all_members = Member.objects.active()
        
#         # Age Groups
#         today = date.today()
#         age_groups = {
#             'children': 0,  # 0-12
#             'youth': 0,      # 13-18
#             'young_adults': 0,  # 19-35
#             'adults': 0,     # 36-60
#             'seniors': 0,    # 60+
#         }
        
#         for member in all_members:
#             age = today.year - member.date_of_birth.year
#             if age <= 12:
#                 age_groups['children'] += 1
#             elif age <= 18:
#                 age_groups['youth'] += 1
#             elif age <= 35:
#                 age_groups['young_adults'] += 1
#             elif age <= 60:
#                 age_groups['adults'] += 1
#             else:
#                 age_groups['seniors'] += 1
        
#         context['age_groups'] = age_groups
        
#         # Monthly Membership Growth (last 12 months)
#         growth_data = {}
#         for i in range(12):
#             month_date = today - timedelta(days=30*i)
#             month_members = Member.objects.filter(
#                 created_at__year=month_date.year,
#                 created_at__month=month_date.month
#             ).count()
#             growth_data[month_date.strftime('%B')] = month_members
        
#         context['growth_data'] = dict(reversed(list(growth_data.items())))
        
#         # Cell Group Rankings
#         cell_groups = CellGroup.objects.filter(is_active=True).annotate(
#             member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#         ).order_by('-member_count')
#         context['cell_groups'] = cell_groups
        
#         # Zone Statistics
#         zones = Zone.objects.filter(is_active=True).annotate(
#             annotated_cell_group_count=Count('cell_groups', filter=Q(cell_groups__is_active=True)),
#             annotated_member_count=Count('cell_groups__members', filter=Q(
#                 cell_groups__members__member_status=Member.ACTIVE,
#                 cell_groups__is_active=True
#             ))
#         ).order_by('name')
#         context['zone_statistics'] = zones
#         context['total_zones'] = zones.count()
#         context['zones_without_leaders'] = zones.filter(zone_leader__isnull=True).count()
        
#         # Statistics Summary
#         total = all_members.count()
#         context['stats_summary'] = {
#             'total_members': total,
#             'baptized_percentage': (all_members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
#             'married_percentage': (all_members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
#             'male_percentage': (all_members.filter(gender='M').count() / total * 100) if total > 0 else 0,
#         }
    
#     elif user.is_zone_leader() and user.zone_name:
#         # Zone Leader Statistics
#         try:
#             zone = Zone.objects.get(name=user.zone_name, is_active=True)
#             members = Member.objects.filter(
#                 cell_group__zone=zone,
#                 cell_group__is_active=True,
#                 member_status=Member.ACTIVE
#             )
            
#             # Age Groups for Zone
#             today = date.today()
#             age_groups = {
#                 'children': 0,
#                 'youth': 0,
#                 'young_adults': 0,
#                 'adults': 0,
#                 'seniors': 0,
#             }
            
#             for member in members:
#                 age = today.year - member.date_of_birth.year
#                 if age <= 12:
#                     age_groups['children'] += 1
#                 elif age <= 18:
#                     age_groups['youth'] += 1
#                 elif age <= 35:
#                     age_groups['young_adults'] += 1
#                 elif age <= 60:
#                     age_groups['adults'] += 1
#                 else:
#                     age_groups['seniors'] += 1
            
#             context['age_groups'] = age_groups
#             context['zone_name'] = zone.name
#             context['total_members'] = members.count()
            
#             # Cell Groups in Zone
#             cell_groups = CellGroup.objects.filter(zone=zone, is_active=True).annotate(
#                 member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#             )
#             context['cell_groups'] = cell_groups
            
#             total = members.count()
#             context['stats_summary'] = {
#                 'total_members': total,
#                 'baptized_percentage': (members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
#                 'married_percentage': (members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
#                 'male_percentage': (members.filter(gender='M').count() / total * 100) if total > 0 else 0,
#             }
#         except Zone.DoesNotExist:
#             # Fallback to old zone_name
#             members = Member.objects.filter(
#                 cell_group__zone_name=user.zone_name,
#                 cell_group__is_active=True,
#                 member_status=Member.ACTIVE
#             )
            
#             # Age Groups
#             today = date.today()
#             age_groups = {
#                 'children': 0,
#                 'youth': 0,
#                 'young_adults': 0,
#                 'adults': 0,
#                 'seniors': 0,
#             }
            
#             for member in members:
#                 age = today.year - member.date_of_birth.year
#                 if age <= 12:
#                     age_groups['children'] += 1
#                 elif age <= 18:
#                     age_groups['youth'] += 1
#                 elif age <= 35:
#                     age_groups['young_adults'] += 1
#                 elif age <= 60:
#                     age_groups['adults'] += 1
#                 else:
#                     age_groups['seniors'] += 1
            
#             context['age_groups'] = age_groups
#             context['zone_name'] = user.zone_name
#             context['total_members'] = members.count()
            
#             total = members.count()
#             context['stats_summary'] = {
#                 'total_members': total,
#                 'baptized_percentage': (members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
#                 'married_percentage': (members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
#                 'male_percentage': (members.filter(gender='M').count() / total * 100) if total > 0 else 0,
#             }
    
#     elif user.is_cell_leader() and user.assigned_cell_group:
#         members = user.assigned_cell_group.members.active()
        
#         # Age Groups
#         today = date.today()
#         age_groups = {
#             'children': 0,
#             'youth': 0,
#             'young_adults': 0,
#             'adults': 0,
#             'seniors': 0,
#         }
        
#         for member in members:
#             age = today.year - member.date_of_birth.year
#             if age <= 12:
#                 age_groups['children'] += 1
#             elif age <= 18:
#                 age_groups['youth'] += 1
#             elif age <= 35:
#                 age_groups['young_adults'] += 1
#             elif age <= 60:
#                 age_groups['adults'] += 1
#             else:
#                 age_groups['seniors'] += 1
        
#         context['age_groups'] = age_groups
        
#         total = members.count()
#         context['stats_summary'] = {
#             'total_members': total,
#             'baptized_percentage': (members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
#             'married_percentage': (members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
#             'male_percentage': (members.filter(gender='M').count() / total * 100) if total > 0 else 0,
#         }
    
#     # Note: Only render statistics.html if it exists
#     # If you don't have this template, remove this function or modify it
#     return render(request, 'dashboard/statistics.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from datetime import date, timedelta
from django.utils import timezone

from apps.members.models import Member
from apps.cell_groups.models import CellGroup
from apps.accounts.models import CustomUser
from apps.activity_logs.models import ActivityLog
from apps.zones.models import Zone


@login_required(login_url='accounts:login')
def dashboard_view(request):
    """Main dashboard view."""
    user = request.user
    
    # ✅ Redirect Viewers to the Executive Dashboard
    if user.role == 'viewer':
        return redirect('dashboard:executive_dashboard')
        
    context = {}
    
    if user.is_admin():
        context['is_admin'] = True
        context['total_members'] = Member.objects.active().count()
        context['total_cell_groups'] = CellGroup.objects.filter(is_active=True).count()
        context['total_leaders'] = CustomUser.objects.filter(role='leader', is_active_user=True).count()
        
        context['baptized_members'] = Member.objects.active().filter(is_baptized=True).count()
        context['married_members'] = Member.objects.active().filter(is_married=True).count()
        context['male_count'] = Member.objects.active().filter(gender='M').count()
        context['female_count'] = Member.objects.active().filter(gender='F').count()
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        context['recent_members'] = Member.objects.active().filter(created_at__gte=seven_days_ago).order_by('-created_at')[:5]
        
        today = date.today()
        context['birthdays_this_month'] = Member.objects.active().filter(date_of_birth__month=today.month).order_by('date_of_birth')[:10]
        
        context['cell_groups_stats'] = CellGroup.objects.filter(is_active=True).annotate(
            member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
        ).order_by('-member_count')[:5]
        
        context['recent_activities'] = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
        
        zones = Zone.objects.filter(is_active=True).annotate(
            annotated_cell_group_count=Count('cell_groups', filter=Q(cell_groups__is_active=True)),
            annotated_member_count=Count('cell_groups__members', filter=Q(
                cell_groups__members__member_status=Member.ACTIVE,
                cell_groups__is_active=True
            ))
        ).order_by('name')
        
        context['total_zones'] = zones.count()
        context['zones_without_leaders'] = zones.filter(zone_leader__isnull=True).count()
        context['zones'] = zones[:5]
        context['total_cell_groups_in_zones'] = CellGroup.objects.filter(zone__is_active=True, is_active=True).count()
        context['total_members_in_zones'] = Member.objects.filter(cell_group__zone__is_active=True, cell_group__is_active=True, member_status=Member.ACTIVE).count()
        
    elif user.is_zone_leader() and user.zone_name:
        context['is_zone_leader'] = True
        try:
            zone = Zone.objects.get(name=user.zone_name, is_active=True)
            zone_cell_groups = CellGroup.objects.filter(is_active=True, zone=zone).annotate(
                member_count=Count('members', filter=Q(members__member_status=Member.ACTIVE))
            ).order_by('name')
            zone_members = Member.objects.filter(cell_group__in=zone_cell_groups).active()
            
            context['zone_name'] = zone.name
            context['zone_cell_groups'] = zone_cell_groups
            context['zone_cell_group_count'] = zone_cell_groups.count()
            context['zone_member_count'] = zone_members.count()
            context['zone_active_members'] = zone_members.filter(member_status=Member.ACTIVE).count()
            context['zone_inactive_members'] = zone_members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count()
            context['zone_follow_up_required'] = zone_members.filter(follow_up_required=True).count()
        except Zone.DoesNotExist:
            context['zone_name'] = user.zone_name
            context['zone_cell_group_count'] = 0
            context['zone_member_count'] = 0

    elif user.is_cell_leader():
        context['is_cell_leader'] = True
        cell_group = user.assigned_cell_group
        if cell_group:
            members = cell_group.members.active()
            context['cell_group'] = cell_group
            context['total_members'] = members.count()
            context['baptized_members'] = members.filter(is_baptized=True).count()
            context['married_members'] = members.filter(is_married=True).count()
            context['male_count'] = members.filter(gender='M').count()
            context['female_count'] = members.filter(gender='F').count()
            context['recent_members'] = members.order_by('-created_at')[:5]
            context['birthdays_this_month'] = members.filter(date_of_birth__month=date.today().month).order_by('date_of_birth')[:10]
            context['follow_up_required'] = members.filter(follow_up_required=True).count()
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='accounts:login')
def statistics_view(request):
    """Detailed statistics view."""
    user = request.user
    context = {}
    
    if user.is_admin():
        all_members = Member.objects.active()
        today = date.today()
        age_groups = {'children': 0, 'youth': 0, 'young_adults': 0, 'adults': 0, 'seniors': 0}
        
        for member in all_members:
            age = today.year - member.date_of_birth.year
            if age <= 12: age_groups['children'] += 1
            elif age <= 18: age_groups['youth'] += 1
            elif age <= 35: age_groups['young_adults'] += 1
            elif age <= 60: age_groups['adults'] += 1
            else: age_groups['seniors'] += 1
        
        context['age_groups'] = age_groups
        context['total_members'] = all_members.count()
        total = context['total_members']
        context['stats_summary'] = {
            'baptized_percentage': (all_members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
            'married_percentage': (all_members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
        }
    
    return render(request, 'dashboard/statistics.html', context)


# ✅ NEW: Executive Dashboard View for Viewers (MUST BE AT THE TOP LEVEL, NO INDENTATION)
@login_required(login_url='accounts:login')
def executive_dashboard_view(request):
    """Dedicated read-only dashboard for Viewers (Archbishop, Exec Team)."""
    
    # Ensure only Viewers (and Admins for testing) can access this
    if not (request.user.role == 'viewer' or request.user.is_admin()):
        messages.error(request, "You do not have permission to view this dashboard.")
        return redirect('dashboard:dashboard')

    today = date.today()
    current_year = today.year
    current_month = today.month

    # Calculate High-Level KPIs (Read-Only)
    total_members = Member.objects.filter(member_status=Member.ACTIVE).count()
    total_zones = Zone.objects.filter(is_active=True).count()
    total_cell_groups = CellGroup.objects.filter(is_active=True).count()
    
    new_members_this_month = Member.objects.filter(
        member_status=Member.ACTIVE,
        date_joined_church__month=current_month,
        date_joined_church__year=current_year
    ).count()
    
    baptisms_this_year = Member.objects.filter(
        is_baptized=True,
        baptism_date__year=current_year
    ).count()

    recent_members = Member.objects.filter(
        member_status=Member.ACTIVE
    ).order_by('-date_joined_church')[:5]

    follow_up_needed = Member.objects.filter(
        member_status=Member.ACTIVE,
        follow_up_required=True
    ).count()

    context = {
        'total_members': total_members,
        'total_zones': total_zones,
        'total_cell_groups': total_cell_groups,
        'new_members_this_month': new_members_this_month,
        'baptisms_this_year': baptisms_this_year,
        'follow_up_needed': follow_up_needed,
        'recent_members': recent_members,
        'current_year': current_year,
    }
    
    return render(request, 'dashboard/executive_dashboard.html', context)