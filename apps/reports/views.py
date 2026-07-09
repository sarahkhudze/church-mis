# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse, FileResponse
# from django.contrib import messages
# from datetime import date
# import csv
# import io
# from collections import defaultdict

# # Correct reportlab imports
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
# # Fix: Remove the enum import and use alignment constants directly
# from reportlab.lib.enums import TA_CENTER, TA_LEFT

# import openpyxl
# from openpyxl.styles import Font, PatternFill, Alignment
# from openpyxl.utils import get_column_letter

# from apps.members.models import Member, AttendanceRecord  # Added AttendanceRecord
# from apps.cell_groups.models import CellGroup  # Fixed: Added import from correct location
# from apps.accounts.models import CustomUser
# from apps.accounts.utils import log_activity, admin_required, get_user_members

# @login_required(login_url='login')
# def reports_view(request):
#     """Reports menu view."""
#     context = {
#         'is_admin': request.user.is_admin(),
#         'is_cell_leader': request.user.is_cell_leader(),
#         'is_zone_leader': request.user.is_zone_leader(),
#     }
#     return render(request, 'reports/reports_menu.html', context)


# @login_required(login_url='login')
# def member_report_view(request):
#     """Generate member report."""
#     members = get_user_members(request.user)
    
#     # Filter by zone or cell group for leaders
#     if request.user.is_zone_leader() and request.user.zone_name:
#         members = members.filter(cell_group__zone_name=request.user.zone_name)
#     elif request.user.is_cell_leader():
#         members = members.filter(cell_group=request.user.assigned_cell_group)
    
#     # Filter by baptized status if provided
#     baptized = request.GET.get('baptized', '')
#     if baptized:
#         members = members.filter(is_baptized=baptized == 'yes')
    
#     # Filter by married status if provided
#     married = request.GET.get('married', '')
#     if married:
#         members = members.filter(is_married=married == 'yes')
    
#     # Filter by gender if provided
#     gender = request.GET.get('gender', '')
#     if gender:
#         members = members.filter(gender=gender)
    
#     # Filter by cell group if admin
#     if request.user.is_admin():
#         cell_group = request.GET.get('cell_group', '')
#         if cell_group:
#             members = members.filter(cell_group_id=cell_group)
    
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_member_pdf(members, request.user)
#     elif format_type == 'excel':
#         return generate_member_excel(members, request.user)
#     elif format_type == 'csv':
#         return generate_member_csv(members, request.user)
    
#     cell_groups = CellGroup.objects.filter(is_active=True) if request.user.is_admin() else []
    
#     context = {
#         'members': members,
#         'cell_groups': cell_groups,
#         'is_admin': request.user.is_admin(),
#     }
    
#     return render(request, 'reports/member_report.html', context)


# @login_required(login_url='login')
# def cell_group_report_view(request):
#     """Generate cell group report."""
#     if request.user.is_zone_leader() and request.user.zone_name:
#         cell_groups = CellGroup.objects.filter(is_active=True, zone_name=request.user.zone_name)
#     elif request.user.is_cell_leader():
#         cell_groups = CellGroup.objects.filter(id=request.user.assigned_cell_group.id)
#     else:
#         cell_groups = CellGroup.objects.filter(is_active=True)
    
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_cell_group_pdf(cell_groups, request.user)
#     elif format_type == 'excel':
#         return generate_cell_group_excel(cell_groups, request.user)
#     elif format_type == 'csv':
#         return generate_cell_group_csv(cell_groups, request.user)
    
#     context = {'cell_groups': cell_groups}
#     return render(request, 'reports/cell_group_report.html', context)


# @login_required(login_url='login')
# def baptism_report_view(request):
#     """Generate baptism report."""
#     members = get_user_members(request.user).filter(is_baptized=True)
    
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_baptism_pdf(members, request.user)
#     elif format_type == 'excel':
#         return generate_baptism_excel(members, request.user)
#     elif format_type == 'csv':
#         return generate_baptism_csv(members, request.user)
    
#     context = {'members': members}
#     return render(request, 'reports/baptism_report.html', context)


# @login_required(login_url='login')
# def marriage_report_view(request):
#     """Generate marriage report."""
#     members = get_user_members(request.user).filter(is_married=True)
    
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_marriage_pdf(members, request.user)
#     elif format_type == 'excel':
#         return generate_marriage_excel(members, request.user)
#     elif format_type == 'csv':
#         return generate_marriage_csv(members, request.user)
    
#     context = {'members': members}
#     return render(request, 'reports/marriage_report.html', context)


# # ... (previous imports and other functions remain unchanged) ...

# @login_required(login_url='login')
# def attendance_report_view(request, cell_group_id):
#     """Generate attendance report for a specific cell group."""
#     cell_group = get_object_or_404(CellGroup, id=cell_group_id)
    
#     # Permission check: Only allow access if user is admin, the cell group leader, or the zone leader of the cell group's zone
#     if not (
#         request.user.is_admin() or
#         (request.user.is_cell_leader() and request.user.assigned_cell_group == cell_group) or
#         (request.user.is_zone_leader() and request.user.zone_name == cell_group.zone_name)
#     ):
#         messages.error(request, 'You do not have permission to view this attendance report.')
#         return redirect('dashboard:dashboard') # Redirect to dashboard or appropriate page

#     # Get all attendance records for the cell group, ordered by meeting date
#     attendance_records = AttendanceRecord.objects.filter(
#         cell_group=cell_group
#     ).order_by('meeting_date')

#     # Get all unique meeting dates
#     meeting_dates = sorted(set(record.meeting_date for record in attendance_records))

#     # Get all members in the cell group who were active at the time of the meeting
#     # For the report, we'll consider all currently active members in the group
#     all_group_members = Member.objects.filter(cell_group=cell_group, member_status=Member.ACTIVE).order_by('last_name', 'first_name')

#     # Prepare attendance summary data: {member_instance: {date: 'present'/'absent'}}
#     attendance_summary = defaultdict(dict)
#     for record in attendance_records:
#         attendance_summary[record.member][record.meeting_date] = record.status

#     # Calculate overall percentage for each member
#     for member, date_statuses in attendance_summary.items():
#         present_count = sum(1 for status in date_statuses.values() if status == 'present')
#         total_meetings = len(date_statuses)
#         if total_meetings > 0:
#             attendance_summary[member]['overall_percentage'] = (present_count / total_meetings) * 100
#         else:
#             attendance_summary[member]['overall_percentage'] = 0.0

#     # *** NEW LOGIC: Prepare table data for the template ***
#     table_data = []
#     for member in all_group_members:
#         member_row = {
#             'member': member,
#             'statuses': [], # List of statuses aligned with meeting_dates
#             'overall_percentage': attendance_summary.get(member, {}).get('overall_percentage', 0.0)
#         }
        
#         # Align statuses with meeting_dates
#         for date in meeting_dates:
#             status = attendance_summary.get(member, {}).get(date, 'N/A') # Default to 'N/A' if no record for this date
#             member_row['statuses'].append(status)
        
#         table_data.append(member_row)

#     # Calculate summary by date
#     attendance_by_date = {}
#     for date in meeting_dates:
#         records_on_date = [r for r in attendance_records if r.meeting_date == date]
#         present_count = sum(1 for r in records_on_date if r.status == 'present')
#         absent_count = sum(1 for r in records_on_date if r.status == 'absent')
#         total = present_count + absent_count
#         rate = (present_count / total * 100) if total > 0 else 0.0
#         attendance_by_date[date] = {
#             'present': present_count,
#             'absent': absent_count,
#             'rate': rate,
#             'notes': ', '.join(set(r.notes for r in records_on_date if r.notes)) # Example: combine notes
#         }

#     # Calculate overall summary statistics
#     total_meetings = len(meeting_dates)
#     total_attendance_records = len(attendance_records)
#     total_present = sum(1 for r in attendance_records if r.status == 'present')
#     total_absent = sum(1 for r in attendance_records if r.status == 'absent')
#     average_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0.0

#     # Handle export formats
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_attendance_pdf(attendance_records, cell_group, request.user)
#     elif format_type == 'excel':
#         return generate_attendance_excel(attendance_records, cell_group, request.user)
#     elif format_type == 'csv':
#         return generate_attendance_csv(attendance_records, cell_group, request.user)

#     context = {
#         'cell_group': cell_group,
#         'attendance_records': attendance_records,
#         'meeting_dates': meeting_dates,
#         'all_group_members': all_group_members,
#         'table_data': table_data, # Pass the pre-formatted data
#         # 'attendance_summary': dict(attendance_summary), # Comment out or remove if no longer needed elsewhere in the template
#         'attendance_by_date': attendance_by_date,
#         'total_meetings': total_meetings,
#         'total_present': total_present,
#         'total_absent': total_absent,
#         'average_attendance_rate': average_attendance_rate,
#     }
    
#     return render(request, 'reports/attendance_report.html', context)

# # @login_required(login_url='login')
# # def attendance_report_view(request, cell_group_id):
# #     """Generate attendance report for a specific cell group."""
# #     cell_group = get_object_or_404(CellGroup, id=cell_group_id)
    
# #     # Permission check: Only allow access if user is admin, the cell group leader, or the zone leader of the cell group's zone
# #     if not (
# #         request.user.is_admin() or
# #         (request.user.is_cell_leader() and request.user.assigned_cell_group == cell_group) or
# #         (request.user.is_zone_leader() and request.user.zone_name == cell_group.zone_name)
# #     ):
# #         messages.error(request, 'You do not have permission to view this attendance report.')
# #         return redirect('dashboard:dashboard') # Redirect to dashboard or appropriate page

# #     # Get all attendance records for the cell group, ordered by meeting date
# #     attendance_records = AttendanceRecord.objects.filter(
# #         cell_group=cell_group
# #     ).order_by('meeting_date')

# #     # Get all unique meeting dates
# #     meeting_dates = sorted(set(record.meeting_date for record in attendance_records))

# #     # Get all members in the cell group who were active at the time of the meeting
# #     # Note: This is a simplified approach. You might need to adjust based on how you track membership over time.
# #     # For now, we'll get all members who have ever been in this cell group and are currently active.
# #     all_group_members = Member.objects.filter(cell_group=cell_group, member_status=Member.ACTIVE).order_by('last_name', 'first_name')

# #     # Prepare attendance summary data: {member_instance: {date: 'present'/'absent'}}
# #     attendance_summary = defaultdict(dict)
# #     for record in attendance_records:
# #         attendance_summary[record.member][record.meeting_date] = record.status

# #     # Calculate overall percentage for each member
# #     for member, date_statuses in attendance_summary.items():
# #         present_count = sum(1 for status in date_statuses.values() if status == 'present')
# #         total_meetings = len(date_statuses)
# #         if total_meetings > 0:
# #             attendance_summary[member]['overall_percentage'] = (present_count / total_meetings) * 100
# #         else:
# #             attendance_summary[member]['overall_percentage'] = 0.0

# #     # Calculate summary by date
# #     attendance_by_date = {}
# #     for date in meeting_dates:
# #         records_on_date = [r for r in attendance_records if r.meeting_date == date]
# #         present_count = sum(1 for r in records_on_date if r.status == 'present')
# #         absent_count = sum(1 for r in records_on_date if r.status == 'absent')
# #         total = present_count + absent_count
# #         rate = (present_count / total * 100) if total > 0 else 0.0
# #         attendance_by_date[date] = {
# #             'present': present_count,
# #             'absent': absent_count,
# #             'rate': rate,
# #             'notes': ', '.join(set(r.notes for r in records_on_date if r.notes)) # Example: combine notes
# #         }

# #     # Calculate overall summary statistics
# #     total_meetings = len(meeting_dates)
# #     total_attendance_records = len(attendance_records)
# #     total_present = sum(1 for r in attendance_records if r.status == 'present')
# #     total_absent = sum(1 for r in attendance_records if r.status == 'absent')
# #     average_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0.0

# #     # Handle export formats
# #     format_type = request.GET.get('format', 'html')
    
# #     if format_type == 'pdf':
# #         return generate_attendance_pdf(attendance_records, cell_group, request.user)
# #     elif format_type == 'excel':
# #         return generate_attendance_excel(attendance_records, cell_group, request.user)
# #     elif format_type == 'csv':
# #         return generate_attendance_csv(attendance_records, cell_group, request.user)

# #     context = {
# #         'cell_group': cell_group,
# #         'attendance_records': attendance_records,
# #         'meeting_dates': meeting_dates,
# #         'all_group_members': all_group_members,
# #         'attendance_summary': dict(attendance_summary), # Convert defaultdict to regular dict for template
# #         'attendance_by_date': attendance_by_date,
# #         'total_meetings': total_meetings,
# #         'total_present': total_present,
# #         'total_absent': total_absent,
# #         'average_attendance_rate': average_attendance_rate,
# #     }
    
# #     return render(request, 'reports/attendance_report.html', context)


# # PDF Generation Functions

# def generate_member_pdf(members, user):
#     """Generate member list PDF."""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
#     elements = []
    
#     # Title
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=18,
#         textColor=colors.HexColor('#1f4788'),
#         spaceAfter=6,
#         alignment=TA_CENTER  # Now this works with correct import
#     )
#     elements.append(Paragraph('CHURCH MEMBER REPORT', title_style))
#     elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
#     elements.append(Spacer(1, 0.3*inch))
    
#     # Table data
#     data = [[
#         'Name', 'Phone', 'Email', 'Cell Group', 
#         'Baptized', 'Married', 'Date Joined'
#     ]]
    
#     for member in members:
#         # Handle potential missing fields
#         full_name = f"{member.first_name} {member.last_name}" if hasattr(member, 'first_name') else str(member)
#         phone = getattr(member, 'phone_number', 'N/A')
#         email = getattr(member, 'email', 'N/A')
#         cell_group = member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else 'N/A'
#         is_baptized = 'Yes' if getattr(member, 'is_baptized', False) else 'No'
#         is_married = 'Yes' if getattr(member, 'is_married', False) else 'No'
#         date_joined = member.date_joined_church.strftime('%m/%d/%Y') if hasattr(member, 'date_joined_church') and member.date_joined_church else 'N/A'
        
#         data.append([
#             full_name, phone, email, cell_group, 
#             is_baptized, is_married, date_joined
#         ])
    
#     # Create table
#     table = Table(data, colWidths=[1.8*inch, 1*inch, 1.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.9*inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 10),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('FONTSIZE', (0, 1), (-1, -1), 9),
#         ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
#     ]))
    
#     elements.append(table)
#     doc.build(elements)
    
#     buffer.seek(0)
#     log_activity(user, 'export', 'member', 'Exported members to PDF')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'member_report_{date.today()}.pdf',
#         content_type='application/pdf'
#     )


# def generate_member_excel(members, user):
#     """Generate member list Excel file."""
#     workbook = openpyxl.Workbook()
#     worksheet = workbook.active
#     worksheet.title = 'Members'
    
#     # Headers
#     headers = [
#         'First Name', 'Last Name', 'Date of Birth', 'Gender',
#         'Phone', 'Email', 'Cell Group', 'Date Joined',
#         'Baptized', 'Baptism Cert', 'Married', 'Spouse Name'
#     ]
    
#     worksheet.append(headers)
    
#     # Style header row
#     header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
#     header_font = Font(bold=True, color='FFFFFF')
    
#     for cell in worksheet[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal='center', vertical='center')
    
#     # Add data
#     for member in members:
#         worksheet.append([
#             member.first_name,
#             member.last_name,
#             member.date_of_birth if hasattr(member, 'date_of_birth') else '',
#             member.get_gender_display() if hasattr(member, 'get_gender_display') else member.gender,
#             member.phone_number,
#             member.email,
#             member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else '',
#             member.date_joined_church if hasattr(member, 'date_joined_church') else '',
#             'Yes' if member.is_baptized else 'No',
#             member.baptism_certificate_number or '',
#             'Yes' if member.is_married else 'No',
#             member.spouse_name or '',
#         ])
    
#     # Adjust column widths
#     for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
#         worksheet.column_dimensions[col].width = 15
    
#     buffer = io.BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'member', 'Exported members to Excel')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'member_report_{date.today()}.xlsx',
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )


# def generate_member_csv(members, user):
#     """Generate member list CSV file."""
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="member_report_{date.today()}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow([
#         'First Name', 'Last Name', 'Date of Birth', 'Gender',
#         'Phone', 'Email', 'Cell Group', 'Date Joined',
#         'Baptized', 'Baptism Cert', 'Married', 'Spouse Name'
#     ])
    
#     for member in members:
#         writer.writerow([
#             member.first_name,
#             member.last_name,
#             member.date_of_birth if hasattr(member, 'date_of_birth') else '',
#             member.get_gender_display() if hasattr(member, 'get_gender_display') else member.gender,
#             member.phone_number,
#             member.email,
#             member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else '',
#             member.date_joined_church if hasattr(member, 'date_joined_church') else '',
#             'Yes' if member.is_baptized else 'No',
#             member.baptism_certificate_number or '',
#             'Yes' if member.is_married else 'No',
#             member.spouse_name or '',
#         ])
    
#     log_activity(user, 'export', 'member', 'Exported members to CSV')
#     return response


# # Cell Group Report Functions

# def generate_cell_group_pdf(cell_groups, user):
#     """Generate cell group PDF report"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         textColor=colors.HexColor('#1f4788'),
#         alignment=TA_CENTER
#     )
    
#     elements.append(Paragraph('CELL GROUP REPORT', title_style))
#     elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
#     elements.append(Spacer(1, 0.3*inch))
    
#     data = [['Cell Group', 'Location', 'Leader', 'Member Count']]
    
#     for group in cell_groups:
#         data.append([
#             group.name,
#             group.location,
#             group.leader.get_full_name() if group.leader else 'N/A',
#             str(group.member_count),
#         ])
    
#     table = Table(data)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
    
#     elements.append(table)
#     doc.build(elements)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'cell_group', 'Exported cell groups to PDF')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'cell_group_report_{date.today()}.pdf',
#         content_type='application/pdf'
#     )


# def generate_cell_group_excel(cell_groups, user):
#     workbook = openpyxl.Workbook()
#     worksheet = workbook.active
#     worksheet.title = 'Cell Groups'
    
#     headers = ['Cell Group', 'Location', 'Leader', 'Member Count']
#     worksheet.append(headers)
    
#     # Style header
#     header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
#     header_font = Font(bold=True, color='FFFFFF')
    
#     for cell in worksheet[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal='center')
    
#     for group in cell_groups:
#         worksheet.append([
#             group.name,
#             group.location,
#             group.leader.get_full_name() if group.leader else 'N/A',
#             group.member_count,
#         ])
    
#     # Adjust column widths
#     worksheet.column_dimensions['A'].width = 20
#     worksheet.column_dimensions['B'].width = 20
#     worksheet.column_dimensions['C'].width = 20
#     worksheet.column_dimensions['D'].width = 15
    
#     buffer = io.BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'cell_group', 'Exported cell groups to Excel')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'cell_group_report_{date.today()}.xlsx',
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )


# def generate_cell_group_csv(cell_groups, user):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="cell_group_report_{date.today()}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Cell Group', 'Location', 'Leader', 'Member Count'])
    
#     for group in cell_groups:
#         writer.writerow([
#             group.name,
#             group.location,
#             group.leader.get_full_name() if group.leader else 'N/A',
#             group.member_count
#         ])
    
#     log_activity(user, 'export', 'cell_group', 'Exported cell groups to CSV')
#     return response


# # Baptism Report Functions

# def generate_baptism_pdf(members, user):
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         textColor=colors.HexColor('#1f4788'),
#         alignment=TA_CENTER
#     )
    
#     elements.append(Paragraph('BAPTISM REPORT', title_style))
#     elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
#     elements.append(Spacer(1, 0.3*inch))
    
#     data = [['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number']]
    
#     for member in members:
#         data.append([
#             f"{member.first_name} {member.last_name}",
#             member.phone_number,
#             member.email,
#             str(member.baptism_date) if hasattr(member, 'baptism_date') and member.baptism_date else 'N/A',
#             member.baptism_certificate_number or 'N/A',
#         ])
    
#     table = Table(data)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
    
#     elements.append(table)
#     doc.build(elements)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'baptism', 'Exported baptism report to PDF')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'baptism_report_{date.today()}.pdf',
#         content_type='application/pdf'
#     )


# def generate_baptism_excel(members, user):
#     workbook = openpyxl.Workbook()
#     worksheet = workbook.active
#     worksheet.title = 'Baptized Members'
    
#     headers = ['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number']
#     worksheet.append(headers)
    
#     header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
#     header_font = Font(bold=True, color='FFFFFF')
    
#     for cell in worksheet[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal='center')
    
#     for member in members:
#         worksheet.append([
#             f"{member.first_name} {member.last_name}",
#             member.phone_number,
#             member.email,
#             member.baptism_date if hasattr(member, 'baptism_date') else '',
#             member.baptism_certificate_number or '',
#         ])
    
#     buffer = io.BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'baptism', 'Exported baptism report to Excel')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'baptism_report_{date.today()}.xlsx',
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )


# def generate_baptism_csv(members, user):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="baptism_report_{date.today()}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number'])
    
#     for member in members:
#         writer.writerow([
#             f"{member.first_name} {member.last_name}",
#             member.phone_number,
#             member.email,
#             member.baptism_date if hasattr(member, 'baptism_date') else '',
#             member.baptism_certificate_number or '',
#         ])
    
#     log_activity(user, 'export', 'baptism', 'Exported baptism report to CSV')
#     return response


# # Marriage Report Functions

# def generate_marriage_pdf(members, user):
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         textColor=colors.HexColor('#1f4788'),
#         alignment=TA_CENTER
#     )
    
#     elements.append(Paragraph('MARRIAGE REPORT', title_style))
#     elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
#     elements.append(Spacer(1, 0.3*inch))
    
#     data = [['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number']]
    
#     for member in members:
#         data.append([
#             f"{member.first_name} {member.last_name}",
#             member.spouse_name or 'N/A',
#             member.phone_number,
#             str(member.marriage_date) if hasattr(member, 'marriage_date') and member.marriage_date else 'N/A',
#             member.marriage_certificate_number or 'N/A',
#         ])
    
#     table = Table(data)
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
    
#     elements.append(table)
#     doc.build(elements)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'marriage', 'Exported marriage report to PDF')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'marriage_report_{date.today()}.pdf',
#         content_type='application/pdf'
#     )


# def generate_marriage_excel(members, user):
#     workbook = openpyxl.Workbook()
#     worksheet = workbook.active
#     worksheet.title = 'Married Members'
    
#     headers = ['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number']
#     worksheet.append(headers)
    
#     header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
#     header_font = Font(bold=True, color='FFFFFF')
    
#     for cell in worksheet[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal='center')
    
#     for member in members:
#         worksheet.append([
#             f"{member.first_name} {member.last_name}",
#             member.spouse_name or '',
#             member.phone_number,
#             member.marriage_date if hasattr(member, 'marriage_date') else '',
#             member.marriage_certificate_number or '',
#         ])
    
#     buffer = io.BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'marriage', 'Exported marriage report to Excel')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'marriage_report_{date.today()}.xlsx',
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )


# def generate_marriage_csv(members, user):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="marriage_report_{date.today()}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number'])
    
#     for member in members:
#         writer.writerow([
#             f"{member.first_name} {member.last_name}",
#             member.spouse_name or '',
#             member.phone_number,
#             member.marriage_date if hasattr(member, 'marriage_date') else '',
#             member.marriage_certificate_number or '',
#         ])
    
#     log_activity(user, 'export', 'marriage', 'Exported marriage report to CSV')
#     return response


# # Attendance Report Functions
# def generate_attendance_pdf(attendance_records, cell_group, user):
#     """Generate attendance PDF report"""
#     buffer = io.BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     elements = []
    
#     styles = getSampleStyleSheet()
#     title_style = ParagraphStyle(
#         'CustomTitle',
#         parent=styles['Heading1'],
#         fontSize=16,
#         textColor=colors.HexColor('#1f4788'),
#         alignment=TA_CENTER
#     )
    
#     elements.append(Paragraph(f'ATTENDANCE REPORT - {cell_group.name}', title_style))
#     elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
#     elements.append(Spacer(1, 0.3*inch))
    
#     # Summary table
#     summary_data = [['Total Meetings', 'Total Records', 'Total Present', 'Total Absent', 'Avg. Rate (%)']]
#     total_meetings = attendance_records.values('meeting_date').distinct().count()
#     total_records = attendance_records.count()
#     total_present = attendance_records.filter(status='present').count()
#     total_absent = attendance_records.filter(status='absent').count()
#     avg_rate = (total_present / total_records * 100) if total_records > 0 else 0.0
    
#     summary_data.append([
#         str(total_meetings),
#         str(total_records),
#         str(total_present),
#         str(total_absent),
#         f"{avg_rate:.2f}"
#     ])
    
#     summary_table = Table(summary_data)
#     summary_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#     elements.append(summary_table)
#     elements.append(Spacer(1, 0.2*inch))

#     # Detailed attendance table
#     data = [['Date', 'Member', 'Status', 'Notes']]
#     for record in attendance_records:
#         data.append([
#             record.meeting_date.strftime('%Y-%m-%d'),
#             f"{record.member.first_name} {record.member.last_name}",
#             record.get_status_display(),  # Assuming you have a get_status_display method
#             record.notes or ''
#         ])
    
#     detailed_table = Table(data)
#     detailed_table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
#     elements.append(detailed_table)
    
#     doc.build(elements)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'attendance', f'Exported attendance report for {cell_group.name} to PDF')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'attendance_report_{cell_group.name}_{date.today()}.pdf',
#         content_type='application/pdf'
#     )


# def generate_attendance_excel(attendance_records, cell_group, user):
#     """Generate attendance Excel report"""
#     workbook = openpyxl.Workbook()
#     worksheet = workbook.active
#     worksheet.title = f'Attendance - {cell_group.name}'
    
#     headers = ['Date', 'Member', 'Status', 'Notes']
#     worksheet.append(headers)
    
#     # Style header
#     header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
#     header_font = Font(bold=True, color='FFFFFF')
    
#     for cell in worksheet[1]:
#         cell.fill = header_fill
#         cell.font = header_font
#         cell.alignment = Alignment(horizontal='center')
    
#     for record in attendance_records:
#         worksheet.append([
#             record.meeting_date,
#             f"{record.member.first_name} {record.member.last_name}",
#             record.get_status_display(),  # Assuming you have a get_status_display method
#             record.notes or ''
#         ])
    
#     # Adjust column widths
#     worksheet.column_dimensions['A'].width = 15
#     worksheet.column_dimensions['B'].width = 25
#     worksheet.column_dimensions['C'].width = 12
#     worksheet.column_dimensions['D'].width = 30
    
#     buffer = io.BytesIO()
#     workbook.save(buffer)
#     buffer.seek(0)
    
#     log_activity(user, 'export', 'attendance', f'Exported attendance report for {cell_group.name} to Excel')
    
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'attendance_report_{cell_group.name}_{date.today()}.xlsx',
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )


# def generate_attendance_csv(attendance_records, cell_group, user):
#     """Generate attendance CSV report"""
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="attendance_report_{cell_group.name}_{date.today()}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Date', 'Member', 'Status', 'Notes'])
    
#     for record in attendance_records:
#         writer.writerow([
#             record.meeting_date,
#             f"{record.member.first_name} {record.member.last_name}",
#             record.get_status_display(),  # Assuming you have a get_status_display method
#             record.notes or ''
#         ])
    
#     log_activity(user, 'export', 'attendance', f'Exported attendance report for {cell_group.name} to CSV')
#     return response


# @login_required(login_url='login')
# def zone_report_view(request):
#     """Generate a zone-level report for zone leaders."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'Only zone leaders and administrators can access zone reports.')
#         return redirect('reports:reports')

#     if request.user.is_zone_leader() and request.user.zone_name:
#         cell_groups = CellGroup.objects.filter(is_active=True, zone_name=request.user.zone_name)
#         members = Member.objects.filter(cell_group__in=cell_groups)
#         zone_name = request.user.zone_name
#     else:
#         cell_groups = CellGroup.objects.filter(is_active=True)
#         members = Member.objects.active()
#         zone_name = 'All Zones'

#     context = {
#         'zone_name': zone_name,
#         'cell_groups': cell_groups,
#         'members': members,
#         'active_members': members.filter(member_status=Member.ACTIVE).count(),
#         'inactive_members': members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count(),
#         'follow_up_required': members.filter(
#             member_status=Member.ACTIVE,
#             phone_number__in=['', None],
#         ).count(),
#     }
#     return render(request, 'reports/zone_report.html', context)


# @login_required(login_url='login')
# def growth_report_view(request):
#     """Generate growth report."""
#     if not (request.user.is_admin() or request.user.is_zone_leader()):
#         messages.error(request, 'Only administrators and zone leaders can access growth reports.')
#         return redirect('reports:reports')
    
#     # Get last 12 months of data
#     from datetime import datetime, timedelta
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=365)
    
#     monthly_growth = []
#     current_date = start_date
    
#     from apps.members.models import Member
#     members = Member.objects.active()
#     if request.user.is_zone_leader() and request.user.zone_name:
#         members = members.filter(cell_group__zone_name=request.user.zone_name)
    
#     while current_date <= end_date:
#         month_start = current_date.replace(day=1)
#         if current_date.month == 12:
#             next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
#         else:
#             next_month = current_date.replace(month=current_date.month + 1, day=1)
        
#         new_members = members.filter(
#             date_joined_church__gte=month_start,
#             date_joined_church__lt=next_month
#         ).count()
        
#         monthly_growth.append({
#             'month': month_start.strftime('%B %Y'),
#             'new_members': new_members,
#         })
        
#         current_date = next_month
    
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'excel':
#         # Create Excel export
#         import openpyxl
#         from django.http import FileResponse
#         import io
        
#         workbook = openpyxl.Workbook()
#         worksheet = workbook.active
#         worksheet.title = 'Growth Report'
        
#         worksheet.append(['Month', 'New Members'])
#         for data in monthly_growth:
#             worksheet.append([data['month'], data['new_members']])
        
#         buffer = io.BytesIO()
#         workbook.save(buffer)
#         buffer.seek(0)
        
#         return FileResponse(
#             buffer,
#             as_attachment=True,
#             filename='growth_report.xlsx',
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
    
#     elif format_type == 'csv':
#         import csv
#         from django.http import HttpResponse
        
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="growth_report.csv"'
        
#         writer = csv.writer(response)
#         writer.writerow(['Month', 'New Members'])
#         for data in monthly_growth:
#             writer.writerow([data['month'], data['new_members']])
        
#         return response
    
#     context = {
#         'monthly_growth': monthly_growth,
#         'total_new_members': sum(item['new_members'] for item in monthly_growth),
#     }
    
#     return render(request, 'reports/growth_report.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from datetime import date, datetime
import csv
import io
from collections import defaultdict

# Correct reportlab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
# Fix: Remove the enum import and use alignment constants directly
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

from apps.members.models import Member, AttendanceRecord  # Added AttendanceRecord
from apps.cell_groups.models import CellGroup  # Fixed: Added import from correct location
from apps.accounts.models import CustomUser
from apps.accounts.utils import log_activity, admin_required, get_user_members

@login_required(login_url='login')
def reports_view(request):
    """Reports menu view."""
    context = {
        'is_admin': request.user.is_admin(),
        'is_cell_leader': request.user.is_cell_leader(),
        'is_zone_leader': request.user.is_zone_leader(),
    }
    return render(request, 'reports/reports_menu.html', context)


@login_required(login_url='login')
def member_report_view(request):
    """Generate member report."""
    members = get_user_members(request.user)
    
    # Filter by zone or cell group for leaders
    if request.user.is_zone_leader() and request.user.zone_name:
        members = members.filter(cell_group__zone_name=request.user.zone_name)
    elif request.user.is_cell_leader():
        members = members.filter(cell_group=request.user.assigned_cell_group)
    
    # Filter by baptized status if provided
    baptized = request.GET.get('baptized', '')
    if baptized:
        members = members.filter(is_baptized=baptized == 'yes')
    
    # Filter by married status if provided
    married = request.GET.get('married', '')
    if married:
        members = members.filter(is_married=married == 'yes')
    
    # Filter by gender if provided
    gender = request.GET.get('gender', '')
    if gender:
        members = members.filter(gender=gender)
    
    # Filter by cell group if admin
    if request.user.is_admin():
        cell_group = request.GET.get('cell_group', '')
        if cell_group:
            members = members.filter(cell_group_id=cell_group)
    
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'pdf':
        return generate_member_pdf(members, request.user)
    elif format_type == 'excel':
        return generate_member_excel(members, request.user)
    elif format_type == 'csv':
        return generate_member_csv(members, request.user)
    
    cell_groups = CellGroup.objects.filter(is_active=True) if request.user.is_admin() else []
    
    context = {
        'members': members,
        'cell_groups': cell_groups,
        'is_admin': request.user.is_admin(),
    }
    
    return render(request, 'reports/member_report.html', context)


@login_required(login_url='login')
def cell_group_report_view(request):
    """Generate cell group report."""
    if request.user.is_zone_leader() and request.user.zone_name:
        cell_groups = CellGroup.objects.filter(is_active=True, zone_name=request.user.zone_name)
    elif request.user.is_cell_leader():
        cell_groups = CellGroup.objects.filter(id=request.user.assigned_cell_group.id)
    else:
        cell_groups = CellGroup.objects.filter(is_active=True)
    
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'pdf':
        return generate_cell_group_pdf(cell_groups, request.user)
    elif format_type == 'excel':
        return generate_cell_group_excel(cell_groups, request.user)
    elif format_type == 'csv':
        return generate_cell_group_csv(cell_groups, request.user)
    
    context = {'cell_groups': cell_groups}
    return render(request, 'reports/cell_group_report.html', context)


@login_required(login_url='login')
def baptism_report_view(request):
    """Generate baptism report."""
    members = get_user_members(request.user).filter(is_baptized=True)
    
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'pdf':
        return generate_baptism_pdf(members, request.user)
    elif format_type == 'excel':
        return generate_baptism_excel(members, request.user)
    elif format_type == 'csv':
        return generate_baptism_csv(members, request.user)
    
    context = {'members': members}
    return render(request, 'reports/baptism_report.html', context)


@login_required(login_url='login')
def marriage_report_view(request):
    """Generate marriage report."""
    members = get_user_members(request.user).filter(is_married=True)
    
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'pdf':
        return generate_marriage_pdf(members, request.user)
    elif format_type == 'excel':
        return generate_marriage_excel(members, request.user)
    elif format_type == 'csv':
        return generate_marriage_csv(members, request.user)
    
    context = {'members': members}
    return render(request, 'reports/marriage_report.html', context)


# ... (previous imports and other functions remain unchanged) ...

@login_required(login_url='login')
def attendance_report_view(request, cell_group_id):
    """Generate attendance report for a specific cell group."""
    cell_group = get_object_or_404(CellGroup, id=cell_group_id)
    
    # Permission check: Only allow access if user is admin, the cell group leader, or the zone leader of the cell group's zone
    if not (
        request.user.is_admin() or
        (request.user.is_cell_leader() and request.user.assigned_cell_group == cell_group) or
        (request.user.is_zone_leader() and request.user.zone_name == cell_group.zone_name)
    ):
        messages.error(request, 'You do not have permission to view this attendance report.')
        return redirect('dashboard:dashboard') # Redirect to dashboard or appropriate page

    # Get all attendance records for the cell group, ordered by meeting date
    attendance_records = AttendanceRecord.objects.filter(
        cell_group=cell_group
    ).order_by('meeting_date')

    # Get all unique meeting dates
    all_meeting_dates = sorted(set(record.meeting_date for record in attendance_records))

    # --- Handle Date Filtering ---
    selected_date_str = request.GET.get('meeting_date', '')
    selected_date = None
    filtered_attendance_records = attendance_records
    
    if selected_date_str:
        try:
            # Parse the date string from the GET parameter
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            # Filter the records to only those from the selected date
            filtered_attendance_records = attendance_records.filter(meeting_date=selected_date)
        except ValueError:
            # Handle invalid date format gracefully
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            # Optionally, reset to show all records if date is invalid
            selected_date_str = ''
            selected_date = None
            filtered_attendance_records = attendance_records

    # Get all members in the cell group who were active at the time of the meeting
    # For the report, we'll consider all currently active members in the group
    all_group_members = Member.objects.filter(cell_group=cell_group, member_status=Member.ACTIVE).order_by('last_name', 'first_name')

    # Prepare attendance summary data: {member_instance: {date: 'present'/'absent'}}
    attendance_summary = defaultdict(dict)
    for record in filtered_attendance_records: # Use filtered records for summary
        attendance_summary[record.member][record.meeting_date] = record.status

    # Calculate overall percentage for each member based on *all* meetings (if not filtering by date)
    # Or calculate percentage based on *filtered* meetings (if filtering by date)
    total_meetings_for_calc = 1 if selected_date else len(all_meeting_dates) # Use 1 if filtered by date, otherwise all dates
    for member, date_statuses in attendance_summary.items():
        present_count = sum(1 for status in date_statuses.values() if status == 'present')
        # total_meetings_for_calc is determined above based on filter
        if total_meetings_for_calc > 0:
            attendance_summary[member]['overall_percentage'] = (present_count / total_meetings_for_calc) * 100
        else:
            attendance_summary[member]['overall_percentage'] = 0.0

    # *** NEW LOGIC: Prepare table data for the template based on filtered records ***
    table_data = []
    for member in all_group_members:
        member_row = {
            'member': member,
            'statuses': [], # List of statuses aligned with the *filtered* meeting dates
            'overall_percentage': attendance_summary.get(member, {}).get('overall_percentage', 0.0)
        }
        
        # If filtered by date, we only have one date to check
        if selected_date:
             status = attendance_summary.get(member, {}).get(selected_date, 'N/A') # Default to 'N/A' if no record for this member on this date
             member_row['statuses'].append(status)
        else:
            # If not filtered, align statuses with all_meeting_dates
            for date in all_meeting_dates:
                status = attendance_summary.get(member, {}).get(date, 'N/A') # Default to 'N/A' if no record for this date
                member_row['statuses'].append(status)
        
        table_data.append(member_row)

    # Calculate summary by date (this should be based on ALL records, or the filtered ones depending on context)
    # For the summary table, it makes sense to show stats for the selected date if one is chosen
    attendance_by_date = {}
    if selected_date:
        # Only calculate for the selected date
        records_on_selected_date = filtered_attendance_records # This is already filtered
        present_count = sum(1 for r in records_on_selected_date if r.status == 'present')
        absent_count = sum(1 for r in records_on_selected_date if r.status == 'absent')
        total = present_count + absent_count
        rate = (present_count / total * 100) if total > 0 else 0.0
        attendance_by_date[selected_date] = {
            'present': present_count,
            'absent': absent_count,
            'rate': rate,
            'notes': ', '.join(set(r.notes for r in records_on_selected_date if r.notes))
        }
    else:
        # Calculate for all dates if no filter is applied
        for date in all_meeting_dates:
            records_on_date = [r for r in attendance_records if r.meeting_date == date] # Use original unfiltered records
            present_count = sum(1 for r in records_on_date if r.status == 'present')
            absent_count = sum(1 for r in records_on_date if r.status == 'absent')
            total = present_count + absent_count
            rate = (present_count / total * 100) if total > 0 else 0.0
            attendance_by_date[date] = {
                'present': present_count,
                'absent': absent_count,
                'rate': rate,
                'notes': ', '.join(set(r.notes for r in records_on_date if r.notes))
            }

    # Calculate overall summary statistics based on *filtered* records
    total_meetings = len(set(r.meeting_date for r in filtered_attendance_records)) # Count unique dates in filtered set
    total_attendance_records = len(filtered_attendance_records)
    total_present = sum(1 for r in filtered_attendance_records if r.status == 'present')
    total_absent = sum(1 for r in filtered_attendance_records if r.status == 'absent')
    average_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0.0

    # Handle export formats
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'pdf':
        # Pass the filtered records and selected date info to the PDF function
        return generate_attendance_pdf(filtered_attendance_records, cell_group, request.user, selected_date)
    elif format_type == 'excel':
        # Pass the filtered records and selected date info to the Excel function
        return generate_attendance_excel(filtered_attendance_records, cell_group, request.user, selected_date)
    elif format_type == 'csv':
        # Pass the filtered records and selected date info to the CSV function
        return generate_attendance_csv(filtered_attendance_records, cell_group, request.user, selected_date)

    # Determine the meeting dates to display in the template (filtered or all)
    display_meeting_dates = [selected_date] if selected_date else all_meeting_dates

    context = {
        'cell_group': cell_group,
        'attendance_records': attendance_records, # Original set for other purposes if needed
        'filtered_attendance_records': filtered_attendance_records, # The records used for calculations
        'all_meeting_dates': all_meeting_dates, # All possible dates for the filter dropdown
        'selected_date': selected_date, # The date currently being filtered on
        'display_meeting_dates': display_meeting_dates, # Dates to show in the table header
        'table_data': table_data, # Pass the pre-formatted data
        'attendance_by_date': attendance_by_date, # Summary by date
        'total_meetings': total_meetings,
        'total_present': total_present,
        'total_absent': total_absent,
        'average_attendance_rate': average_attendance_rate,
    }
    
    return render(request, 'reports/attendance_report.html', context)

# @login_required(login_url='login')
# def attendance_report_view(request, cell_group_id):
#     """Generate attendance report for a specific cell group."""
#     cell_group = get_object_or_404(CellGroup, id=cell_group_id)
    
#     # Permission check: Only allow access if user is admin, the cell group leader, or the zone leader of the cell group's zone
#     if not (
#         request.user.is_admin() or
#         (request.user.is_cell_leader() and request.user.assigned_cell_group == cell_group) or
#         (request.user.is_zone_leader() and request.user.zone_name == cell_group.zone_name)
#     ):
#         messages.error(request, 'You do not have permission to view this attendance report.')
#         return redirect('dashboard:dashboard') # Redirect to dashboard or appropriate page

#     # Get all attendance records for the cell group, ordered by meeting date
#     attendance_records = AttendanceRecord.objects.filter(
#         cell_group=cell_group
#     ).order_by('meeting_date')

#     # Get all unique meeting dates
#     meeting_dates = sorted(set(record.meeting_date for record in attendance_records))

#     # Get all members in the cell group who were active at the time of the meeting
#     # Note: This is a simplified approach. You might need to adjust based on how you track membership over time.
#     # For now, we'll get all members who have ever been in this cell group and are currently active.
#     all_group_members = Member.objects.filter(cell_group=cell_group, member_status=Member.ACTIVE).order_by('last_name', 'first_name')

#     # Prepare attendance summary data: {member_instance: {date: 'present'/'absent'}}
#     attendance_summary = defaultdict(dict)
#     for record in attendance_records:
#         attendance_summary[record.member][record.meeting_date] = record.status

#     # Calculate overall percentage for each member
#     for member, date_statuses in attendance_summary.items():
#         present_count = sum(1 for status in date_statuses.values() if status == 'present')
#         total_meetings = len(date_statuses)
#         if total_meetings > 0:
#             attendance_summary[member]['overall_percentage'] = (present_count / total_meetings) * 100
#         else:
#             attendance_summary[member]['overall_percentage'] = 0.0

#     # Calculate summary by date
#     attendance_by_date = {}
#     for date in meeting_dates:
#         records_on_date = [r for r in attendance_records if r.meeting_date == date]
#         present_count = sum(1 for r in records_on_date if r.status == 'present')
#         absent_count = sum(1 for r in records_on_date if r.status == 'absent')
#         total = present_count + absent_count
#         rate = (present_count / total * 100) if total > 0 else 0.0
#         attendance_by_date[date] = {
#             'present': present_count,
#             'absent': absent_count,
#             'rate': rate,
#             'notes': ', '.join(set(r.notes for r in records_on_date if r.notes)) # Example: combine notes
#         }

#     # Calculate overall summary statistics
#     total_meetings = len(meeting_dates)
#     total_attendance_records = len(attendance_records)
#     total_present = sum(1 for r in attendance_records if r.status == 'present')
#     total_absent = sum(1 for r in attendance_records if r.status == 'absent')
#     average_attendance_rate = (total_present / total_attendance_records * 100) if total_attendance_records > 0 else 0.0

#     # Handle export formats
#     format_type = request.GET.get('format', 'html')
    
#     if format_type == 'pdf':
#         return generate_attendance_pdf(attendance_records, cell_group, request.user)
#     elif format_type == 'excel':
#         return generate_attendance_excel(attendance_records, cell_group, request.user)
#     elif format_type == 'csv':
#         return generate_attendance_csv(attendance_records, cell_group, request.user)

#     context = {
#         'cell_group': cell_group,
#         'attendance_records': attendance_records,
#         'meeting_dates': meeting_dates,
#         'all_group_members': all_group_members,
#         'attendance_summary': dict(attendance_summary), # Convert defaultdict to regular dict for template
#         'attendance_by_date': attendance_by_date,
#         'total_meetings': total_meetings,
#         'total_present': total_present,
#         'total_absent': total_absent,
#         'average_attendance_rate': average_attendance_rate,
#     }
    
#     return render(request, 'reports/attendance_report.html', context)


# PDF Generation Functions

def generate_member_pdf(members, user):
    """Generate member list PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=TA_CENTER  # Now this works with correct import
    )
    elements.append(Paragraph('CHURCH MEMBER REPORT', title_style))
    elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data
    data = [[
        'Name', 'Phone', 'Email', 'Cell Group', 
        'Baptized', 'Married', 'Date Joined'
    ]]
    
    for member in members:
        # Handle potential missing fields
        full_name = f"{member.first_name} {member.last_name}" if hasattr(member, 'first_name') else str(member)
        phone = getattr(member, 'phone_number', 'N/A')
        email = getattr(member, 'email', 'N/A')
        cell_group = member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else 'N/A'
        is_baptized = 'Yes' if getattr(member, 'is_baptized', False) else 'No'
        is_married = 'Yes' if getattr(member, 'is_married', False) else 'No'
        date_joined = member.date_joined_church.strftime('%m/%d/%Y') if hasattr(member, 'date_joined_church') and member.date_joined_church else 'N/A'
        
        data.append([
            full_name, phone, email, cell_group, 
            is_baptized, is_married, date_joined
        ])
    
    # Create table
    table = Table(data, colWidths=[1.8*inch, 1*inch, 1.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.9*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    log_activity(user, 'export', 'member', 'Exported members to PDF')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'member_report_{date.today()}.pdf',
        content_type='application/pdf'
    )


def generate_member_excel(members, user):
    """Generate member list Excel file."""
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Members'
    
    # Headers
    headers = [
        'First Name', 'Last Name', 'Date of Birth', 'Gender',
        'Phone', 'Email', 'Cell Group', 'Date Joined',
        'Baptized', 'Baptism Cert', 'Married', 'Spouse Name'
    ]
    
    worksheet.append(headers)
    
    # Style header row
    header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Add data
    for member in members:
        worksheet.append([
            member.first_name,
            member.last_name,
            member.date_of_birth if hasattr(member, 'date_of_birth') else '',
            member.get_gender_display() if hasattr(member, 'get_gender_display') else member.gender,
            member.phone_number,
            member.email,
            member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else '',
            member.date_joined_church if hasattr(member, 'date_joined_church') else '',
            'Yes' if member.is_baptized else 'No',
            member.baptism_certificate_number or '',
            'Yes' if member.is_married else 'No',
            member.spouse_name or '',
        ])
    
    # Adjust column widths
    for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']:
        worksheet.column_dimensions[col].width = 15
    
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    log_activity(user, 'export', 'member', 'Exported members to Excel')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'member_report_{date.today()}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def generate_member_csv(members, user):
    """Generate member list CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="member_report_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'First Name', 'Last Name', 'Date of Birth', 'Gender',
        'Phone', 'Email', 'Cell Group', 'Date Joined',
        'Baptized', 'Baptism Cert', 'Married', 'Spouse Name'
    ])
    
    for member in members:
        writer.writerow([
            member.first_name,
            member.last_name,
            member.date_of_birth if hasattr(member, 'date_of_birth') else '',
            member.get_gender_display() if hasattr(member, 'get_gender_display') else member.gender,
            member.phone_number,
            member.email,
            member.cell_group.name if hasattr(member, 'cell_group') and member.cell_group else '',
            member.date_joined_church if hasattr(member, 'date_joined_church') else '',
            'Yes' if member.is_baptized else 'No',
            member.baptism_certificate_number or '',
            'Yes' if member.is_married else 'No',
            member.spouse_name or '',
        ])
    
    log_activity(user, 'export', 'member', 'Exported members to CSV')
    return response


# Cell Group Report Functions

def generate_cell_group_pdf(cell_groups, user):
    """Generate cell group PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('CELL GROUP REPORT', title_style))
    elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    data = [['Cell Group', 'Location', 'Leader', 'Member Count']]
    
    for group in cell_groups:
        data.append([
            group.name,
            group.location,
            group.leader.get_full_name() if group.leader else 'N/A',
            str(group.member_count),
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    log_activity(user, 'export', 'cell_group', 'Exported cell groups to PDF')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'cell_group_report_{date.today()}.pdf',
        content_type='application/pdf'
    )


def generate_cell_group_excel(cell_groups, user):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Cell Groups'
    
    headers = ['Cell Group', 'Location', 'Leader', 'Member Count']
    worksheet.append(headers)
    
    # Style header
    header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    for group in cell_groups:
        worksheet.append([
            group.name,
            group.location,
            group.leader.get_full_name() if group.leader else 'N/A',
            group.member_count,
        ])
    
    # Adjust column widths
    worksheet.column_dimensions['A'].width = 20
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 20
    worksheet.column_dimensions['D'].width = 15
    
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    log_activity(user, 'export', 'cell_group', 'Exported cell groups to Excel')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'cell_group_report_{date.today()}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def generate_cell_group_csv(cell_groups, user):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="cell_group_report_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Cell Group', 'Location', 'Leader', 'Member Count'])
    
    for group in cell_groups:
        writer.writerow([
            group.name,
            group.location,
            group.leader.get_full_name() if group.leader else 'N/A',
            group.member_count
        ])
    
    log_activity(user, 'export', 'cell_group', 'Exported cell groups to CSV')
    return response


# Baptism Report Functions

def generate_baptism_pdf(members, user):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('BAPTISM REPORT', title_style))
    elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    data = [['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number']]
    
    for member in members:
        data.append([
            f"{member.first_name} {member.last_name}",
            member.phone_number,
            member.email,
            str(member.baptism_date) if hasattr(member, 'baptism_date') and member.baptism_date else 'N/A',
            member.baptism_certificate_number or 'N/A',
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    log_activity(user, 'export', 'baptism', 'Exported baptism report to PDF')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'baptism_report_{date.today()}.pdf',
        content_type='application/pdf'
    )


def generate_baptism_excel(members, user):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Baptized Members'
    
    headers = ['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number']
    worksheet.append(headers)
    
    header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    for member in members:
        worksheet.append([
            f"{member.first_name} {member.last_name}",
            member.phone_number,
            member.email,
            member.baptism_date if hasattr(member, 'baptism_date') else '',
            member.baptism_certificate_number or '',
        ])
    
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    log_activity(user, 'export', 'baptism', 'Exported baptism report to Excel')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'baptism_report_{date.today()}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def generate_baptism_csv(members, user):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="baptism_report_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Baptism Date', 'Certificate Number'])
    
    for member in members:
        writer.writerow([
            f"{member.first_name} {member.last_name}",
            member.phone_number,
            member.email,
            member.baptism_date if hasattr(member, 'baptism_date') else '',
            member.baptism_certificate_number or '',
        ])
    
    log_activity(user, 'export', 'baptism', 'Exported baptism report to CSV')
    return response


# Marriage Report Functions

def generate_marriage_pdf(members, user):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('MARRIAGE REPORT', title_style))
    elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    data = [['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number']]
    
    for member in members:
        data.append([
            f"{member.first_name} {member.last_name}",
            member.spouse_name or 'N/A',
            member.phone_number,
            str(member.marriage_date) if hasattr(member, 'marriage_date') and member.marriage_date else 'N/A',
            member.marriage_certificate_number or 'N/A',
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    log_activity(user, 'export', 'marriage', 'Exported marriage report to PDF')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'marriage_report_{date.today()}.pdf',
        content_type='application/pdf'
    )


def generate_marriage_excel(members, user):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Married Members'
    
    headers = ['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number']
    worksheet.append(headers)
    
    header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    for member in members:
        worksheet.append([
            f"{member.first_name} {member.last_name}",
            member.spouse_name or '',
            member.phone_number,
            member.marriage_date if hasattr(member, 'marriage_date') else '',
            member.marriage_certificate_number or '',
        ])
    
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    log_activity(user, 'export', 'marriage', 'Exported marriage report to Excel')
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'marriage_report_{date.today()}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def generate_marriage_csv(members, user):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="marriage_report_{date.today()}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Spouse', 'Phone', 'Marriage Date', 'Certificate Number'])
    
    for member in members:
        writer.writerow([
            f"{member.first_name} {member.last_name}",
            member.spouse_name or '',
            member.phone_number,
            member.marriage_date if hasattr(member, 'marriage_date') else '',
            member.marriage_certificate_number or '',
        ])
    
    log_activity(user, 'export', 'marriage', 'Exported marriage report to CSV')
    return response


# Attendance Report Functions
def generate_attendance_pdf(attendance_records, cell_group, user, selected_date=None):
    """Generate attendance PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        alignment=TA_CENTER
    )
    
    # Add date info to title if filtered
    title_text = f'ATTENDANCE REPORT - {cell_group.name}'
    if selected_date:
        title_text += f' (Meeting Date: {selected_date.strftime("%Y-%m-%d")})'
        
    elements.append(Paragraph(title_text, title_style))
    elements.append(Paragraph(f'Generated on: {date.today().strftime("%B %d, %Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary table
    summary_data = [['Total Records', 'Total Present', 'Total Absent', 'Rate (%)']]
    total_records = attendance_records.count()
    total_present = attendance_records.filter(status='present').count()
    total_absent = attendance_records.filter(status='absent').count()
    avg_rate = (total_present / total_records * 100) if total_records > 0 else 0.0
    
    summary_data.append([
        str(total_records),
        str(total_present),
        str(total_absent),
        f"{avg_rate:.2f}"
    ])
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))

    # Detailed attendance table
    data = [['Date', 'Member', 'Status', 'Notes']]
    for record in attendance_records:
        data.append([
            record.meeting_date.strftime('%Y-%m-%d'),
            f"{record.member.first_name} {record.member.last_name}",
            record.get_status_display(),  # Assuming you have a get_status_display method
            record.notes or ''
        ])
    
    detailed_table = Table(data)
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(detailed_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    # Log message including date filter info
    log_msg = f'Exported attendance report for {cell_group.name} to PDF'
    if selected_date:
        log_msg += f' (Meeting Date: {selected_date})'
    log_activity(user, 'export', 'attendance', log_msg)
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'attendance_report_{cell_group.name}_{selected_date.strftime("%Y%m%d") if selected_date else "all_dates"}_{date.today()}.pdf',
        content_type='application/pdf'
    )


def generate_attendance_excel(attendance_records, cell_group, user, selected_date=None):
    """Generate attendance Excel report"""
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    # Include date in sheet name if filtered
    worksheet_title = f'Attendance - {cell_group.name}'
    if selected_date:
        worksheet_title += f' ({selected_date.strftime("%Y-%m-%d")})'
    worksheet.title = worksheet_title
    
    headers = ['Date', 'Member', 'Status', 'Notes']
    worksheet.append(headers)
    
    # Style header
    header_fill = PatternFill(start_color='1f4788', end_color='1f4788', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    for record in attendance_records:
        worksheet.append([
            record.meeting_date,
            f"{record.member.first_name} {record.member.last_name}",
            record.get_status_display(),  # Assuming you have a get_status_display method
            record.notes or ''
        ])
    
    # Adjust column widths
    worksheet.column_dimensions['A'].width = 15
    worksheet.column_dimensions['B'].width = 25
    worksheet.column_dimensions['C'].width = 12
    worksheet.column_dimensions['D'].width = 30
    
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    # Log message including date filter info
    log_msg = f'Exported attendance report for {cell_group.name} to Excel'
    if selected_date:
        log_msg += f' (Meeting Date: {selected_date})'
    log_activity(user, 'export', 'attendance', log_msg)
    
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'attendance_report_{cell_group.name}_{selected_date.strftime("%Y%m%d") if selected_date else "all_dates"}_{date.today()}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


def generate_attendance_csv(attendance_records, cell_group, user, selected_date=None):
    """Generate attendance CSV report"""
    response = HttpResponse(content_type='text/csv')
    # Include date in filename if filtered
    filename = f'attendance_report_{cell_group.name}_'
    if selected_date:
        filename += f'{selected_date.strftime("%Y%m%d")}_'
    filename += f'{date.today()}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Member', 'Status', 'Notes'])
    
    for record in attendance_records:
        writer.writerow([
            record.meeting_date,
            f"{record.member.first_name} {record.member.last_name}",
            record.get_status_display(),  # Assuming you have a get_status_display method
            record.notes or ''
        ])
    
    # Log message including date filter info
    log_msg = f'Exported attendance report for {cell_group.name} to CSV'
    if selected_date:
        log_msg += f' (Meeting Date: {selected_date})'
    log_activity(user, 'export', 'attendance', log_msg)
    return response


@login_required(login_url='login')
def zone_report_view(request):
    """Generate a zone-level report for zone leaders."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'Only zone leaders and administrators can access zone reports.')
        return redirect('reports:reports')

    if request.user.is_zone_leader() and request.user.zone_name:
        cell_groups = CellGroup.objects.filter(is_active=True, zone_name=request.user.zone_name)
        members = Member.objects.filter(cell_group__in=cell_groups)
        zone_name = request.user.zone_name
    else:
        cell_groups = CellGroup.objects.filter(is_active=True)
        members = Member.objects.active()
        zone_name = 'All Zones'

    context = {
        'zone_name': zone_name,
        'cell_groups': cell_groups,
        'members': members,
        'active_members': members.filter(member_status=Member.ACTIVE).count(),
        'inactive_members': members.filter(member_status__in=[Member.LEFT, Member.DECEASED]).count(),
        'follow_up_required': members.filter(
            member_status=Member.ACTIVE,
            phone_number__in=['', None],
        ).count(),
    }
    return render(request, 'reports/zone_report.html', context)


@login_required(login_url='login')
def growth_report_view(request):
    """Generate growth report."""
    if not (request.user.is_admin() or request.user.is_zone_leader()):
        messages.error(request, 'Only administrators and zone leaders can access growth reports.')
        return redirect('reports:reports')
    
    # Get last 12 months of data
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    monthly_growth = []
    current_date = start_date
    
    from apps.members.models import Member
    members = Member.objects.active()
    if request.user.is_zone_leader() and request.user.zone_name:
        members = members.filter(cell_group__zone_name=request.user.zone_name)
    
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)
        
        new_members = members.filter(
            date_joined_church__gte=month_start,
            date_joined_church__lt=next_month
        ).count()
        
        monthly_growth.append({
            'month': month_start.strftime('%B %Y'),
            'new_members': new_members,
        })
        
        current_date = next_month
    
    format_type = request.GET.get('format', 'html')
    
    if format_type == 'excel':
        # Create Excel export
        import openpyxl
        from django.http import FileResponse
        import io
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Growth Report'
        
        worksheet.append(['Month', 'New Members'])
        for data in monthly_growth:
            worksheet.append([data['month'], data['new_members']])
        
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='growth_report.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif format_type == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="growth_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Month', 'New Members'])
        for data in monthly_growth:
            writer.writerow([data['month'], data['new_members']])
        
        return response
    
    context = {
        'monthly_growth': monthly_growth,
        'total_new_members': sum(item['new_members'] for item in monthly_growth),
    }
    
    return render(request, 'reports/growth_report.html', context)