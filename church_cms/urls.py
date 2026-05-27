"""
URL configuration for church_cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
Examples:
Function views
    1. Add an import:  from . import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app import views
    2. Add a URL to urlpatterns:  path('', views.Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home/Dashboard
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Authentication & User Management
    path('accounts/', include('apps.accounts.urls')),
    
    # Members & Cell Groups
    path('members/', include('apps.members.urls')),
    path('cell-groups/', include('apps.cell_groups.urls')),
    
    # Reports
    path('reports/', include('apps.reports.urls')),
    
    # Notifications
    path('notifications/', include('apps.notifications.urls')),
    
    # Activity Logs
    path('activity-logs/', include('apps.activity_logs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
