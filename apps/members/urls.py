from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    # Member URLs
    path('', views.member_list_view, name='member_list'),
    path('create/', views.member_create_view, name='member_create'),
    path('<int:pk>/', views.member_detail_view, name='member_detail'),
    path('<int:pk>/edit/', views.member_edit_view, name='member_edit'),
    path('<int:pk>/delete/', views.member_delete_view, name='member_delete'),
    
    # Bulk Actions
    path('bulk-action/', views.bulk_member_action_view, name='bulk_action'),
    
    # Cell Group URLs
    path('groups/', views.cell_group_list_view, name='cell_group_list'),
    path('groups/create/', views.cell_group_create_view, name='cell_group_create'),
    path('groups/<int:pk>/', views.cell_group_detail_view, name='cell_group_detail'),
    path('groups/<int:cell_group_id>/attendance/', views.record_attendance_view, name='record_attendance'),
    path('groups/<int:pk>/edit/', views.cell_group_edit_view, name='cell_group_edit'),
    path('groups/<int:pk>/approve/', views.cell_group_approve_view, name='cell_group_approve'),
    path('groups/<int:pk>/reject/', views.cell_group_reject_view, name='cell_group_reject'),
]
