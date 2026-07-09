from django.urls import path

from . import views

app_name = 'zones'

urlpatterns = [
    path('', views.zone_list, name='zone_list'),
    path('create/', views.zone_create, name='zone_create'),
    path('api/overview/', views.zone_overview_api, name='zone_overview_api'),
    path('<int:pk>/', views.zone_detail, name='zone_detail'),
    path('<int:pk>/edit/', views.zone_edit, name='zone_edit'),
    path('<int:pk>/delete/', views.zone_delete, name='zone_delete'),
]
