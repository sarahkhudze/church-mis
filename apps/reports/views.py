from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from datetime import date
import csv
import io

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

from apps.members.models import Member  # Fixed: Removed CellGroup from here
from apps.cell_groups.models import CellGroup  # Fixed: Added import from correct location
from apps.accounts.models import CustomUser
from apps.accounts.utils import log_activity, admin_required, get_user_members

@login_required(login_url='login')
def reports_view(request):
    """Reports menu view."""
    context = {
        'is_admin': request.user.is_admin(),
        'is_cell_leader': request.user.is_cell_leader(),
    }
    return render(request, 'reports/reports_menu.html', context)


@login_required(login_url='login')
def member_report_view(request):
    """Generate member report."""
    members = get_user_members(request.user)
    
    # Filter by cell group for leaders
    if request.user.is_cell_leader():
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
    if request.user.is_cell_leader():
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

@login_required(login_url='login')
def growth_report_view(request):
    """Generate growth report."""
    if not request.user.is_admin():
        messages.error(request, 'Only administrators can access growth reports.')
        return redirect('reports:reports')
    
    # Get last 12 months of data
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    monthly_growth = []
    current_date = start_date
    
    from apps.members.models import Member
    
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            next_month = current_date.replace(month=current_date.month + 1, day=1)
        
        new_members = Member.objects.filter(
            date_joined_church__gte=month_start,
            date_joined_church__lt=next_month,
            is_active=True
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