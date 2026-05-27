from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from datetime import date, timedelta
from django.utils import timezone

from apps.members.models import Member
from apps.cell_groups.models import CellGroup  # Fixed import
from apps.accounts.models import CustomUser
from apps.activity_logs.models import ActivityLog


@login_required(login_url='login')
def dashboard_view(request):
    """Main dashboard view."""
    user = request.user
    context = {}
    
    if user.is_admin():
        # Admin Dashboard
        context['is_admin'] = True
        
        # Overall Statistics
        context['total_members'] = Member.objects.filter(is_active=True).count()
        context['total_cell_groups'] = CellGroup.objects.filter(is_active=True).count()
        context['total_leaders'] = CustomUser.objects.filter(role='leader', is_active_user=True).count()
        
        # Member Statistics
        baptized_members = Member.objects.filter(is_active=True, is_baptized=True).count()
        married_members = Member.objects.filter(is_active=True, is_married=True).count()
        context['baptized_members'] = baptized_members
        context['married_members'] = married_members
        
        # Gender Distribution
        male_count = Member.objects.filter(is_active=True, gender='M').count()
        female_count = Member.objects.filter(is_active=True, gender='F').count()
        context['male_count'] = male_count
        context['female_count'] = female_count
        
        # Recent Members (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_members = Member.objects.filter(
            is_active=True,
            created_at__gte=seven_days_ago
        ).order_by('-created_at')[:5]
        context['recent_members'] = recent_members
        
        # Birthdays This Month
        today = date.today()
        birthdays_this_month = Member.objects.filter(
            is_active=True,
            date_of_birth__month=today.month
        ).order_by('date_of_birth')[:10]
        context['birthdays_this_month'] = birthdays_this_month
        
        # Cell Groups with Member Count
        cell_groups_stats = CellGroup.objects.filter(
            is_active=True
        ).annotate(
            member_count=Count('members', filter=Q(members__is_active=True))
        ).order_by('-member_count')[:5]
        context['cell_groups_stats'] = cell_groups_stats
        
        # Recent Activity
        recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
        context['recent_activities'] = recent_activities
        
    elif user.is_cell_leader():
        # Cell Leader Dashboard
        context['is_cell_leader'] = True
        cell_group = user.assigned_cell_group
        
        if cell_group:
            # Cell Group Statistics
            members = cell_group.members.filter(is_active=True)
            context['cell_group'] = cell_group
            context['total_members'] = members.count()
            
            # Member Statistics
            context['baptized_members'] = members.filter(is_baptized=True).count()
            context['married_members'] = members.filter(is_married=True).count()
            
            # Gender Distribution
            context['male_count'] = members.filter(gender='M').count()
            context['female_count'] = members.filter(gender='F').count()
            
            # Recently Added Members
            recent_members = members.order_by('-created_at')[:5]
            context['recent_members'] = recent_members
            
            # Birthdays This Month
            today = date.today()
            birthdays = members.filter(date_of_birth__month=today.month).order_by('date_of_birth')[:10]
            context['birthdays_this_month'] = birthdays
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required(login_url='login')
def statistics_view(request):
    """Detailed statistics view."""
    user = request.user
    context = {}
    
    if user.is_admin():
        # Overall statistics
        all_members = Member.objects.filter(is_active=True)
        
        # Age Groups
        today = date.today()
        age_groups = {
            'children': 0,  # 0-12
            'youth': 0,      # 13-18
            'young_adults': 0,  # 19-35
            'adults': 0,     # 36-60
            'seniors': 0,    # 60+
        }
        
        for member in all_members:
            age = today.year - member.date_of_birth.year
            if age <= 12:
                age_groups['children'] += 1
            elif age <= 18:
                age_groups['youth'] += 1
            elif age <= 35:
                age_groups['young_adults'] += 1
            elif age <= 60:
                age_groups['adults'] += 1
            else:
                age_groups['seniors'] += 1
        
        context['age_groups'] = age_groups
        
        # Monthly Membership Growth (last 12 months)
        growth_data = {}
        for i in range(12):
            month_date = today - timedelta(days=30*i)
            month_members = Member.objects.filter(
                created_at__year=month_date.year,
                created_at__month=month_date.month
            ).count()
            growth_data[month_date.strftime('%B')] = month_members
        
        context['growth_data'] = dict(reversed(list(growth_data.items())))
        
        # Cell Group Rankings
        cell_groups = CellGroup.objects.filter(is_active=True).annotate(
            member_count=Count('members', filter=Q(members__is_active=True))
        ).order_by('-member_count')
        context['cell_groups'] = cell_groups
        
        # Statistics Summary
        total = all_members.count()
        context['stats_summary'] = {
            'total_members': total,
            'baptized_percentage': (all_members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
            'married_percentage': (all_members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
            'male_percentage': (all_members.filter(gender='M').count() / total * 100) if total > 0 else 0,
        }
    
    elif user.is_cell_leader() and user.assigned_cell_group:
        members = user.assigned_cell_group.members.filter(is_active=True)
        
        # Age Groups
        today = date.today()
        age_groups = {
            'children': 0,
            'youth': 0,
            'young_adults': 0,
            'adults': 0,
            'seniors': 0,
        }
        
        for member in members:
            age = today.year - member.date_of_birth.year
            if age <= 12:
                age_groups['children'] += 1
            elif age <= 18:
                age_groups['youth'] += 1
            elif age <= 35:
                age_groups['young_adults'] += 1
            elif age <= 60:
                age_groups['adults'] += 1
            else:
                age_groups['seniors'] += 1
        
        context['age_groups'] = age_groups
        
        total = members.count()
        context['stats_summary'] = {
            'total_members': total,
            'baptized_percentage': (members.filter(is_baptized=True).count() / total * 100) if total > 0 else 0,
            'married_percentage': (members.filter(is_married=True).count() / total * 100) if total > 0 else 0,
            'male_percentage': (members.filter(gender='M').count() / total * 100) if total > 0 else 0,
        }
    
    return render(request, 'dashboard/statistics.html', context)

