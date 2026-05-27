# Church Management System (CMS)

A comprehensive web-based Church Management System built with Django for **Charismatic Redeemed Ministries International**. The system helps churches digitally manage members, organize cell groups, track spiritual records, and simplify administrative operations.

## Features

### Core Features
- ✅ Digital member registration and management
- ✅ Cell group organization and management
- ✅ Spiritual milestones tracking (baptism, marriage)
- ✅ Role-based access control (Admin, Cell Leaders, Viewers)
- ✅ Advanced search and filtering capabilities
- ✅ Comprehensive reporting (PDF, Excel, CSV)
- ✅ Activity logging and audit trails
- ✅ Statistics and analytics dashboard

### User Roles

#### Church Administrator
- Full system access
- Manage all members across all cell groups
- Create and assign cell groups
- Manage user accounts
- Generate comprehensive reports
- Monitor church statistics
- Access activity logs

#### Cell Group Leader
- Manage members in their assigned cell group
- Add new members to their group
- Edit member details within their group
- Search members within their group
- Generate group-specific reports
- View group statistics

#### Viewer (Optional)
- Read-only access to assigned data

## Technology Stack

- **Backend**: Django 4.2.13
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Additional Libraries**:
  - Django REST Framework
  - Django Crispy Forms
  - ReportLab (PDF generation)
  - OpenPyXL (Excel generation)
  - Pandas (Data analysis)

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual Environment (recommended)

### Step 1: Clone/Extract Project
```bash
cd church_management_system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Update DEBUG, SECRET_KEY, DATABASE settings, etc.
```

### Step 5: Database Migration
```bash
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

### Step 8: Access Admin Panel
Visit `http://localhost:8000/admin/` with your superuser credentials to manage users, members, and cell groups.

## Project Structure

```
church_management_system/
├── manage.py
├── requirements.txt
├── .env.example
├── church_cms/              # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/            # User authentication & management
│   │   ├── models.py        # CustomUser model
│   │   ├── views.py         # Auth views, user management
│   │   ├── forms.py         # Auth forms
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── members/             # Member & cell group management
│   │   ├── models.py        # Member, CellGroup models
│   │   ├── views.py         # Member CRUD operations
│   │   ├── forms.py         # Member forms
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── cell_groups/         # Cell group views
│   ├── dashboard/           # Dashboard & statistics
│   ├── reports/             # Report generation
│   ├── notifications/       # Notification system
│   └── activity_logs/       # Activity audit trail
│
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploads
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── accounts/
│   ├── members/
│   ├── dashboard/
│   └── reports/
└── db.sqlite3              # Development database
```

## Key Models

### CustomUser
- Extends Django's User model
- Fields: role, phone_number, assigned_cell_group
- Roles: Admin, Cell Leader, Viewer

### Member
- Full name, date of birth, gender
- Contact information (phone, email, address)
- Church information (cell group, date joined)
- Baptism details (status, certificate, date)
- Marriage details (status, spouse, certificate, date)
- Created by (tracking who added the member)

### CellGroup
- Name, location, description
- Assigned leader
- Auto-calculated member count

### ActivityLog
- Tracks all user actions
- Stores: user, action, entity type, description, IP address, timestamp
- Read-only in admin

## User Workflows

### For Cell Group Leaders
1. Login with credentials
2. View dashboard showing group statistics
3. Add new members to their group
4. Edit member information
5. Generate group-specific reports
6. View member search results

### For Administrators
1. Login with admin credentials
2. View comprehensive dashboard with all statistics
3. Manage cell groups (create, assign leaders)
4. Manage users (create, edit, deactivate)
5. Generate comprehensive reports
6. View activity logs
7. Access system settings

## Features in Detail

### Member Management
- **Search**: Search by name, email, phone number
- **Filter**: By gender, baptized status, marital status, age, cell group
- **Bulk Actions**: Transfer members, mark baptized/married, activate/deactivate
- **Conditional Fields**: Baptism certificate required if baptized, marriage certificate required if married

### Reporting
- **Report Types**: Members, Cell Groups, Baptisms, Marriages, Youth Statistics
- **Export Formats**: PDF, Excel, CSV
- **Date Filtering**: Date ranges for membership reports
- **Group-Specific Reports**: Leaders can only report on their group

### Dashboard
- **Admin Dashboard**: System-wide statistics, trends, recent activities
- **Leader Dashboard**: Group-specific statistics, member list, birthdays
- **Statistics**: Gender distribution, age groups, baptism/marriage percentages

### Security
- Django's built-in CSRF protection
- Session-based authentication
- Role-based authorization
- Password hashing (PBKDF2)
- Activity logging for audit trails
- Secure password change functionality

## Database Fields Reference

### Member Model
```
Personal Information:
- first_name, last_name
- date_of_birth
- gender (M/F)
- phone_number, email
- residential_address
- occupation (optional)

Church Information:
- cell_group (FK)
- date_joined_church
- is_baptized, baptism_certificate_number, baptism_date
- is_married, marriage_certificate_number, marriage_date, spouse_name

System Fields:
- created_by (FK to User)
- created_at, updated_at
- is_active
- notes
```

## Admin Panel Features

- User creation and management
- Member CRUD operations
- Cell group administration
- Activity log viewing
- Batch operations through Django admin interface

## API Capabilities (Future Enhancement)

The system is built with REST framework integration for:
- Member API endpoints
- Cell group API endpoints
- Report API endpoints
- User management API

## Configuration Options

### Email Setup
Update `church_cms/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Database Setup for Production
Update `church_cms/settings.py` or `.env`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'church_cms',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Deployment Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Update `SECRET_KEY` to a strong value
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Configure email settings
- [ ] Set up PostgreSQL database
- [ ] Create superuser
- [ ] Run `collectstatic` for static files
- [ ] Set up SSL/HTTPS
- [ ] Configure web server (Gunicorn, Nginx)

## Troubleshooting

### Migration Issues
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Database Errors
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Future Enhancements

- [ ] SMS notifications (Twilio integration)
- [ ] Email notifications
- [ ] Birthday reminders
- [ ] Anniversary reminders
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Member photos
- [ ] Family relationship tracking
- [ ] Attendance tracking
- [ ] Tithe/offering tracking
- [ ] Event management
- [ ] Prayer request tracking

## Security Considerations

1. Always use strong passwords
2. Keep dependencies updated
3. Use HTTPS in production
4. Regularly backup database
5. Monitor activity logs
6. Limit admin access
7. Use environment variables for sensitive data
8. Implement regular security audits

## Support & Documentation

For detailed documentation on:
- User management: See `apps/accounts/` module
- Member management: See `apps/members/` module
- Reports: See `apps/reports/` module
- Dashboard: See `apps/dashboard/` module

## License

© 2026 Charismatic Redeemed Ministries International. All rights reserved.

## Contact

For support and inquiries, please contact the system administrator.

---

**Last Updated**: May 27, 2026
**Version**: 1.0.0
**Status**: Production Ready
