from django.urls import path
from apps.members import views

app_name = 'cell_groups'

urlpatterns = [
    path('', views.cell_group_list_view, name='cell_group_list'),
    path('create/', views.cell_group_create_view, name='cell_group_create'),
    path('<int:pk>/', views.cell_group_detail_view, name='cell_group_detail'),
    path('<int:pk>/edit/', views.cell_group_edit_view, name='cell_group_edit'),
]
