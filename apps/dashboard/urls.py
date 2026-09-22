from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('statistics/', views.statistics_view, name='statistics'),
    
    # ADD THIS: Executive Dashboard for Viewers
    path('executive/', views.executive_dashboard_view, name='executive_dashboard'),
]
