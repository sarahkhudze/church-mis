# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db.models import Q, Count
# from django.utils import timezone
# from datetime import date, datetime

# from .models import Member, AttendanceRecord
# from apps.cell_groups.models import CellGroup
# from apps.accounts.models import Zone
# from .forms import MemberForm, MemberSearchForm, CellGroupForm, BulkMemberActionForm
# from apps.accounts.utils import log_activity, can_manage_member, get_user_members


# @login_required(login_url='login')
# def member_list_view(request):
#     """Display list of members with filtering and searching."""
#     show_inactive = request.user.is_admin() and request.GET.get('show_inactive') == 'on'
#     members = Member.objects.all() if show_inactive else get_user_members(request.user)
    
#     form = MemberSearchForm(request.GET)
    
#     # Search
#     search_query = request.GET.get('search', '')
#     if search_query:
#         members = members.filter(
#             Q(first_name__icontains=search_query) |
#             Q(last_name__icontains=search_query) |
#             Q(email__icontains=search_query) |
#             Q(phone_number__icontains=search_query)
#         )
    
#     # Gender filter
#     gender = request.GET.get('gender', '')
#     if gender:
#         members = members.filter(gender=gender)
    
#     # Baptized filter
#     is_baptized = request.GET.get('is_baptized', '')
#     if is_baptized:
#         members = members.filter(is_baptized=is_baptized == 'True')
    
#     # Married filter
#     is_married = request.GET.get('is_married', '')
#     if is_married:
#         members = members.filter(is_married=is_married == 'True')
    
#     # Cell group filter
#     cell_group = request.GET.get('cell_group', '')
#     if cell_group:
#         members = members.filter(cell_group_id=cell_group)
    
#     # Age range filter
#     age_from = request.GET.get('age_from', '')
#     age_to = request.GET.get('age_to', '')
#     if age_from or age_to:
#         today = date.today()
#         if age_from:
#             birth_year_to = today.year - int(age_from)
#             members = members.filter(date_of_birth__lte=date(birth_year_to, 12, 31))
#         if age_to:
#             birth_year_from = today.year - int(age_to)
#             members = members.filter(date_of_birth__gte=date(birth_year_from, 1, 1))
    
#     if not show_inactive:
#         members = members.active()

#     member_status = request.GET.get('member_status', '')
#     if member_status:
#         members = members.filter(member_status=member_status)

#     # Ordering
#     ordering = request.GET.get('ordering', '-updated_at')
#     members = members.order_by(ordering)
    
#     # Logging
#     if search_query or gender or is_baptized or is_married or member_status or cell_group or age_from or age_to or show_inactive:
#         log_activity(
#             user=request.user,
#             action='search',
#             entity_type='member',
#             description='Searched/filtered members',
#             request=request
#         )
    
#     context = {
#         'members': members,
#         'form': form,
#         'search_query': search_query,
#     }
    
#     return render(request, 'members/member_list.html', context)


# @login_required(login_url='login')
# def member_detail_view(request, pk):
#     """Display member details."""
#     member = get_object_or_404(Member, pk=pk)
    
#     # Check permissions
#     if not (
#         request.user.is_admin() or
#         (request.user.is_zone_leader() and member.cell_group and member.cell_group.zone == request.user.zone) or
#         (request.user.is_cell_leader() and member.cell_group == request.user.assigned_cell_group)
#     ):
#         messages.error(request, 'You do not have permission to view this member.')
#         return redirect('members:member_list')
    
#     log_activity(
#         user=request.user,
#         action='view',
#         entity_type='member',
#         description=f'Viewed member: {member.get_full_name()}',
#         entity_id=member.id,
#         request=request
#     )
    
#     attendance_history = AttendanceRecord.objects.filter(member=member).order_by('-meeting_date')[:10]

#     context = {
#         'member': member,
#         'attendance_history': attendance_history,
#     }
#     return render(request, 'members/member_detail.html', context)


# @login_required(login_url='login')
# def member_create_view(request):
#     """Create a new member."""
#     if not (request.user.is_admin() or request.user.is_cell_leader() or request.user.is_zone_leader()):
#         messages.error(request, 'You do not have permission to add members.')
#         return redirect('members:member_list')
    
#     if request.method == 'POST':
#         form = MemberForm(request.POST)
#         if form.is_valid():
#             member = form.save(commit=False)
#             member.created_by = request.user
            
#             # If cell leader, assign to their cell group
#             if request.user.is_cell_leader() and not member.cell_group:
#                 member.cell_group = request.user.assigned_cell_group
            
#             member.save()
            
#             log_activity(
#                 user=request.user,
#                 action='create',
#                 entity_type='member',
#                 description=f'Created member: {member.get_full_name()}',
#                 entity_id=member.id,
#                 request=request
#             )
            
#             messages.success(request, f'Member {member.get_full_name()} added successfully!')
#             return redirect('members:member_detail', pk=member.id)
#     else:
#         form = MemberForm()
#         # Restrict the available cell groups by role and zone
#         if request.user.is_zone_leader() and request.user.zone:
#             form.fields['cell_group'].queryset = CellGroup.objects.filter(
#                 zone=request.user.zone,
#                 is_active=True
#             )
#         elif request.user.is_cell_leader() and request.user.assigned_cell_group:
#             form.fields['cell_group'].queryset = CellGroup.objects.filter(
#                 id=request.user.assigned_cell_group.id
#             )
    
#     context = {'form': form}
#     return render(request, 'members/member_form.html', context)


# @login_required(login_url='login')
# def member_edit_view(request, pk):
#     """Edit member information."""
#     member = get_object_or_404(Member, pk=pk)
    
#     # Check permissions
#     if not can_manage_member(request.user, member):
#         messages.error(request, 'You do not have permission to edit this member.')
#         return redirect('members:member_list')
    
#     if request.method == 'POST':
#         form = MemberForm(request.POST, instance=member)
#         if form.is_valid():
#             member = form.save()
            
#             log_activity(
#                 user=request.user,
#                 action='edit',
#                 entity_type='member',
#                 description=f'Edited member: {member.get_full_name()}',
#                 entity_id=member.id,
#                 request=request
#             )
            
#             messages.success(request, 'Member information updated successfully!')
#             return redirect('members:member_detail', pk=member.id)
#     else:
#         form = MemberForm(instance=member)
#         # Restrict the available cell groups by role and zone
#         if request.user.is_zone_leader() and request.user.zone:
#             form.fields['cell_group'].queryset = CellGroup.objects.filter(
#                 zone=request.user.zone,
#                 is_active=True
#             )
#         elif request.user.is_cell_leader() and request.user.assigned_cell_group:
#             form.fields['cell_group'].queryset = CellGroup.objects.filter(
#                 id=request.user.assigned_cell_group.id
#             )
    
#     context = {'form': form, 'member': member}
#     return render(request, 'members/member_form.html', context)


# @login_required(login_url='login')
# def member_delete_view(request, pk):
#     """Delete/deactivate a member."""
#     member = get_object_or_404(Member, pk=pk)
    
#     # Check permissions
#     if not request.user.is_admin():
#         messages.error(request, 'Only administrators can delete members.')
#         return redirect('members:member_list')
    
#     if request.method == 'POST':
#         member_name = member.get_full_name()
#         member.member_status = Member.LEFT
#         member.save()
        
#         log_activity(
#             user=request.user,
#             action='delete',
#             entity_type='member',
#             description=f'Deactivated member: {member_name}',
#             entity_id=member.id,
#             request=request
#         )
        
#         messages.success(request, f'Member {member_name} has been deactivated.')
#         return redirect('members:member_list')
    
#     context = {'member': member}
#     return render(request, 'members/member_delete.html', context)


# @login_required(login_url='login')
# def bulk_member_action_view(request):
#     """Perform bulk actions on members."""
#     if not request.user.is_admin():
#         messages.error(request, 'Only administrators can perform bulk actions.')
#         return redirect('members:member_list')
    
#     members_ids = request.GET.getlist('members')
    
#     if request.method == 'POST':
#         form = BulkMemberActionForm(request.POST)
#         if form.is_valid():
#             action = form.cleaned_data['action']
#             target_cell_group = form.cleaned_data.get('target_cell_group')
            
#             members = Member.objects.filter(id__in=members_ids)
            
#             if action == 'transfer_group' and target_cell_group:
#                 members.update(cell_group=target_cell_group)
#                 log_activity(
#                     user=request.user,
#                     action='edit',
#                     entity_type='member',
#                     description=f'Transferred {members.count()} members to {target_cell_group.name}',
#                     request=request
#                 )
#                 messages.success(request, f'{members.count()} members transferred successfully!')
            
#             elif action == 'mark_baptized':
#                 members.update(is_baptized=True)
#                 log_activity(
#                     user=request.user,
#                     action='edit',
#                     entity_type='member',
#                     description=f'Marked {members.count()} members as baptized',
#                     request=request
#                 )
#                 messages.success(request, f'{members.count()} members marked as baptized!')
            
#             elif action == 'mark_married':
#                 members.update(is_married=True)
#                 log_activity(
#                     user=request.user,
#                     action='edit',
#                     entity_type='member',
#                     description=f'Marked {members.count()} members as married',
#                     request=request
#                 )
#                 messages.success(request, f'{members.count()} members marked as married!')
            
#             elif action == 'deactivate':
#                 members.update(member_status=Member.LEFT)
#                 log_activity(
#                     user=request.user,
#                     action='edit',
#                     entity_type='member',
#                     description=f'Deactivated {members.count()} members',
#                     request=request
#                 )
#                 messages.success(request, f'{members.count()} members deactivated!')
            
#             elif action == 'activate':
#                 members.update(member_status=Member.ACTIVE)
#                 log_activity(
#                     user=request.user,
#                     action='edit',
#                     entity_type='member',
#                     description=f'Activated {members.count()} members',
#                     request=request
#                 )
#                 messages.success(request, f'{members.count()} members activated!')
            
#             return redirect('members:member_list')
#     else:
#         form = BulkMemberActionForm()
    
#     members = Member.objects.filter(id__in=members_ids)
#     context = {
#         'form': form,
#         'members': members,
#         'members_ids': ','.join(members_ids),
#     }
    
#     return render(request, 'members/bulk_action.html', context)


# # Cell Group Views (Admin only)

# # @login_required(login_url='login')
# # def cell_group_list_view(request):
# #     """Display list of cell groups."""
# #     if not request.user.is_admin():
# #         messages.error(request, 'Only administrators can view cell groups.')
# #         return redirect('members:member_list')
    
# #     cell_groups = CellGroup.objects.filter(is_active=True).annotate(
# #         member_count=Count('members', filter=Q(members__is_active=True))
# #     )
    
# #     search_query = request.GET.get('search', '')
# #     if search_query:
# #         cell_groups = cell_groups.filter(
# #             Q(name__icontains=search_query) |
# #             Q(location__icontains=search_query)
# #         )
    
# #     context = {
# #         'cell_groups': cell_groups,
# #         'search_query': search_query,
# #     }
    
# #     return render(request, 'members/cell_group_list.html', context)

# @login_required(login_url='login')
# def cell_group_list_view(request):
#     """Display list of cell groups."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'Only administrators and zone leaders can view cell groups.')
#         return redirect('members:member_list')
    
#     # Use 'total_members' instead of 'member_count' to avoid conflicts
#     base_queryset = CellGroup.objects.filter(is_active=True)
#     if request.user.is_zone_leader() and not request.user.is_admin():
#         base_queryset = base_queryset.filter(zone=request.user.zone, approval_status__in=['pending', 'approved'])

#     cell_groups = base_queryset.annotate(
#         total_members=Count('members', filter=Q(members__member_status=Member.ACTIVE))
#     )
    
#     search_query = request.GET.get('search', '')
#     if search_query:
#         cell_groups = cell_groups.filter(
#             Q(name__icontains=search_query) |
#             Q(location__icontains=search_query)
#         )
    
#     context = {
#         'cell_groups': cell_groups,
#         'search_query': search_query,
#     }
    
#     return render(request, 'members/cell_group_list.html', context)

# @login_required(login_url='login')
# def cell_group_detail_view(request, pk):
#     """Display cell group details."""
#     if not (request.user.is_admin() or request.user.is_zone_leader() or request.user.is_cell_leader()):
#         messages.error(request, 'Only administrators, zone leaders, and cell leaders can view cell group details.')
#         return redirect('members:member_list')
    
#     cell_group = get_object_or_404(CellGroup, pk=pk)
#     if request.user.is_zone_leader() and not request.user.is_admin() and cell_group.zone != request.user.zone:
#         messages.error(request, 'You do not have permission to view this cell group.')
#         return redirect('members:cell_group_list')
#     if request.user.is_cell_leader() and not request.user.is_admin() and cell_group.id != request.user.assigned_cell_group_id:
#         messages.error(request, 'You do not have permission to view this cell group.')
#         return redirect('members:cell_group_list')

#     members = cell_group.members.active()
    
#     attendance_history = AttendanceRecord.objects.filter(cell_group=cell_group).order_by('-meeting_date')[:10]

#     context = {
#         'cell_group': cell_group,
#         'members': members,
#         'member_count': members.count(),
#         'attendance_history': attendance_history,
#     }
    
#     return render(request, 'members/cell_group_detail.html', context)


# @login_required(login_url='login')
# def record_attendance_view(request, cell_group_id):
#     """Record attendance for a cell-group meeting."""
#     cell_group = get_object_or_404(CellGroup, pk=cell_group_id)
#     can_manage = (
#         request.user.is_admin() or
#         (request.user.is_zone_leader() and request.user.zone and cell_group.zone == request.user.zone) or
#         (request.user.is_cell_leader() and request.user.assigned_cell_group_id == cell_group.id) or
#         (cell_group.leader_id == request.user.id)
#     )

#     if not can_manage:
#         messages.error(request, 'You do not have permission to record attendance for this cell group.')
#         return redirect('members:cell_group_detail', pk=cell_group.id)

#     members = cell_group.members.filter(member_status=Member.ACTIVE).order_by('last_name', 'first_name')

#     if request.method == 'POST':
#         meeting_date = request.POST.get('meeting_date')
#         if not meeting_date:
#             messages.error(request, 'Please select a meeting date.')
#             return redirect('members:record_attendance', cell_group_id=cell_group.id)

#         parsed_date = datetime.strptime(meeting_date, '%Y-%m-%d').date()
#         for member in members:
#             status = request.POST.get(f'status_{member.id}')
#             if status in ['present', 'absent']:
#                 AttendanceRecord.objects.update_or_create(
#                     member=member,
#                     cell_group=cell_group,
#                     meeting_date=parsed_date,
#                     defaults={'status': status, 'notes': request.POST.get(f'notes_{member.id}', '')}
#                 )

#         messages.success(request, f'Attendance recorded for {cell_group.name}.')
#         return redirect('members:cell_group_detail', pk=cell_group.id)

#     context = {
#         'cell_group': cell_group,
#         'members': members,
#         'default_date': timezone.now().date().isoformat(),
#     }
#     return render(request, 'members/attendance_record.html', context)


# # @login_required(login_url='login')
# # def cell_group_create_view(request):
# #     """Create a new cell group."""
# #     if not request.user.is_zone_leader():
# #         messages.error(request, 'Only zone leaders can create cell groups.')
# #         return redirect('members:member_list')
    
# #     if request.method == 'POST':
# #         form = CellGroupForm(request.POST, user=request.user)  # Pass user to form
# #         if form.is_valid():
# #             cell_group = form.save(commit=False)
# #             if request.user.is_zone_leader() and request.user.zone:
# #                 # Auto-assign the zone from the user's zone (using the Zone model)
# #                 cell_group.zone = request.user.zone
# #             cell_group.approval_status = 'pending'
# #             cell_group.save()
            
# #             log_activity(
# #                 user=request.user,
# #                 action='create',
# #                 entity_type='cell_group',
# #                 description=f'Created cell group: {cell_group.name}',
# #                 entity_id=cell_group.id,
# #                 request=request
# #             )
            
# #             if cell_group.approval_status == 'pending':
# #                 messages.success(request, f'Cell group {cell_group.name} submitted for approval.')
# #             else:
# #                 messages.success(request, f'Cell group {cell_group.name} created successfully!')
# #             return redirect('members:cell_group_detail', pk=cell_group.id)
# #     else:
# #         form = CellGroupForm(user=request.user)  # Pass user to form
    
# #     context = {'form': form}
# #     return render(request, 'members/cell_group_form.html', context)

# # @login_required(login_url='login')
# # def cell_group_create_view(request):
# #     """Create a new cell group."""
# #     print("=== DEBUG: cell_group_create_view ===")
# #     print(f"User: {request.user.username}")
# #     print(f"User role: {request.user.role}")
# #     print(f"User is_zone_leader: {request.user.is_zone_leader()}")
# #     print(f"User zone: {getattr(request.user, 'zone', 'NO ZONE FIELD')}")
# #     print(f"User zone_name: {getattr(request.user, 'zone_name', 'NO ZONE_NAME FIELD')}")
# #     print(f"Available user attributes: {[field.name for field in request.user._meta.fields]}")
    
# #     if not request.user.is_zone_leader():
# #         print("User is NOT a zone leader - redirecting")
# #         messages.error(request, 'Only zone leaders can create cell groups.')
# #         return redirect('members:member_list')
# #     else:
# #         print("User IS a zone leader - proceeding")
    
# #     if request.method == 'POST':
# #         print("POST request received")
# #         form = CellGroupForm(request.POST, user=request.user)  # Pass user to form
# #         print(f"Form created with user parameter: {form}")
# #         if form.is_valid():
# #             print("Form is valid")
# #             cell_group = form.save(commit=False)
# #             if request.user.is_zone_leader() and request.user.zone:
# #                 # Auto-assign the zone from the user's zone (using the Zone model)
# #                 cell_group.zone = request.user.zone
# #             cell_group.approval_status = 'pending'
# #             cell_group.save()
            
# #             log_activity(
# #                 user=request.user,
# #                 action='create',
# #                 entity_type='cell_group',
# #                 description=f'Created cell group: {cell_group.name}',
# #                 entity_id=cell_group.id,
# #                 request=request
# #             )
            
# #             if cell_group.approval_status == 'pending':
# #                 messages.success(request, f'Cell group {cell_group.name} submitted for approval.')
# #             else:
# #                 messages.success(request, f'Cell group {cell_group.name} created successfully!')
# #             return redirect('members:cell_group_detail', pk=cell_group.id)
# #     else:
# #         print("GET request - showing form")
# #         form = CellGroupForm(user=request.user)  # Pass user to form
# #         print(f"Form created with user parameter: {form}")
    
# #     context = {'form': form}
# #     return render(request, 'members/cell_group_form.html', context)
# @login_required(login_url='login')
# def cell_group_create_view(request):
#     """Create a new cell group."""
#     if not request.user.is_zone_leader():
#         messages.error(request, 'Only zone leaders can create cell groups.')
#         return redirect('members:member_list')
    
#     if request.method == 'POST':
#         form = CellGroupForm(request.POST, user=request.user)  # Pass user to form
#         if form.is_valid():
#             cell_group = form.save(commit=False)
#             if request.user.is_zone_leader() and request.user.zone_name:
#                 # Auto-assign the zone from the user's zone_name field
#                 from apps.zones.models import Zone as ZonesAppZone
#                 try:
#                     zone = ZonesAppZone.objects.get(name=request.user.zone_name)
#                     cell_group.zone = zone
#                 except ZonesAppZone.DoesNotExist:
#                     pass  # Or handle error appropriately
#             cell_group.approval_status = 'pending'
#             cell_group.save()
            
#             log_activity(
#                 user=request.user,
#                 action='create',
#                 entity_type='cell_group',
#                 description=f'Created cell group: {cell_group.name}',
#                 entity_id=cell_group.id,
#                 request=request
#             )
            
#             if cell_group.approval_status == 'pending':
#                 messages.success(request, f'Cell group {cell_group.name} submitted for approval.')
#             else:
#                 messages.success(request, f'Cell group {cell_group.name} created successfully!')
#             return redirect('members:cell_group_detail', pk=cell_group.id)
#     else:
#         form = CellGroupForm(user=request.user)  # Pass user to form
    
#     context = {'form': form}
#     return render(request, 'members/cell_group_form.html', context)
# @login_required(login_url='login')
# def cell_group_approve_view(request, pk):
#     """Approve a pending cell-group creation request."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'You do not have permission to approve cell groups.')
#         return redirect('members:member_list')

#     cell_group = get_object_or_404(CellGroup, pk=pk)
#     if request.user.is_zone_leader() and not request.user.is_admin() and cell_group.zone != request.user.zone:
#         messages.error(request, 'You do not have permission to approve this cell group.')
#         return redirect('members:cell_group_list')
#     cell_group.approval_status = 'approved'
#     cell_group.save()

#     log_activity(
#         user=request.user,
#         action='approve',
#         entity_type='cell_group',
#         description=f'Approved cell group: {cell_group.name}',
#         entity_id=cell_group.id,
#         request=request
#     )
#     messages.success(request, f'Cell group {cell_group.name} approved successfully.')
#     return redirect('members:cell_group_list')


# @login_required(login_url='login')
# def cell_group_reject_view(request, pk):
#     """Reject a pending cell-group creation request."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'You do not have permission to reject cell groups.')
#         return redirect('members:member_list')

#     cell_group = get_object_or_404(CellGroup, pk=pk)
#     if request.user.is_zone_leader() and not request.user.is_admin() and cell_group.zone != request.user.zone:
#         messages.error(request, 'You do not have permission to reject this cell group.')
#         return redirect('members:cell_group_list')
#     cell_group.approval_status = 'rejected'
#     cell_group.save()

#     log_activity(
#         user=request.user,
#         action='reject',
#         entity_type='cell_group',
#         description=f'Rejected cell group: {cell_group.name}',
#         entity_id=cell_group.id,
#         request=request
#     )
#     messages.success(request, f'Cell group {cell_group.name} rejected.')
#     return redirect('members:cell_group_list')


# @login_required(login_url='login')
# def cell_group_edit_view(request, pk):
#     """Edit cell group."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'Only administrators and zone leaders can edit cell groups.')
#         return redirect('members:member_list')
    
#     cell_group = get_object_or_404(CellGroup, pk=pk)
#     if request.user.is_zone_leader() and not request.user.is_admin() and cell_group.zone != request.user.zone:
#         messages.error(request, 'You do not have permission to edit this cell group.')
#         return redirect('members:cell_group_list')
    
#     if request.method == 'POST':
#         form = CellGroupForm(request.POST, instance=cell_group, user=request.user)  # Pass user to form
#         if form.is_valid():
#             cell_group = form.save(commit=False)
#             if cell_group.zone:
#                 cell_group.zone_name = cell_group.zone.name
#             else:
#                 cell_group.zone_name = ''
#             cell_group.save()
            
#             log_activity(
#                 user=request.user,
#                 action='edit',
#                 entity_type='cell_group',
#                 description=f'Edited cell group: {cell_group.name}',
#                 entity_id=cell_group.id,
#                 request=request
#             )
            
#             messages.success(request, 'Cell group updated successfully!')
#             return redirect('members:cell_group_detail', pk=cell_group.id)
#     else:
#         form = CellGroupForm(instance=cell_group, user=request.user)  # Pass user to form
    
#     context = {'form': form, 'cell_group': cell_group}
#     return render(request, 'members/cell_group_form.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import date, datetime

from .models import Member, AttendanceRecord
from apps.cell_groups.models import CellGroup
from .forms import MemberForm, MemberSearchForm, CellGroupForm, BulkMemberActionForm
from apps.accounts.utils import log_activity, can_manage_member, get_user_members
from .forms import MemberTransferForm # Make sure to import this at the top


@login_required(login_url='login')
def member_list_view(request):
    """Display list of members with filtering and searching."""
    show_inactive = request.user.is_admin() and request.GET.get('show_inactive') == 'on'
    members = Member.objects.all() if show_inactive else get_user_members(request.user)
    
    form = MemberSearchForm(request.GET)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Gender filter
    gender = request.GET.get('gender', '')
    if gender:
        members = members.filter(gender=gender)
    
    # Baptized filter
    is_baptized = request.GET.get('is_baptized', '')
    if is_baptized:
        members = members.filter(is_baptized=is_baptized == 'True')
    
    # Married filter
    is_married = request.GET.get('is_married', '')
    if is_married:
        members = members.filter(is_married=is_married == 'True')
    
    # Cell group filter
    cell_group = request.GET.get('cell_group', '')
    if cell_group:
        members = members.filter(cell_group_id=cell_group)
    
    # Age range filter
    age_from = request.GET.get('age_from', '')
    age_to = request.GET.get('age_to', '')
    if age_from or age_to:
        today = date.today()
        if age_from:
            birth_year_to = today.year - int(age_from)
            members = members.filter(date_of_birth__lte=date(birth_year_to, 12, 31))
        if age_to:
            birth_year_from = today.year - int(age_to)
            members = members.filter(date_of_birth__gte=date(birth_year_from, 1, 1))
    
    if not show_inactive:
        members = members.active()

    member_status = request.GET.get('member_status', '')
    if member_status:
        members = members.filter(member_status=member_status)

    # Ordering
    ordering = request.GET.get('ordering', '-updated_at')
    members = members.order_by(ordering)
    
    # Logging
    if search_query or gender or is_baptized or is_married or member_status or cell_group or age_from or age_to or show_inactive:
        log_activity(
            user=request.user,
            action='search',
            entity_type='member',
            description='Searched/filtered members',
            request=request
        )
    
    context = {
        'members': members,
        'form': form,
        'search_query': search_query,
    }
    
    return render(request, 'members/member_list.html', context)


@login_required(login_url='login')
def member_detail_view(request, pk):
    """Display member details."""
    member = get_object_or_404(Member, pk=pk)
    
    # Check permissions (FIXED: use zone_name instead of zone)
    user_zone_name = getattr(request.user, 'zone_name', None)
    if not (
        request.user.is_admin() or
        (request.user.is_zone_leader() and member.cell_group and member.cell_group.zone and member.cell_group.zone.name == user_zone_name) or
        (request.user.is_cell_leader() and member.cell_group == request.user.assigned_cell_group)
    ):
        messages.error(request, 'You do not have permission to view this member.')
        return redirect('members:member_list')
    
    log_activity(
        user=request.user,
        action='view',
        entity_type='member',
        description=f'Viewed member: {member.get_full_name()}',
        entity_id=member.id,
        request=request
    )
    
    attendance_history = AttendanceRecord.objects.filter(member=member).order_by('-meeting_date')[:10]

    context = {
        'member': member,
        'attendance_history': attendance_history,
    }
    return render(request, 'members/member_detail.html', context)


@login_required(login_url='login')
def member_create_view(request):
    """Create a new member."""
    if not (request.user.is_admin() or request.user.is_cell_leader() or request.user.is_zone_leader()):
        messages.error(request, 'You do not have permission to add members.')
        return redirect('members:member_list')
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.created_by = request.user
            
            # If cell leader, assign to their cell group
            if request.user.is_cell_leader() and not member.cell_group:
                member.cell_group = request.user.assigned_cell_group
            
            member.save()
            
            log_activity(
                user=request.user,
                action='create',
                entity_type='member',
                description=f'Created member: {member.get_full_name()}',
                entity_id=member.id,
                request=request
            )
            
            messages.success(request, f'Member {member.get_full_name()} added successfully!')
            return redirect('members:member_detail', pk=member.id)
    else:
        form = MemberForm()
        # Restrict the available cell groups by role and zone (FIXED: use zone__name=zone_name)
        if request.user.is_zone_leader() and request.user.zone_name:
            form.fields['cell_group'].queryset = CellGroup.objects.filter(
                zone__name=request.user.zone_name,
                is_active=True
            )
        elif request.user.is_cell_leader() and request.user.assigned_cell_group:
            form.fields['cell_group'].queryset = CellGroup.objects.filter(
                id=request.user.assigned_cell_group.id
            )
    
    context = {'form': form}
    return render(request, 'members/member_form.html', context)


@login_required(login_url='login')
def member_edit_view(request, pk):
    """Edit member information."""
    member = get_object_or_404(Member, pk=pk)
    
    # Check permissions
    if not can_manage_member(request.user, member):
        messages.error(request, 'You do not have permission to edit this member.')
        return redirect('members:member_list')
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            
            log_activity(
                user=request.user,
                action='edit',
                entity_type='member',
                description=f'Edited member: {member.get_full_name()}',
                entity_id=member.id,
                request=request
            )
            
            messages.success(request, 'Member information updated successfully!')
            return redirect('members:member_detail', pk=member.id)
    else:
        form = MemberForm(instance=member)
        # Restrict the available cell groups by role and zone (FIXED: use zone__name=zone_name)
        if request.user.is_zone_leader() and request.user.zone_name:
            form.fields['cell_group'].queryset = CellGroup.objects.filter(
                zone__name=request.user.zone_name,
                is_active=True
            )
        elif request.user.is_cell_leader() and request.user.assigned_cell_group:
            form.fields['cell_group'].queryset = CellGroup.objects.filter(
                id=request.user.assigned_cell_group.id
            )
    
    context = {'form': form, 'member': member}
    return render(request, 'members/member_form.html', context)


@login_required(login_url='login')
def member_delete_view(request, pk):
    """Delete/deactivate a member."""
    member = get_object_or_404(Member, pk=pk)
    
    # Check permissions
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can delete members.')
        return redirect('members:member_list')
    
    if request.method == 'POST':
        member_name = member.get_full_name()
        member.member_status = Member.LEFT
        member.save()
        
        log_activity(
            user=request.user,
            action='delete',
            entity_type='member',
            description=f'Deactivated member: {member_name}',
            entity_id=member.id,
            request=request
        )
        
        messages.success(request, f'Member {member_name} has been deactivated.')
        return redirect('members:member_list')
    
    context = {'member': member}
    return render(request, 'members/member_delete.html', context)


@login_required(login_url='login')
def bulk_member_action_view(request):
    """Perform bulk actions on members."""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can perform bulk actions.')
        return redirect('members:member_list')
    
    members_ids = request.GET.getlist('members')
    
    if request.method == 'POST':
        form = BulkMemberActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            target_cell_group = form.cleaned_data.get('target_cell_group')
            
            members = Member.objects.filter(id__in=members_ids)
            
            if action == 'transfer_group' and target_cell_group:
                members.update(cell_group=target_cell_group)
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='member',
                    description=f'Transferred {members.count()} members to {target_cell_group.name}',
                    request=request
                )
                messages.success(request, f'{members.count()} members transferred successfully!')
            
            elif action == 'mark_baptized':
                members.update(is_baptized=True)
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='member',
                    description=f'Marked {members.count()} members as baptized',
                    request=request
                )
                messages.success(request, f'{members.count()} members marked as baptized!')
            
            elif action == 'mark_married':
                members.update(is_married=True)
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='member',
                    description=f'Marked {members.count()} members as married',
                    request=request
                )
                messages.success(request, f'{members.count()} members marked as married!')
            
            elif action == 'deactivate':
                members.update(member_status=Member.LEFT)
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='member',
                    description=f'Deactivated {members.count()} members',
                    request=request
                )
                messages.success(request, f'{members.count()} members deactivated!')
            
            elif action == 'activate':
                members.update(member_status=Member.ACTIVE)
                log_activity(
                    user=request.user,
                    action='edit',
                    entity_type='member',
                    description=f'Activated {members.count()} members',
                    request=request
                )
                messages.success(request, f'{members.count()} members activated!')
            
            return redirect('members:member_list')
    else:
        form = BulkMemberActionForm()
    
    members = Member.objects.filter(id__in=members_ids)
    context = {
        'form': form,
        'members': members,
        'members_ids': ','.join(members_ids),
    }
    
    return render(request, 'members/bulk_action.html', context)


@login_required(login_url='login')
def cell_group_list_view(request):
    """Display list of cell groups."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'Only administrators and zone leaders can view cell groups.')
        return redirect('members:member_list')
    
    base_queryset = CellGroup.objects.filter(is_active=True)
    # FIXED: use zone__name=zone_name
    if request.user.is_zone_leader() and not request.user.is_admin():
        base_queryset = base_queryset.filter(
            zone__name=request.user.zone_name, 
            approval_status__in=['pending', 'approved']
        )

    cell_groups = base_queryset.annotate(
        total_members=Count('members', filter=Q(members__member_status=Member.ACTIVE))
    )
    
    search_query = request.GET.get('search', '')
    if search_query:
        cell_groups = cell_groups.filter(
            Q(name__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'cell_groups': cell_groups,
        'search_query': search_query,
    }
    
    return render(request, 'members/cell_group_list.html', context)


@login_required(login_url='login')
def cell_group_detail_view(request, pk):
    """Display cell group details."""
    if not (request.user.is_admin() or request.user.is_zone_leader() or request.user.is_cell_leader()):
        messages.error(request, 'Only administrators, zone leaders, and cell leaders can view cell group details.')
        return redirect('members:member_list')
    
    cell_group = get_object_or_404(CellGroup, pk=pk)
    
    # FIXED: use zone.name == zone_name
    if request.user.is_zone_leader() and not request.user.is_admin() and (not cell_group.zone or cell_group.zone.name != request.user.zone_name):
        messages.error(request, 'You do not have permission to view this cell group.')
        return redirect('members:cell_group_list')
        
    if request.user.is_cell_leader() and not request.user.is_admin() and cell_group.id != request.user.assigned_cell_group_id:
        messages.error(request, 'You do not have permission to view this cell group.')
        return redirect('members:cell_group_list')

    members = cell_group.members.active()
    attendance_history = AttendanceRecord.objects.filter(cell_group=cell_group).order_by('-meeting_date')[:10]

    context = {
        'cell_group': cell_group,
        'members': members,
        'member_count': members.count(),
        'attendance_history': attendance_history,
    }
    
    return render(request, 'members/cell_group_detail.html', context)


@login_required(login_url='login')
def record_attendance_view(request, cell_group_id):
    """Record attendance for a cell-group meeting."""
    cell_group = get_object_or_404(CellGroup, pk=cell_group_id)
    
    # FIXED: use zone_name comparison
    can_manage = (
        request.user.is_admin() or
        (request.user.is_zone_leader() and request.user.zone_name and cell_group.zone and cell_group.zone.name == request.user.zone_name) or
        (request.user.is_cell_leader() and request.user.assigned_cell_group_id == cell_group.id) or
        (cell_group.leader_id == request.user.id)
    )

    if not can_manage:
        messages.error(request, 'You do not have permission to record attendance for this cell group.')
        return redirect('members:cell_group_detail', pk=cell_group.id)

    members = cell_group.members.filter(member_status=Member.ACTIVE).order_by('last_name', 'first_name')

    if request.method == 'POST':
        meeting_date = request.POST.get('meeting_date')
        if not meeting_date:
            messages.error(request, 'Please select a meeting date.')
            return redirect('members:record_attendance', cell_group_id=cell_group.id)

        parsed_date = datetime.strptime(meeting_date, '%Y-%m-%d').date()
        for member in members:
            status = request.POST.get(f'status_{member.id}')
            if status in ['present', 'absent']:
                AttendanceRecord.objects.update_or_create(
                    member=member,
                    cell_group=cell_group,
                    meeting_date=parsed_date,
                    defaults={'status': status, 'notes': request.POST.get(f'notes_{member.id}', '')}
                )

        messages.success(request, f'Attendance recorded for {cell_group.name}.')
        return redirect('members:cell_group_detail', pk=cell_group.id)

    context = {
        'cell_group': cell_group,
        'members': members,
        'default_date': timezone.now().date().isoformat(),
    }
    return render(request, 'members/attendance_record.html', context)


@login_required(login_url='login')
def cell_group_create_view(request):
    """Create a new cell group."""
    if not request.user.is_zone_leader():
        messages.error(request, 'Only zone leaders can create cell groups.')
        return redirect('members:member_list')
    
    if request.method == 'POST':
        form = CellGroupForm(request.POST, user=request.user)
        if form.is_valid():
            cell_group = form.save(commit=False)
            if request.user.is_zone_leader() and request.user.zone_name:
                from apps.zones.models import Zone as ZonesAppZone
                try:
                    zone = ZonesAppZone.objects.get(name=request.user.zone_name)
                    cell_group.zone = zone
                except ZonesAppZone.DoesNotExist:
                    pass
            cell_group.approval_status = 'pending'
            cell_group.save()
            
            log_activity(
                user=request.user,
                action='create',
                entity_type='cell_group',
                description=f'Created cell group: {cell_group.name}',
                entity_id=cell_group.id,
                request=request
            )
            
            if cell_group.approval_status == 'pending':
                messages.success(request, f'Cell group {cell_group.name} submitted for approval.')
            else:
                messages.success(request, f'Cell group {cell_group.name} created successfully!')
            return redirect('members:cell_group_detail', pk=cell_group.id)
    else:
        form = CellGroupForm(user=request.user)
    
    context = {'form': form}
    return render(request, 'members/cell_group_form.html', context)


@login_required(login_url='login')
def cell_group_approve_view(request, pk):
    """Approve a pending cell-group creation request."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'You do not have permission to approve cell groups.')
        return redirect('members:member_list')

    cell_group = get_object_or_404(CellGroup, pk=pk)
    
    # FIXED: use zone.name == zone_name
    if request.user.is_zone_leader() and not request.user.is_admin() and (not cell_group.zone or cell_group.zone.name != request.user.zone_name):
        messages.error(request, 'You do not have permission to approve this cell group.')
        return redirect('members:cell_group_list')
        
    cell_group.approval_status = 'approved'
    cell_group.save()

    log_activity(
        user=request.user,
        action='approve',
        entity_type='cell_group',
        description=f'Approved cell group: {cell_group.name}',
        entity_id=cell_group.id,
        request=request
    )
    messages.success(request, f'Cell group {cell_group.name} approved successfully.')
    return redirect('members:cell_group_list')


@login_required(login_url='login')
def cell_group_reject_view(request, pk):
    """Reject a pending cell-group creation request."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'You do not have permission to reject cell groups.')
        return redirect('members:member_list')

    cell_group = get_object_or_404(CellGroup, pk=pk)
    
    # FIXED: use zone.name == zone_name
    if request.user.is_zone_leader() and not request.user.is_admin() and (not cell_group.zone or cell_group.zone.name != request.user.zone_name):
        messages.error(request, 'You do not have permission to reject this cell group.')
        return redirect('members:cell_group_list')
        
    cell_group.approval_status = 'rejected'
    cell_group.save()

    log_activity(
        user=request.user,
        action='reject',
        entity_type='cell_group',
        description=f'Rejected cell group: {cell_group.name}',
        entity_id=cell_group.id,
        request=request
    )
    messages.success(request, f'Cell group {cell_group.name} rejected.')
    return redirect('members:cell_group_list')


@login_required(login_url='login')
def cell_group_edit_view(request, pk):
    """Edit cell group."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'Only administrators and zone leaders can edit cell groups.')
        return redirect('members:member_list')
    
    cell_group = get_object_or_404(CellGroup, pk=pk)
    
    # FIXED: use zone.name == zone_name
    if request.user.is_zone_leader() and not request.user.is_admin() and (not cell_group.zone or cell_group.zone.name != request.user.zone_name):
        messages.error(request, 'You do not have permission to edit this cell group.')
        return redirect('members:cell_group_list')
    
    if request.method == 'POST':
        form = CellGroupForm(request.POST, instance=cell_group, user=request.user)
        if form.is_valid():
            cell_group = form.save(commit=False)
            if cell_group.zone:
                cell_group.zone_name = cell_group.zone.name
            else:
                cell_group.zone_name = ''
            cell_group.save()
            
            log_activity(
                user=request.user,
                action='edit',
                entity_type='cell_group',
                description=f'Edited cell group: {cell_group.name}',
                entity_id=cell_group.id,
                request=request
            )
            
            messages.success(request, 'Cell group updated successfully!')
            return redirect('members:cell_group_detail', pk=cell_group.id)
    else:
        form = CellGroupForm(instance=cell_group, user=request.user)
    
    context = {'form': form, 'cell_group': cell_group}
    return render(request, 'members/cell_group_form.html', context)



@login_required(login_url='login')
def member_transfer_view(request, pk):
    """Transfer a member to a different cell group."""
    member = get_object_or_404(Member, pk=pk)
    old_cell_group = member.cell_group
    
    # Check permissions (reuse your existing permission logic)
    if not can_manage_member(request.user, member):
        messages.error(request, 'You do not have permission to transfer this member.')
        return redirect('members:member_detail', pk=member.id)
    
    if request.method == 'POST':
        # Pass user and current cell group to the form to filter the dropdown
        form = MemberTransferForm(request.POST, user=request.user, current_cell_group=old_cell_group)
        if form.is_valid():
            new_cell_group = form.cleaned_data['target_cell_group']
            reason = form.cleaned_data.get('transfer_reason', '')
            
            # Update the member
            member.cell_group = new_cell_group
            member.save()
            
            # Log the activity
            old_group_name = old_cell_group.name if old_cell_group else "None"
            log_activity(
                user=request.user,
                action='transfer',
                entity_type='member',
                description=f'Transferred {member.get_full_name()} from "{old_group_name}" to "{new_cell_group.name}". Reason: {reason}',
                entity_id=member.id,
                request=request
            )
            
            messages.success(request, f'{member.get_full_name()} successfully transferred to {new_cell_group.name}.')
            return redirect('members:member_detail', pk=member.id)
    else:
        form = MemberTransferForm(user=request.user, current_cell_group=old_cell_group)
    
    context = {
        'form': form,
        'member': member,
        'old_cell_group': old_cell_group,
    }
    return render(request, 'members/member_transfer.html', context)