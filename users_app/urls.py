from django.urls import path
from users_app import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('add-user/', views.adduser, name = 'adduser'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name = 'password_change_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name = 'password_change'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name = 'password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name = 'password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"), name = 'password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name = 'password_reset_complete'),
    path('logged-in/', views.logged_in, name='logged_in'), 
    path('view-users/', views.view_users, name='view_users'),  
    path('edit-user/<user_id>', views.edit_user, name='edit_user'),
    path('view-dashboard/', views.viewDashboards, name='view_dashboards'),
    path('add-dashboard/', views.addDashboard, name='add_dashboard'), 
    path('edit-dashboard/<dashboard_id>', views.editDashboard, name='edit_dashboard'), 
    path('administration/', views.adminView, name='admin_dashboard'),  
    path('delete/access/<access_id>', views.deleteDashboardAccess, name='delete_access'),   
    path('delete/dashboard/<dashboard_id>', views.deleteDashboard, name='delete_dashboard'),  
    path('delete/user/<user_id>', views.deleteUser, name='delete_user'),  
    path('add-access/', views.addDashboardAccess, name='create_access'),

    path('add-presentation/', views.addPresentation, name='add_presentation'), 
    path('edit-presentation/<candidatepresentation_id>', views.editPresentation, name='edit_presentation'),
    path('delete/presentation/<presentation_id>', views.deletePresentation, name='delete_presentation'), 
    path('view-presentation/', views.viewPresentations, name='view_presentations'), 
    path('add-company/', views.addcompany, name = 'addcompany'),
    path('view-companies/', views.view_companies, name='view_companies'),  
    path('edit-company/<company_id>', views.edit_company, name='edit_company'),
    path('delete/company/<company_id>', views.deleteCompany, name='delete_company'),
    path('add-presentationaccess/', views.addPresentationAccess, name='create_presentationaccess'),  
    path('delete/presentationaccess/<access_id>', views.deletePresentationAccess, name='delete_presentationaccess'),   

]
