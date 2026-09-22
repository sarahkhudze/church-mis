# from django.urls import path
# from . import views

# app_name = 'accounts'

# urlpatterns = [
#     # Authentication URLs
#     path('register/', views.RegisterView.as_view(), name='register'),
#     path('login/', views.LoginView.as_view(), name='login'),
#     path('logout/', views.logout_view, name='logout'),
    
#     # Profile URLs
#     path('profile/', views.profile_view, name='profile'),
#     path('profile/edit/', views.profile_edit_view, name='profile_edit'),
#     path('profile/change-password/', views.change_password_view, name='change_password'),
    
#     # User Management (Admin only)
#     path('management/', views.user_management_view, name='user_management'),
#     path('management/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
#     path('management/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
#     path('management/<int:pk>/deactivate/', views.user_deactivate_view, name='user_deactivate'),
#     path('management/<int:pk>/activate/', views.user_activate_view, name='user_activate'),
# ]

# from django.urls import path
# from . import views

# app_name = 'accounts'

# urlpatterns = [
#     path('register/', views.RegisterView.as_view(), name='register'),
#     path('login/', views.LoginView.as_view(), name='login'),
#     path('logout/', views.logout_view, name='logout'),
#     path('profile/', views.profile_view, name='profile'),
#     path('profile/edit/', views.profile_edit_view, name='profile_edit'),
#     path('change-password/', views.change_password_view, name='change_password'),
    
#     # Admin user management
#     path('users/', views.user_management_view, name='user_management'),
#     path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
#     path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
#     path('users/<int:pk>/deactivate/', views.user_deactivate_view, name='user_deactivate'),
#     path('users/<int:pk>/activate/', views.user_activate_view, name='user_activate'),
    
#     # Approval URLs
#     path('pending-approvals/', views.pending_approvals_view, name='pending_approvals'),
#     path('approve-user/<int:pk>/', views.approve_user_view, name='approve_user'),
#     path('reject-user/<int:pk>/', views.reject_user_view, name='reject_user'),
# ]


from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Admin user management
    path('users/', views.user_management_view, name='user_management'),
    path('users/create/', views.admin_create_user_view, name='admin_create_user'),  # ADD THIS LINE
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('users/<int:pk>/deactivate/', views.user_deactivate_view, name='user_deactivate'),
    path('users/<int:pk>/activate/', views.user_activate_view, name='user_activate'),
    
    # Approval URLs
    path('pending-approvals/', views.pending_approvals_view, name='pending_approvals'),
    path('approve-user/<int:pk>/', views.approve_user_view, name='approve_user'),
    path('reject-user/<int:pk>/', views.reject_user_view, name='reject_user'),
    path('zones/', views.zone_management_view, name='zone_management'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email.html',
        success_url='/accounts/password_reset/done/',
        from_email='noreply@churchcms.com' # Change this to your actual email
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]