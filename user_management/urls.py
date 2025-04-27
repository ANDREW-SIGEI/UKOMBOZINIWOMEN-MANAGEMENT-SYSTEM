from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # Member URLs
    path('members/', views.member_list, name='member_list'),
    path('members/create/', views.member_create, name='member_create'),
    path('members/<int:member_id>/', views.member_detail, name='member_detail'),
    path('members/<int:member_id>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:member_id>/delete/', views.member_delete, name='member_delete'),
    
    # Group URLs
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('groups/<int:group_id>/add-member/', views.group_add_member, name='group_add_member'),
    path('groups/<int:group_id>/bulk-add-members/', views.group_bulk_add_members, name='group_bulk_add_members'),
    path('groups/<int:group_id>/remove-member/<int:membership_id>/', views.group_remove_member, name='group_remove_member'),
    
    # Field Officer Report URLs
    path('field-officers/daily-report/', views.field_officer_daily_report, name='field_officer_daily_report'),
    path('field-officers/monthly-report/', views.field_officer_monthly_report, name='field_officer_monthly_report'),
    path('field-officers/report-success/', views.field_officer_report_success, name='field_officer_report_success'),
    path('field-officers/report-table/', views.field_officer_report_table, name='field_officer_report_table'),
    
    # Offline sync endpoint
    path('field-officers/sync-form/', views.sync_offline_report, name='sync_offline_report'),
] 