# from django.urls import path
# from . import views

# app_name = 'reports'

# urlpatterns = [
#     path('', views.reports_view, name='reports'),
#     path('members/', views.member_report_view, name='member_report'),
#     path('cell-groups/', views.cell_group_report_view, name='cell_group_report'),
#     path('baptisms/', views.baptism_report_view, name='baptism_report'),
#     path('marriages/', views.marriage_report_view, name='marriage_report'),
# ]

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_view, name='reports'),
    path('member/', views.member_report_view, name='member_report'),
    path('cell-group/', views.cell_group_report_view, name='cell_group_report'),
    path('baptism/', views.baptism_report_view, name='baptism_report'),
    path('marriage/', views.marriage_report_view, name='marriage_report'),
    path('growth/', views.growth_report_view, name='growth_report'),  # Add this line
]